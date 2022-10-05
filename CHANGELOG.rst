============================
antsibull-core Release Notes
============================

.. contents:: Topics


v1.3.1
======

Release Summary
---------------

Maintenance release to fix unwanted ``1.3.0.post0`` release.

v1.3.0
======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- Allow to write Python dependencies as ``_python`` key into build and dependency files (https://github.com/ansible-community/antsibull-core/pull/10).

Bugfixes
--------

- Fix async file copying helper (https://github.com/ansible-community/antsibull-core/pull/11).

v1.2.0
======

Release Summary
---------------

Feature release.

Minor Changes
-------------

- Improve typing (https://github.com/ansible-community/antsibull-core/pull/6).
- Make config file management more flexible to allow project-specific config file format extensions for the explicitly passed configuration files (https://github.com/ansible-community/antsibull-core/pull/7).

Deprecated Features
-------------------

- The ``DepsFile.write()`` method will require the first parameter to be a ``packaging.version.Version`` object, the second parameter to be a string, and the third parameter a mapping of strings to strings, from antsibull-core 2.0.0 on (https://github.com/ansible-community/antsibull-core/pull/6).

Bugfixes
--------

- Adjust signature of ``DepsFile.write()`` to work around bug in antsibull (https://github.com/ansible-community/antsibull-core/pull/6).

v1.1.0
======

Release Summary
---------------

Maintenance release.

Minor Changes
-------------

- The files in the source repository now follow the `REUSE Specification <https://reuse.software/spec/>`_. The only exceptions are changelog fragments in ``changelogs/fragments/`` (https://github.com/ansible-community/antsibull-core/pull/5).

v1.0.1
======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- Fix detection of ansible-core devel checkouts (https://github.com/ansible-community/antsibull-core/pull/4).

v1.0.0
======

Release Summary
---------------

First stable release.

Major Changes
-------------

- From version 1.0.0 on, antsibull-core is sticking to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle (https://github.com/ansible-community/antsibull-core/pull/2).

Minor Changes
-------------

- Remove unused code (https://github.com/ansible-community/antsibull-core/pull/1).

Removed Features (previously deprecated)
----------------------------------------

- Remove package ``antsibull_core.utils.transformations`` (https://github.com/ansible-community/antsibull-core/pull/1).

v0.1.0
======

Release Summary
---------------

Initial release.
