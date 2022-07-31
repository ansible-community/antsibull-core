# Author: Toshio Kuratomi <tkuratom@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2020, Ansible Project
"""Argument parsing helpers."""

import argparse
import os.path

from .compat import metadata


class InvalidArgumentError(Exception):
    """A problem parsing or validating a command line argument."""


def get_toplevel_parser(package, **kwargs) -> argparse.ArgumentParser:
    """
    Create a toplevel argument parser with options common across all scripts.

    :arg package: The Python package containing this CLI program.
    :args kwargs: This function takes any keyword arguments and passes them directly on to
        the :class:`argparse.ArgumentParser` constructor.
    :returns: :class:`argparse.ArgumentParser` with common script arguments added.
    """
    try:
        version = metadata.version(package)
    except metadata.PackageNotFoundError:
        # If there's no metadata foun, assume we're running from source
        version = 'source'

    toplevel_parser = argparse.ArgumentParser(**kwargs)
    toplevel_parser.add_argument('--version', action='version', version=version,
                                 help='Print the antsibull version')
    toplevel_parser.add_argument('--config-file', default=[], action='append',
                                 help='Specify one or more config files to use to configure the'
                                 ' program. If more than one are specified, keys from later'
                                 ' config files override keys from earlier ones.')
    return toplevel_parser


def normalize_toplevel_options(args: argparse.Namespace) -> None:
    """
    Normalize and validate the common cli arguments.

    :arg args: The argparse parsed arguments.  The arguments added by the common parser will be
        validated and normalized.

    .. warning:: This function operates by side effect.

        Any normalization needed will be applied directly to ``args``.
    """
    for conf_file in args.config_file:
        if not os.path.isfile(conf_file):
            raise InvalidArgumentError(f'The user specified config file, {conf_file},'
                                       ' must exist.')
