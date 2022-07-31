# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from packaging.version import Version as PypiVer
from semantic_version import Version as SemVer

import pytest

from antsibull_core.dependency_files import BuildFile


SIMPLE_TEST_FILE = """_ansible_version: 4
_ansible_base_version: 2.11.0rc1
community.general: >=1.0.0,<2.0.0
community.routeros: >=2.0.0-a2,<3.0.0
"""

SIMPLE_TEST_DEPS = {'community.general': SemVer('1.0.0'),
                    'community.routeros': SemVer('2.0.0-a2'),
                    }

SIMPLE_TEST_FILE_2 = """_ansible_version: 6
_ansible_core_version: 2.13.0rc1
community.general: >=1.0.0,<2.0.0
community.routeros: >=2.0.0-a2,<3.0.0
"""

SIMPLE_TEST_DEPS_2 = {'community.general': SemVer('1.0.0'),
                    'community.routeros': SemVer('2.0.0-a2'),
                    }

@pytest.mark.parametrize('ansible_ver, core_ver, dependencies, file_contents', (
    ('4.0.0', '2.11.0rc1', SIMPLE_TEST_DEPS, SIMPLE_TEST_FILE),
    ('6.0.0', '2.13.0rc1', SIMPLE_TEST_DEPS_2, SIMPLE_TEST_FILE_2),
))
def test_build_file_write(tmpdir, ansible_ver, core_ver, dependencies, file_contents):
    filename = tmpdir / 'test.build'
    bf = BuildFile(filename)
    bf.write(PypiVer(ansible_ver), core_ver, dependencies)

    with open(filename) as f:
        assert f.read() == file_contents
