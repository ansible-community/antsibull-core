# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021, Ansible Project

"""
YAML handling.
"""

from __future__ import annotations

# pylint: disable=unused-import
from antsibull_fileutils.yaml import load_yaml_bytes  # noqa: F401
from antsibull_fileutils.yaml import load_yaml_file  # noqa: F401
from antsibull_fileutils.yaml import store_yaml_file  # noqa: F401
from antsibull_fileutils.yaml import store_yaml_stream  # noqa: F401
