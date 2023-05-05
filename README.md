<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# antsibull-core -- Library for Ansible Build Scripts
[![Python linting badge](https://github.com/ansible-community/antsibull-core/workflows/Python%20linting/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-core/actions?query=workflow%3A%22Python+linting%22+branch%3Amain)
[![Python testing badge](https://github.com/ansible-community/antsibull-core/workflows/Python%20testing/badge.svg?event=push&branch=main)](https://github.com/ansible-community/antsibull-core/actions?query=workflow%3A%22Python+testing%22+branch%3Amain)
[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-core)](https://codecov.io/gh/ansible-community/antsibull-core)

Library needed for tooling for building various things related to Ansible.

You can find a list of changes in [the antsibull-core changelog](./CHANGELOG.rst).

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later.

antsibull-core is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).

## Versioning and compatibility

From version 1.0.0 on, antsibull-core sticks to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.

The current major version is 2.x.y. Development for 2.x.y occurs on the `main` branch. 2.x.y mainly differs from 1.x.y by dropping support for Python 3.6, 3.7, and 3.8. It deprecates several compatibility functions for older Python versions that are no longer needed; see the changelog for details. 1.x.y is still developed on the `stable-1` branch, but only security fixes, major bugfixes, and other changes that are absolutely necessary for the other antsibull projects will be backported.

## Creating a new release:

If you want to create a new release::

    vim pyproject.toml  # Make sure version number is correct
    vim changelogs/fragment/$VERSION_NUMBER.yml  # create 'release_summary:' fragment
    antsibull-changelog release --version $VERSION_NUMBER
    git add CHANGELOG.rst changelogs
    git commit -m "Release $VERSION_NUMBER."
    poetry build
    poetry publish  # Uploads to pypi.  Be sure you really want to do this

    git tag $VERSION_NUMBER
    git push --tags
    vim pyproject.toml  # Bump the version number to X.Y.Z.post0
    git commit -m 'Update the version number for the next release' pyproject.toml
    git push

## License

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later. See
[LICENSES/GPL-3.0-or-later.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSE)
for a copy of the license.

Parts of the code are vendored from other sources and are licensed under other licenses:
1. `src/antsibull_core/vendored/collections.py` and `src/antsibull_core/vendored/json_utils.py` are licensed under the terms of the BSD 2-Clause license. See [LICENSES/BSD-2-Clause.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/BSD-2-Clause.txt) for a copy of the license.
2. `tests/functional/aiohttp_utils.py` and `tests/functional/certificate_utils.py` are licensed under the terms of the MIT license. See [LICENSES/MIT.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/MIT.txt) for a copy of the license.
3. `src/antsibull_core/vendored/_argparse_booleanoptionalaction.py` is licensed under the terms of the Python Software Foundation license version 2. See [LICENSES/PSF-2.0.txt](https://github.com/ansible-community/antsibull-changelog/tree/main/LICENSES/PSF-2.0.txt) for a copy of the license.

The repository follows the [REUSE Specification](https://reuse.software/spec/) for declaring copyright and
licensing information. The only exception are changelog fragments in ``changelog/fragments/``.
