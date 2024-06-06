# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2019, Toshio Kuratomi
"""
Setup an application context to save global data which is set on program start.

There is some application data which is set on application startup and then never modified.
These values are *almost* constants and should be eligible to be global variables.  However,
global variables make testing hard (as the test has to monkeypatch constants) and the use of
globals prevents re-using the functionality as a library.

Enter contexts.  Contexts can be used to set global values.  But the context can be swapped out if
the program needs to use a different set of globals and some location for some reason.  This file
contains the context framework itself.

For Python3.6 compatibility, this file needs to be loaded early, before any event loops are created.
This is due to limitations in the backport of the contextvars library to Python3.6.  For code which
targets Python3.7 and above, there is no such limitation.

.. warning:: This is not a stable interface.

    The API has quite a few rough edges that need to be ironed out before this is finished.  Some of
    this code and data will be moved into an antibull.context module which can deal with the generic
    side of things while this module will only contain the things that are particular to specfic
    applications.

Setup
=====

Importing antsibull_core.app_context will setup a default context with default values for the
library to use.  The application should initialize a new context with user overriding values by
calling :func:`antsibull_core.app_context.create_contexts` with command line args and
configuration data.  The data from those will be used to initialize a new ``app_ctx`` and new
``lib_ctx``.  The application can then use the context managers to utilize these contexts before
calling any further antsibull code.  An example:

.. code-block:: python

    from antsibull_core import app_context
    from antsibull_core.config import load_config


    def do_something():
        app_ctx = app_context.app_ctx.get()
        core_filename = download_python_package('ansible-core', server_url=app_ctx.pypi_url)
        return core_filename

    def run(args):
        args = parse_args(args)
        cfg = load_config(args.config_file)
        context_data = app_context.create_contexts(args=args, cfg=cfg)
        with app_context.app_and_lib_context(context_data):
            do_something()

Extending AppContext
====================

Since antsibull-core 1.2.0, applications using antsibull-core can use their own extension
of AppContext to better handle command line arguments, or handle additional configuration
values in explicitly specified configuration files.  (The implicitly specified configuration
files, ``/etc/antsibull.cfg`` and ``~/.antsibull.cfg``, cannot have extra keys to prevent
incompatibility with other antsibull-core based applications.)

For this, the application needs to create a derived class of :obj:`AppContext`, and pass
it to :func:`antsibull_core.config.load_config` when loading the configuration.  Please
note that :func:`antsibull_core.app_context.app_ctx.get` always returns the :obj:`AppContext`
view of that extended app context, so applications should create their own ``app_context``
module that provides itself a way to obtain the extended app context.  For example in
antsibull-docs this is done as follows:

.. code-block:: python

    from antsibull_core.app_context import AppContextWrapper
    from antsibull_docs.schemas.app_context import DocsAppContext

    app_ctx: AppContextWrapper[DocsAppContext] = AppContextWrapper()

In antsibull-docs, the extended app context (``DocsAppContext``) is then used as follows:

.. code-block:: python

    from antsibull_core.app_context import app_and_lib_context, create_contexts
    from antsibull_core.config import load_config

    from antsibull_docs import app_context
    from antsibull_docs.schemas.app_context import DocsAppContext


    def do_something():
        app_ctx = app_context.app_ctx.get()
        # collection_url is an option in DocsAppContext
        print(f'collection_url configuration: {app_ctx.collection_url}')

    def run(args):
        args = parse_args(args)
        cfg = load_config(args.config_file, app_context_model=DocsAppContext)
        context_data = create_contexts(args=args, cfg=cfg)
        with app_and_lib_context(context_data):
            do_something()
"""

from __future__ import annotations

import argparse
import contextvars
import typing as t
from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager, contextmanager

from .schemas.context import AppContext, LibContext
from .vendored.collections import ImmutableDict

AppContextT = t.TypeVar("AppContextT", bound=AppContext)


#: lib_ctx should be restricted to things which do not belong in the API but an application or
#: user might want to tweak.  Global, internal, incidental values are good to store here.  Things
#: that are already settable by the public API are not.  For instance, a function whose primary
#: purpose is to retrieve a file from the internet and return the filename where it was
#: downloaded to might need a number of bytes to read at a time so that the entire file contents
#: aren't in memory at one time.  The number of bytes is incidental and an internal
#: implementation detail.  However, it might be something that an end user wants to adjust
#: globally for all functions which need to chunk data.  So this is appropriate to make available
#: for tweaking via a value saved in lib_ctx.  All values in lib_ctx need to have a default value
#: so that code which uses it can fallback to something if the application or user did not
#: specify a value.
lib_ctx: contextvars.ContextVar[LibContext] = contextvars.ContextVar("lib_ctx")

