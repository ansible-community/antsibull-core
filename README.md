<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# antsibull-core -- Library for Ansible Build Scripts
[![Discuss on Matrix at #antsibull:ansible.com](https://img.shields.io/matrix/antsibull:ansible.com.svg?server_fqdn=ansible-accounts.ems.host&label=Discuss%20on%20Matrix%20at%20%23antsibull:ansible.com&logo=matrix)](https://matrix.to/#/#antsibull:ansible.com)
[![Nox badge](https://github.com/ansible-community/antsibull-core/actions/workflows/nox.yml/badge.svg)](https://github.com/ansible-community/antsibull-core/actions/workflows/nox.yml)
[![Codecov badge](https://img.shields.io/codecov/c/github/ansible-community/antsibull-core)](https://codecov.io/gh/ansible-community/antsibull-core)
[![REUSE status](https://api.reuse.software/badge/github.com/ansible-community/antsibull-core)](https://api.reuse.software/info/github.com/ansible-community/antsibull-core)

Library needed for tooling for building various things related to Ansible.

You can find a list of changes in [the antsibull-core changelog](./CHANGELOG.rst).

Unless otherwise noted in the code, it is licensed under the terms of the GNU
General Public License v3 or, at your option, later.

antsibull-core is covered by the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html).

## Versioning and compatibility

From version 1.0.0 on, antsibull-core sticks to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle. We might make exceptions from this in case of security fixes for vulnerabilities that are severe enough.

The current development version is 3.x.y. 3.x.y is developed on the `main` branch. The current supported major version is 2.x.y. Development for 2.x.y occurs on the `stable-2` branch. 1.x.y is End of Life and was developed on the `stable-1` branch. It is no longer updated. 2.x.y mainly differs from 1.x.y by dropping support for Python 3.6, 3.7, and 3.8. It deprecates several compatibility functions for older Python versions that are no longer needed; see the changelog for details.

## Development

Install and run `nox` to run all tests. That's it for simple contributions!
`nox` will create virtual environments in `.nox` inside the checked out project
and install the requirements needed to run the tests there.

---

antsibull-core depends on the sister antsibull-fileutils project.
By default, `nox` will install a development version of this project from Github.
If you're hacking on antsibull-fileutils alongside antsibull-core,
nox will automatically install this project from `../antsibull-fileutils`
when running tests if this path exists.
You can change this behavior through the `OTHER_ANTSIBULL_MODE` env var:

- `OTHER_ANTSIBULL_MODE=auto` — the default behavior described above
- `OTHER_ANTSIBULL_MODE=local` — install the project from `../antsibull-fileutils`.
  Fail if this path doesn't exist.
- `OTHER_ANTSIBULL_MODE=git` — install the project from the Github main branch
- `OTHER_ANTSIBULL_MODE=pypi` — install the latest version from PyPI

---

To run specific tests:

1. `nox -e test` to only run unit tests;
2. `nox -e coverage` to display combined coverage results after running `nox -e
   test`;
3. `nox -e lint` to run all linters and formatters at once;
4. `nox -e formatters` to run `isort` and `black`;
3. `nox -e codeqa` to run `flake8`, `pylint`, `reuse lint`, and `antsibull-changelog lint`;
6. `nox -e typing` to run `mypy` and `pyre`

## Creating a new release:

1. Run `nox -e bump -- <version> <release_summary_message>`. This:
   * Bumps the package version in `src/antsibull_core/__init__.py`.
   * Creates `changelogs/fragments/<version>.yml` with a `release_summary` section.
   * Runs `antsibull-changelog release` and adds the changed files to git.
   * Commits with message `Release <version>.` and runs `git tag -a -m 'antsibull-core <version>' <version>`.
   * Runs `hatch build`.
2. Run `git push` to the appropriate remotes.
3. Once CI passes on GitHub, run `nox -e publish`. This:
   * Runs `hatch publish`;
   * Bumps the version to `<version>.post0`;
   * Adds the changed file to git and run `git commit -m 'Post-release version bump.'`;
4. Run `git push --follow-tags` to the appropriate remotes and create a GitHub release.

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
