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