#: Values in app_ctx are things that form defaults in the application.  Even though it may be
#: tempting to use them for library API, they should not be used there.  Instead, these values
#: are things that should be pat of the API calls themselves and explicitly passed from the
#: application to the library code.  If the value is used by multiple calls to the function (or
#: by calls to multiple related functions) it may be convenient to encapsulate that library code
#: into an object which can be initialized with the data.
#:
#: For instance, a function might contact a web service to retrieve information.  The URL of the
#: web service can be passed in via the API for testing against a non-production server.  The
#: user might toggle these via a config file or command line argument.  The app_ctx provides
#: a place for the application to consolidate the information from these different locations into
#: a single place and then consult them globally.  The values should be passed explicitly from
#: the application code to the library code as a function parameter.
#:
#: If the library provides several functions to retrieve different pieces of information from the
#: server, the library can provide a class which takes the server's URL as a parameter and stores
#: as an attribute and the functions can be converted into methods of the object.  Then the
#: application code can initialize the object once and thereafter call the object's methods.
app_ctx: contextvars.ContextVar[AppContext] = contextvars.ContextVar("app_ctx")


class ContextReturn(t.Generic[AppContextT]):
    """
    NamedTuple-like object for the return value of :func:`create_contexts`.

    The :func:`create_contexts` returns quite a bit of information.  This data structure organizes
    the information.

    :ivar app_ctx: Context for vars that are okay to use globally only within application code.
    :ivar lib_ctx: Context for vars which may be used globally within both library and
        application code.
    :ivar args: An :python:obj:`argparse.Namespace` containing command line arguments that were not
        used to construct the contexts
    :ivar cfg: Configuration values which were not used to construct the contexts.

    .. note:: unfortunately generic ``NamedTuple`` objects are not possible, so this is a generic
              class that tries to behave as close as possible to a named tuple. Right now it does
              not support comparisons though, if that is needed please create an issue in the
              antsibull-core repository.
    """

    app_ctx: AppContextT
    lib_ctx: LibContext
    args: argparse.Namespace
    cfg: dict

    def __init__(
        self,
        # pylint: disable-next=redefined-outer-name
        app_ctx: AppContextT,
        # pylint: disable-next=redefined-outer-name
        lib_ctx: LibContext,
        args: argparse.Namespace,
        cfg: dict,
    ):
        self.app_ctx = app_ctx
        self.lib_ctx = lib_ctx
        self.args = args
        self.cfg = cfg

    def __getitem__(self, index: int) -> t.Any:
        if index == 0:
            return self.app_ctx
        if index == 1:
            return self.lib_ctx
        if index == 2:
            return self.args
        if index == 3:
            return self.cfg
        raise IndexError("tuple index out of range")

    def __iter__(self) -> Iterable:
        return (self.app_ctx, self.lib_ctx, self.args, self.cfg).__iter__()


def _extract_context_values(
    known_fields, args: argparse.Namespace | None, cfg: Mapping = ImmutableDict()
) -> dict:
    context_values = {}
    if cfg:
        for value in known_fields:
            try:
                context_values[value] = cfg[value]
            except KeyError:
                pass

    # Args override config
    if args:
        for value in known_fields:
            try:
                context_values[value] = getattr(args, value)
            except AttributeError:
                pass

    return context_values


@t.overload
def create_contexts(
    args: argparse.Namespace | None = None,
    cfg: Mapping = ImmutableDict(),
    use_extra: bool = True,
) -> ContextReturn[AppContext]: ...


@t.overload
def create_contexts(
    args: argparse.Namespace | None = None,
    cfg: Mapping = ImmutableDict(),
    use_extra: bool = True,
    *,
    app_context_model: type[AppContextT],
) -> ContextReturn[AppContextT]: ...


