# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

import pytest
from packaging.version import Version

import antsibull_core.ansible_core as ac


@pytest.mark.parametrize(
    "version, is_devel",
    [
        ("2.14.0dev0", True),
        ("2.14.0", False),
    ],
)
def test_get_core_package_name_returns_ansible_core(version, is_devel):
    assert ac._version_is_devel(Version(version)) == is_devel
