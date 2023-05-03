============================
antsibull-core Release Notes
============================

.. contents:: Topics


v2.0.0
======

Release Summary
---------------

New major release

Minor Changes
-------------

- Add ``async_log_run()`` and ``log_run()`` methods to ``antsibull_core.venv.VenvRunner` and ``antsibull_core.venv.FakeVenvRunner``. These should be used instead of ``get_command()`` (https://github.com/ansible-community/antsibull-core/pull/50).
- Add a ``store_yaml_stream`` function to ``antsibull_core.yaml`` to dump YAML to an IO stream (https://github.com/ansible-community/antsibull-core/pull/24).
- Add a new ``antsibull_core.subprocess_util`` module to help run subprocesses output and log their output (https://github.com/ansible-community/antsibull-core/pull/40).
- Allow Galaxy client to communicate with the Galaxy v3 API (https://github.com/ansible-community/antsibull-core/pull/45).
- Allow the Galaxy downloader to trust its collection cache to avoid having to query the Galaxy server if an artifact exists in the cache. This can be set with the new configuration file option ``trust_collection_cache`` (https://github.com/ansible-community/antsibull-core/pull/78).
- Allow to cache ansible-core download artifacts with a new config file option ``ansible_core_cache`` (https://github.com/ansible-community/antsibull-core/pull/80).
- Allow to fully trust the ansible-core artifacts cache to avoid querying PyPI with a new config file option ``trust_ansible_core_cache`` (https://github.com/ansible-community/antsibull-core/pull/80).
- Allow to skip content check when doing async file copying using ``antsibull_core.utils.io.copy_file()`` (https://github.com/ansible-community/antsibull-core/pull/78).
- Avoid using the collection artifact filename returned by the Galaxy server. Instead compose it in a uniform way (https://github.com/ansible-community/antsibull-core/pull/78).
- Replace internal usage of ``sh`` with the ``antsibull.subprocess_util`` module (https://github.com/ansible-community/antsibull-core/pull/51).
- The fields ``ansible_core_repo_url``, ``galaxy_url``, and ``pypi_url`` have been added to the library context. If ``ansible_core_repo_url`` is not provided, it will be populated from the field ``ansible_base_url`` if that has been provided (https://github.com/ansible-community/antsibull-core/pull/81).
- Use the pypa ``build`` tool instead of directly calling ``setup.py`` which is deprecated (https://github.com/ansible-community/antsibull-core/pull/51).

Breaking Changes / Porting Guide
--------------------------------

- Remove ``breadcrumbs``, ``indexes``, and ``use_html_blobs`` from global antsibull config handling. These options are only used by antsibull-docs, which already validates them itself (https://github.com/ansible-community/antsibull-core/pull/54).
- Support for Python 3.6, 3.7, and 3.8 has been dropped. antsibull-core 2.x.y needs Python 3.9 or newer. If you need to use Python 3.6 to 3.8, please use antsibull-core 1.x.y (https://github.com/ansible-community/antsibull-core/pull/16).
- The ``install_package()`` method of ``antsibull_core.venv.VenvRunner`` now returns a ``subprocess.CompletedProcess`` object instead of an ``sh.RunningCommand``. The rest of the function signature remains the same. Most callers should not need to access the output to begin with (https://github.com/ansible-community/antsibull-core/pull/50).

Deprecated Features
-------------------

- Deprecate the ``get_command()`` methods of ``antsibull_core.venv.VenvRunner` and ``antsibull_core.venv.FakeVenvRunner``. These methods will be removed in antsibull-core 3.0.0. Use the new ``log_run()`` and ``async_run()`` methods instead (https://github.com/ansible-community/antsibull-core/pull/50).
- The ``antsibull_core.compat`` module deprecates the ``metadata`` module. Use ``importlib.metadata`` instead, which is available from Python 3.8 on (https://github.com/ansible-community/antsibull-core/pull/16).
- The ``antsibull_core.compat`` module deprecates the functions ``asyncio_run``, ``best_get_loop``, and ``create_task``. Replace ``asyncio_run`` with ``asyncio.run``, ``create_task`` with ``asyncio.create_task``, and ``best_get_loop`` with ``asyncio.get_running_loop`` (https://github.com/ansible-community/antsibull-core/pull/16).
- The ``doc_parsing_backend`` option from the library context is deprecated and will be removed in antsibull-core 3.0.0. Applications that need it, such as antsibull-docs, must ensure they allow and validate this option themselves (https://github.com/ansible-community/antsibull-core/pull/59).
- The fields ``ansible_base_url``, ``galaxy_url``, and ``pypi_url`` of the app context have been deprecated. Use the fields ``ansible_core_repo_url``, ``galaxy_url``, and ``pypi_url``, respectively, of the library context instead (https://github.com/ansible-community/antsibull-core/pull/81).

Removed Features (previously deprecated)
----------------------------------------

- The unused ``antsibull_core.schemas.config.ConfigModel`` model and the unused ``antsibull_core.config.read_config`` function have been removed (https://github.com/ansible-community/antsibull-core/pull/82).

Bugfixes
--------

- Fix a bug in Galaxy download code when the filename is found in the cache, but the checksum does not match. In that case, the collection was not copied to the destination, and the code did not try to download the correct file (https://github.com/ansible-community/antsibull-core/pull/76).
- Remove improper usage of ``@functools.cache`` on async functions in the ``antsibull_core.ansible_core`` module (https://github.com/ansible-community/antsibull-core/pull/67).
- Restrict the ``pydantic`` dependency to major version 1 (https://github.com/ansible-community/antsibull-core/pull/35).
- Restrict the ``sh`` dependency to versions before 2.0.0 (https://github.com/ansible-community/antsibull-core/pull/31).

v1.4.0
======

Release Summary
---------------

Bugfix and feature release.

Minor Changes
-------------

- Fix overly restrictive file name type annotations. Use ``StrOrBytesPath`` type annotation instead of ``str`` for functions that accept a file name (https://github.com/ansible-community/antsibull-core/pull/14).

Bugfixes
--------

- Remove use of blocking IO in an async function (https://github.com/ansible-community/antsibull-core/pull/13/).

v1.3.1
======

Release Summary
---------------

Maintenance release to fix unwanted ``1.3.0.post0`` release.

v1.3.0.post0
============

Release Summary
---------------

Erroneously released version.

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
