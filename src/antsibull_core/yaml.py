# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project

"""
YAML handling.
"""

import typing as t

import yaml

_SafeLoader: t.Any
_SafeDumper: t.Any
try:
    # use C version if possible for speedup
    from yaml import CSafeLoader as _SafeLoader
    from yaml import CSafeDumper as _SafeDumper
except ImportError:
    from yaml import SafeLoader as _SafeLoader
    from yaml import SafeDumper as _SafeDumper

if t.TYPE_CHECKING:
    # TODO PY3.8: Use __future__.annotations instead of quoting annotations
    # pylint:disable=unused-import
    from _typeshed import StrOrBytesPath


def load_yaml_bytes(data: bytes) -> t.Any:
    """
    Load and parse YAML from given bytes.
    """
    return yaml.load(data, Loader=_SafeLoader)


def load_yaml_file(path: "StrOrBytesPath") -> t.Any:
    """
    Load and parse YAML file ``path``.
    """
    with open(path, 'rb') as stream:
        return yaml.load(stream, Loader=_SafeLoader)


def store_yaml_file(path: "StrOrBytesPath", content: t.Any) -> None:
    """
    Store ``content`` as YAML file under ``path``.
    """
    with open(path, 'wb') as stream:
        dumper = _SafeDumper
        dumper.ignore_aliases = lambda *args: True
        yaml.dump(content, stream, default_flow_style=False, encoding='utf-8', Dumper=dumper)