def create_contexts(
    args: argparse.Namespace | None = None,
    cfg: Mapping = ImmutableDict(),
    use_extra: bool = True,
    *,
    app_context_model=AppContext,
) -> ContextReturn:
    """
    Create new contexts appropriate for setting the app and lib context.

    This function takes values from the application arguments and configuration and sets them on
    the context.  It validates, normalizes, and sets defaults for the contexts based on what is
    available in the arguments and configuration.

    :kwarg args: An :python:obj:`argparse.Namespace` holding the program's command line
        arguments.  See the warning below about working with :python:mod:`argpase`.
    :kwarg cfg: A dictionary holding the program's configuration.
    :kwarg use_extra: When True, the default, all extra arguments and config values will be set as
        fields in ``app_ctx.extra``.  When False, the extra arguments and config values will be
        returned as part of the ContextReturn.
    :kwarg app_context_model: The model to use for the app context. Must be derived from
        :obj:`AppContext`. If not provided, will use :obj:`AppContext` itself.
    :returns: A ``ContextReturn`` object.

    .. warning::
        We cannot tell whether a user set a value via the command line if :python:mod:`argparse`
        sets the field to a default value.  That means when you specify the field in the
        :obj:`AppContext` or :obj:`LibContext` models, you must tell :python:mod:`argparse` not to
        set the field to a default like this::

            parser.add_argument('--breadcrumbs', default=argparse.SUPPRESS)

        If the field is only used via the :attr:`AppContext.extra` mechanism (not explictly set),
        then you should ignore this section and use :python:mod:`argparse`'s default mechanism.
    """
    fields_in_lib_ctx = set(LibContext.model_fields)
    fields_in_app_ctx = set(app_context_model.model_fields)
    known_fields = fields_in_app_ctx.union(fields_in_lib_ctx)

    normalized_cfg = dict(cfg)

    lib_values = _extract_context_values(fields_in_lib_ctx, args, normalized_cfg)
    app_values = _extract_context_values(fields_in_app_ctx, args, normalized_cfg)

    #
    # Save the unused values
    #

    unused_cfg = {}
    if normalized_cfg:
        unused_cfg = {k: v for k, v in normalized_cfg.items() if k not in known_fields}

    unused_args = {}
    if args:
        unused_args = {k: v for k, v in vars(args).items() if k not in known_fields}

    # Unused values are saved in app_ctx.extra when use_extra is set
    if use_extra:
        unused_cfg.update(unused_args)
        app_values["extra"] = unused_cfg
        unused_cfg = {}
        unused_args = {}

    unused_args_ns = argparse.Namespace(**unused_args)

    # create new app and lib ctxt from the application's arguments and config.
    local_app_ctx = app_context_model(**app_values)
    local_lib_ctx = LibContext(**lib_values)

    return ContextReturn(
        app_ctx=local_app_ctx,
        lib_ctx=local_lib_ctx,
        args=unused_args_ns,
        cfg=unused_cfg,
    )


def _copy_lib_context() -> LibContext:
    try:
        old_context = lib_ctx.get()
    except LookupError:
        old_context = LibContext()

    # Copy just in case contexts are allowed to be writable in the the future
    return old_context.model_copy()


def _copy_app_context() -> AppContext:
    try:
        old_context = app_ctx.get()
    except LookupError:
        old_context = AppContext()

    # Copy just in case contexts are allowed to be writable in the the future
    return old_context.model_copy()


@contextmanager
def lib_context(
    new_context: LibContext | None = None,
) -> t.Generator[LibContext, None, None]:
    """
    Set up a new lib_context.

    :kwarg new_context: New lib context to setup.  If this is None, the context is set to a copy of
        the old context.
    """
    if new_context is None:
        new_context = _copy_lib_context()

    reset_token = lib_ctx.set(new_context)
    try:
        yield new_context
    finally:
        lib_ctx.reset(reset_token)


@t.overload
def app_context() -> AbstractContextManager[AppContext]: ...


@t.overload
def app_context(new_context: AppContextT) -> AbstractContextManager[AppContextT]: ...


@contextmanager
def app_context(new_context=None):
    """
    Set up a new app_context.

    :kwarg new_context: New app context to setup.
    """
    if new_context is None:
        new_context = _copy_app_context()

    reset_token = app_ctx.set(new_context)
    try:
        yield new_context
    finally:
        app_ctx.reset(reset_token)


@contextmanager
def app_and_lib_context(
    context_data: ContextReturn[AppContextT],
) -> t.Generator[tuple[AppContextT, LibContext], None, None]:
    """
    Set the app and lib context at the same time.

    This is a convenience wrapper around the :func:`app_context` and :func:`lib_context`
    context managers.  It's meant to be used with :func:`create_contexts` like this:

    .. code_block:: python

        context_data = create_contexts(args=args, cfg=cfg)

        with app_and_lib_context(context_data):
            do_something()
    """
    with lib_context(context_data.lib_ctx) as new_lib_ctx:
        with app_context(context_data.app_ctx) as new_app_ctx:
            yield (new_app_ctx, new_lib_ctx)


class AppContextWrapper(t.Generic[AppContextT]):
    def __repr__(self):
        return "<ContextVarWrapper name='app_ctx'>"

    @property
    def name(self):
        return "app_ctx"

    @staticmethod
    def get() -> AppContextT:
        return t.cast(AppContextT, app_ctx.get())


#
# Set initial contexts with default values
#
lib_ctx.set(LibContext())
app_ctx.set(AppContext())
