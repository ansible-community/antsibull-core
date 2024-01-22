# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

import argparse

from pydantic import HttpUrl

import antsibull_core.app_context as ap
from antsibull_core.schemas.config import LoggingModel
from antsibull_core.utils.collections import ContextDict

#
# Context creation tests
#


def test_default():
    """Context has default values if no ocntext manager is used"""
    lib_ctx = ap.lib_ctx.get()
    assert lib_ctx.chunksize == 4096
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 8
    assert lib_ctx.max_retries == 10

    app_ctx = ap.app_ctx.get()
    assert app_ctx.extra == ContextDict()
    assert isinstance(app_ctx.logging_cfg, LoggingModel)


def test_create_contexts_with_cfg():
    """Test that the create_contexts function sets values from a config dict"""
    cfg = {"chunksize": 1, "unknown": True}
    app_ctx, lib_ctx, args, cfg = ap.create_contexts(cfg=cfg)

    assert args == argparse.Namespace()
    assert cfg == {}

    assert lib_ctx.chunksize == 1
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 8
    assert lib_ctx.max_retries == 10

    assert app_ctx.extra == ContextDict({"unknown": True})
    assert isinstance(app_ctx.logging_cfg, LoggingModel)


def test_create_contexts_with_args():
    """Test that the create_context function sets values from cli args"""
    args = {"process_max": 2, "unknown": True}
    args = argparse.Namespace(**args)
    app_ctx, lib_ctx, args, cfg = ap.create_contexts(args=args)

    assert args == argparse.Namespace()
    assert cfg == {}

    assert lib_ctx.chunksize == 4096
    assert lib_ctx.process_max == 2
    assert lib_ctx.thread_max == 8
    assert lib_ctx.max_retries == 10

    assert app_ctx.extra == ContextDict({"unknown": True})
    assert isinstance(app_ctx.logging_cfg, LoggingModel)


def test_create_contexts_with_args_and_cfg():
    """Test that args override cfg"""
    cfg = {
        "chunksize": 1,
        "thread_max": 2,
        "unknown": True,
        "cfg": 1,
    }
    args = {
        "chunksize": 3,
        "unknown": False,
        "args": 2,
    }
    args = argparse.Namespace(**args)
    app_ctx, lib_ctx, args, cfg = ap.create_contexts(args=args, cfg=cfg)

    assert args == argparse.Namespace()
    assert cfg == {}

    assert lib_ctx.chunksize == 3
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 2
    assert lib_ctx.max_retries == 10

    assert app_ctx.extra == ContextDict({"unknown": False, "cfg": 1, "args": 2})
    assert isinstance(app_ctx.logging_cfg, LoggingModel)


def test_create_contexts_without_extra():
    """Test that use_extra=False returns unused args and cfg."""
    cfg_data = {"chunksize": 7, "unknown": True, "cfg": 1}
    args_data = {"thread_max": 10, "unknown": False, "args": 2}
    input_args = argparse.Namespace(**args_data)
    app_ctx, lib_ctx, args, cfg = ap.create_contexts(
        args=input_args, cfg=cfg_data, use_extra=False
    )

    assert args == argparse.Namespace(unknown=False, args=2)
    assert cfg == {"unknown": True, "cfg": 1}

    assert lib_ctx.chunksize == 7
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 10
    assert lib_ctx.max_retries == 10

    assert app_ctx.extra == ContextDict()
    assert isinstance(app_ctx.logging_cfg, LoggingModel)


#
# Context manager tests
#


def test_context_overrides():
    data = ap.create_contexts(cfg={"chunksize": 5, "foo": "bar"})

    with ap.app_context(data.app_ctx) as app_ctx:
        # Test that the app_context that was returned has the new values
        assert app_ctx.extra["foo"] == "bar"

        # Test that the context that we can retrieve has the new values too
        app_ctx = ap.app_ctx.get()
        assert app_ctx.extra["foo"] == "bar"

    with ap.lib_context(data.lib_ctx) as lib_ctx:
        # Test that the returned lib_ctx has the new values
        assert lib_ctx.chunksize == 5

        # Likewise for the one that we can retrieve
        lib_ctx = ap.lib_ctx.get()
        assert lib_ctx.chunksize == 5

    # Check that once we return from the context managers, the old values have been restored
    app_ctx = ap.app_ctx.get()
    assert app_ctx.extra == ContextDict()
    assert isinstance(app_ctx.logging_cfg, LoggingModel)

    lib_ctx = ap.lib_ctx.get()
    assert lib_ctx.chunksize == 4096
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 8
    assert lib_ctx.max_retries == 10


def test_manager_creates_new_context():
    orig_app_ctx = ap.app_ctx.get()
    with ap.app_context() as app_ctx:
        new_app_ctx = ap.app_ctx.get()
        # Test that the app_ctx that was returned is the same as the one that is now set
        assert app_ctx is new_app_ctx

        # Test that the new app_ctx is different than the old one
        assert new_app_ctx is not orig_app_ctx

        # Test that the app_ctx that was returned has the same values as the old context
        assert new_app_ctx == orig_app_ctx

    orig_lib_ctx = ap.lib_ctx.get()
    with ap.lib_context() as lib_ctx:
        new_lib_ctx = ap.lib_ctx.get()
        # Test that the lib_ctx that was returned is the same as the one that is now set
        assert lib_ctx is new_lib_ctx

        # Test that the new lib_ctx is different than the old one
        assert new_lib_ctx is not orig_lib_ctx

        # Test that the lib_ctx that was returned has the same values as the old context
        assert new_lib_ctx == orig_lib_ctx

    # Check that once we return from the context managers, the old contexts have been returned
    assert orig_app_ctx is ap.app_ctx.get()
    assert orig_lib_ctx is ap.lib_ctx.get()


def test_app_and_lib_context():
    data = ap.create_contexts(cfg={"chunksize": 5, "foo": "bar"})

    with ap.app_and_lib_context(data) as (app_ctx, lib_ctx):
        # Test that the app_context that was returned has the new values
        assert app_ctx.extra["foo"] == "bar"

        # Test that the context that we can retrieve has the new values too
        app_ctx = ap.app_ctx.get()
        assert app_ctx.extra["foo"] == "bar"

        # Test that the returned lib_ctx has the new values
        assert lib_ctx.chunksize == 5

        # Likewise for the one that we can retrieve
        lib_ctx = ap.lib_ctx.get()
        assert lib_ctx.chunksize == 5

    # Check that once we return from the context manager, the old values have been restored
    app_ctx = ap.app_ctx.get()
    assert app_ctx.extra == ContextDict()
    assert isinstance(app_ctx.logging_cfg, LoggingModel)

    lib_ctx = ap.lib_ctx.get()
    assert lib_ctx.chunksize == 4096
    assert lib_ctx.process_max is None
    assert lib_ctx.thread_max == 8
    assert lib_ctx.max_retries == 10
