# antsibull\-core Release Notes

**Topics**

- <a href="#v3-3-0">v3\.3\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
- <a href="#v3-2-0">v3\.2\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v3-1-0">v3\.1\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
- <a href="#v3-0-2">v3\.0\.2</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v3-0-1">v3\.0\.1</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v3-0-0">v3\.0\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v2-2-0">v2\.2\.0</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v2-1-0">v2\.1\.0</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
- <a href="#v2-0-0">v2\.0\.0</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-1">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated-1">Removed Features \(previously deprecated\)</a>
    - <a href="#bugfixes-5">Bugfixes</a>
- <a href="#v1-4-0">v1\.4\.0</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v1-3-1">v1\.3\.1</a>
    - <a href="#release-summary-10">Release Summary</a>
- <a href="#v1-3-0-post0">v1\.3\.0\.post0</a>
    - <a href="#release-summary-11">Release Summary</a>
- <a href="#v1-3-0">v1\.3\.0</a>
    - <a href="#release-summary-12">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v1-2-0">v1\.2\.0</a>
    - <a href="#release-summary-13">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-8">Bugfixes</a>
- <a href="#v1-1-0">v1\.1\.0</a>
    - <a href="#release-summary-14">Release Summary</a>
    - <a href="#minor-changes-9">Minor Changes</a>
- <a href="#v1-0-1">v1\.0\.1</a>
    - <a href="#release-summary-15">Release Summary</a>
    - <a href="#bugfixes-9">Bugfixes</a>
- <a href="#v1-0-0">v1\.0\.0</a>
    - <a href="#release-summary-16">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes-10">Minor Changes</a>
    - <a href="#removed-features-previously-deprecated-2">Removed Features \(previously deprecated\)</a>
- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#release-summary-17">Release Summary</a>

<a id="v3-3-0"></a>
## v3\.3\.0

<a id="release-summary"></a>
### Release Summary

Feature release\.

<a id="minor-changes"></a>
### Minor Changes

* Allow information on removed collections from previous major releases in collection metadata schema \([https\://github\.com/ansible\-community/antsibull\-core/pull/174](https\://github\.com/ansible\-community/antsibull\-core/pull/174)\)\.

<a id="v3-2-0"></a>
## v3\.2\.0

<a id="release-summary-1"></a>
### Release Summary

Feature and bugfix release\.

<a id="minor-changes-1"></a>
### Minor Changes

* Add pydantic helper for strict linting \([https\://github\.com/ansible\-community/antsibull\-core/pull/169](https\://github\.com/ansible\-community/antsibull\-core/pull/169)\)\.
* Allow information on removed collections in collection metadata schema \([https\://github\.com/ansible\-community/antsibull\-core/pull/173](https\://github\.com/ansible\-community/antsibull\-core/pull/173)\)\.

<a id="bugfixes"></a>
### Bugfixes

* Collection metadata removal schema valiation\: remove bad check that deprecated redirect replacement major version must be in the future \([https\://github\.com/ansible\-community/antsibull\-core/pull/172](https\://github\.com/ansible\-community/antsibull\-core/pull/172)\)\.

<a id="v3-1-0"></a>
## v3\.1\.0

<a id="release-summary-2"></a>
### Release Summary

Feature release adding a new dependency\.

<a id="minor-changes-2"></a>
### Minor Changes

* Add schema and validation helper for ansible\-build\-data\'s collection meta \([https\://github\.com/ansible\-community/ansible\-build\-data/pull/450](https\://github\.com/ansible\-community/ansible\-build\-data/pull/450)\, [https\://github\.com/ansible\-community/antsibull\-core/pull/168](https\://github\.com/ansible\-community/antsibull\-core/pull/168)\)\.
* Antsibull\-core now depends on the new project antsibull\-fileutils\. Some code has been moved to that library\; that code is re\-imported to avoid breaking changes for users of antsibull\-core \([https\://github\.com/ansible\-community/antsibull\-core/pull/166](https\://github\.com/ansible\-community/antsibull\-core/pull/166)\)\.

<a id="v3-0-2"></a>
## v3\.0\.2

<a id="release-summary-3"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-1"></a>
### Bugfixes

* Adjust the aiohttp retry GET mananger to use <code>ClientTimeout</code> instead of a <code>float</code>\, since that will be removed in aiohttp 4\.0\.0 \([https\://github\.com/ansible\-community/antsibull\-core/pull/163](https\://github\.com/ansible\-community/antsibull\-core/pull/163)\)\.
* Bump asyncio requirement to \>\= 3\.3\.0 instead of 3\.0\.0\. Version 3\.0\.0 likely never worked with the retry code that has been in here basically since he beginning \([https\://github\.com/ansible\-community/antsibull\-core/pull/163](https\://github\.com/ansible\-community/antsibull\-core/pull/163)\)\.
* Make sure that app and lib contexts are cleaned up correctly in case of generator exit \([https\://github\.com/ansible\-community/antsibull\-core/pull/161](https\://github\.com/ansible\-community/antsibull\-core/pull/161)\)\.
* Make sure that the right <code>TimeoutError</code> is used in the HTTP retry util\. <code>asyncio\.TimeoutError</code> is a deprecated alias of <code>TimeoutError</code> since Python 3\.11 \([https\://github\.com/ansible\-community/antsibull\-core/pull/160](https\://github\.com/ansible\-community/antsibull\-core/pull/160)\)\.

<a id="v3-0-1"></a>
## v3\.0\.1

<a id="release-summary-4"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-2"></a>
### Bugfixes

* Adjusting ansible\-core PyPI code to also accept a filename starting with <code>ansible\_core</code>\, which seems to be in use since ansible\-core 2\.16\.6 due to [PEP\-625](https\://peps\.python\.org/pep\-0625/) support in setuptools 69\.3\.0 \([https\://github\.com/ansible\-community/antsibull\-core/pull/158](https\://github\.com/ansible\-community/antsibull\-core/pull/158)\)\.

<a id="v3-0-0"></a>
## v3\.0\.0

<a id="release-summary-5"></a>
### Release Summary

New major release\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* Drop support for building Ansible versions less than 6\.0\.0 \([https\://github\.com/ansible\-community/antsibull\-core/pull/132](https\://github\.com/ansible\-community/antsibull\-core/pull/132)\)\.
* Remove <code>GalaxyClient</code>\'s and <code>CollectionDownloader</code>\'s <code>galaxy\_server</code> arguments\. You need to explicitly pass in a <code>GalaxyContext</code> object instead \([https\://github\.com/ansible\-community/antsibull\-core/pull/131](https\://github\.com/ansible\-community/antsibull\-core/pull/131)\)\.
* antsibull\-core now requires major version 2 of the <code>pydantic</code> library\. Version 1 is no longer supported \([https\://github\.com/ansible\-community/antsibull\-core/pull/122](https\://github\.com/ansible\-community/antsibull\-core/pull/122)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* If <code>ansible\_base\_url</code> is provided in a config file\, but <code>ansible\_core\_repo\_url</code> is not\, its value is no longer used for <code>ansible\_core\_repo\_url</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/128](https\://github\.com/ansible\-community/antsibull\-core/pull/128)\)\.
* Remove dependency on <code>sh</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/119](https\://github\.com/ansible\-community/antsibull\-core/pull/119)\)\.
* Removed the deprecated field <code>doc\_parsing\_backend</code> from <code>LibContext</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/128](https\://github\.com/ansible\-community/antsibull\-core/pull/128)\)\.
* Removed the deprecated fields <code>ansible\_base\_url</code>\, <code>galaxy\_url</code>\, <code>pypi\_url</code>\, and <code>collection\_cache</code> from <code>AppContext</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/128](https\://github\.com/ansible\-community/antsibull\-core/pull/128)\)\.
* <code>ansible\_core</code> \- remove <code>get\_ansible\_core\_package\_name\(\)</code> function\. This is no longer necessary now that support for ansible\-base has been dropped \([https\://github\.com/ansible\-community/antsibull\-core/pull/132](https\://github\.com/ansible\-community/antsibull\-core/pull/132)\)\.
* <code>ansible\_core</code> \- remove ansible\-core/ansible\-base normalization in <code>AnsibleCorePyPiClient</code>\. Data retrieval is only supported for <code>ansible\-core</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/132](https\://github\.com/ansible\-community/antsibull\-core/pull/132)\)\.
* <code>antsibull\_core\.compat</code> \- remove deprecated <code>asyncio\_run</code>\, <code>best\_get\_loop</code>\, <code>create\_task</code> and <code>metadata</code> \([https\://github\.com/ansible\-community/antsibull\-core/issues/124](https\://github\.com/ansible\-community/antsibull\-core/issues/124)\, [https\://github\.com/ansible\-community/antsibull\-core/pull/129](https\://github\.com/ansible\-community/antsibull\-core/pull/129)\)\.
* <code>dependency\_files</code> \- drop support for <code>\_ansible\_base\_version</code> and <code>\_acd\_version</code> in pieces files\. <code>\_ansible\_core\_version</code> and <code>\_ansible\_version</code>\, respectively\, should be used instead \([https\://github\.com/ansible\-community/antsibull\-core/pull/132](https\://github\.com/ansible\-community/antsibull\-core/pull/132)\)\.
* <code>venv</code> \- remove <code>get\_command\(\)</code> method from <code>VenvRunner</code> and <code>FakeVenvRunner</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/119](https\://github\.com/ansible\-community/antsibull\-core/pull/119)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* Avoid superfluous network request when trusting the ansible\-core download cache \([https\://github\.com/ansible\-community/antsibull\-core/pull/135](https\://github\.com/ansible\-community/antsibull\-core/pull/135)\)\.

<a id="v2-2-0"></a>
## v2\.2\.0

<a id="release-summary-6"></a>
### Release Summary

Add support for Python 3\.12 and improve <code>subprocess\_util</code>

<a id="minor-changes-3"></a>
### Minor Changes

* Declare support for Python 3\.12 \([https\://github\.com/ansible\-community/antsibull\-core/pull/103](https\://github\.com/ansible\-community/antsibull\-core/pull/103)\)\.
* <code>subprocess\_util\.async\_log\_run\(\)</code>\, <code>subprocess\_util\.log\_run\(\)</code>\, and the corresponding functions  in <code>venv</code> now support passing generic callback functions for <code>stdout\_loglevel</code> and <code>stderr\_loglevel</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/113](https\://github\.com/ansible\-community/antsibull\-core/pull/113)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* Fix typing for <code>antsibull\_core\.app\_context\.app\_context\(\)</code> functions \([https\://github\.com/ansible\-community/antsibull\-core/pull/109](https\://github\.com/ansible\-community/antsibull\-core/pull/109)\)\.
* <code>subprocess\_util\.log\_run</code> \- use proper string formatting when passing command output to the logger \([https\://github\.com/ansible\-community/antsibull\-core/pull/116](https\://github\.com/ansible\-community/antsibull\-core/pull/116)\)\.

<a id="v2-1-0"></a>
## v2\.1\.0

<a id="release-summary-7"></a>
### Release Summary

Feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* Allow to overwrite the version and the program name when using <code>antsibull\_core\.args\.get\_toplevel\_parser\(\)</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/96](https\://github\.com/ansible\-community/antsibull\-core/pull/96)\)\.

<a id="v2-0-0"></a>
## v2\.0\.0

<a id="release-summary-8"></a>
### Release Summary

New major release

<a id="minor-changes-5"></a>
### Minor Changes

* Add <code>async\_log\_run\(\)</code> and <code>log\_run\(\)</code> methods to <code>antsibull\_core\.venv\.VenvRunner</code> and <code>antsibull\_core\.venv\.FakeVenvRunner</code>\. These should be used instead of <code>get\_command\(\)</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/50](https\://github\.com/ansible\-community/antsibull\-core/pull/50)\)\.
* Add a <code>store\_yaml\_stream</code> function to <code>antsibull\_core\.yaml</code> to dump YAML to an IO stream \([https\://github\.com/ansible\-community/antsibull\-core/pull/24](https\://github\.com/ansible\-community/antsibull\-core/pull/24)\)\.
* Add a new <code>antsibull\_core\.subprocess\_util</code> module to help run subprocesses output and log their output \([https\://github\.com/ansible\-community/antsibull\-core/pull/40](https\://github\.com/ansible\-community/antsibull\-core/pull/40)\)\.
* Allow Galaxy client to communicate with the Galaxy v3 API \([https\://github\.com/ansible\-community/antsibull\-core/pull/45](https\://github\.com/ansible\-community/antsibull\-core/pull/45)\)\.
* Allow the Galaxy downloader to trust its collection cache to avoid having to query the Galaxy server if an artifact exists in the cache\. This can be set with the new configuration file option <code>trust\_collection\_cache</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/78](https\://github\.com/ansible\-community/antsibull\-core/pull/78)\)\.
* Allow to cache ansible\-core download artifacts with a new config file option <code>ansible\_core\_cache</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/80](https\://github\.com/ansible\-community/antsibull\-core/pull/80)\)\.
* Allow to fully trust the ansible\-core artifacts cache to avoid querying PyPI with a new config file option <code>trust\_ansible\_core\_cache</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/80](https\://github\.com/ansible\-community/antsibull\-core/pull/80)\)\.
* Allow to skip content check when doing async file copying using <code>antsibull\_core\.utils\.io\.copy\_file\(\)</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/78](https\://github\.com/ansible\-community/antsibull\-core/pull/78)\)\.
* Avoid using the collection artifact filename returned by the Galaxy server\. Instead compose it in a uniform way \([https\://github\.com/ansible\-community/antsibull\-core/pull/78](https\://github\.com/ansible\-community/antsibull\-core/pull/78)\)\.
* Replace internal usage of <code>sh</code> with the <code>antsibull\.subprocess\_util</code> module \([https\://github\.com/ansible\-community/antsibull\-core/pull/51](https\://github\.com/ansible\-community/antsibull\-core/pull/51)\)\.
* The fields <code>ansible\_core\_repo\_url</code>\, <code>galaxy\_url</code>\, and <code>pypi\_url</code> have been added to the library context\. If <code>ansible\_core\_repo\_url</code> is not provided\, it will be populated from the field <code>ansible\_base\_url</code> if that has been provided \([https\://github\.com/ansible\-community/antsibull\-core/pull/81](https\://github\.com/ansible\-community/antsibull\-core/pull/81)\)\.
* Use the pypa <code>build</code> tool instead of directly calling <code>setup\.py</code> which is deprecated \([https\://github\.com/ansible\-community/antsibull\-core/pull/51](https\://github\.com/ansible\-community/antsibull\-core/pull/51)\)\.

<a id="breaking-changes--porting-guide-1"></a>
### Breaking Changes / Porting Guide

* Remove <code>breadcrumbs</code>\, <code>indexes</code>\, and <code>use\_html\_blobs</code> from global antsibull config handling\. These options are only used by antsibull\-docs\, which already validates them itself \([https\://github\.com/ansible\-community/antsibull\-core/pull/54](https\://github\.com/ansible\-community/antsibull\-core/pull/54)\)\.
* Support for Python 3\.6\, 3\.7\, and 3\.8 has been dropped\. antsibull\-core 2\.x\.y needs Python 3\.9 or newer\. If you need to use Python 3\.6 to 3\.8\, please use antsibull\-core 1\.x\.y \([https\://github\.com/ansible\-community/antsibull\-core/pull/16](https\://github\.com/ansible\-community/antsibull\-core/pull/16)\)\.
* The <code>install\_package\(\)</code> method of <code>antsibull\_core\.venv\.VenvRunner</code> now returns a <code>subprocess\.CompletedProcess</code> object instead of an <code>sh\.RunningCommand</code>\. The rest of the function signature remains the same\. Most callers should not need to access the output to begin with \([https\://github\.com/ansible\-community/antsibull\-core/pull/50](https\://github\.com/ansible\-community/antsibull\-core/pull/50)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* Deprecate the <code>get\_command\(\)</code> methods of <code>antsibull\_core\.venv\.VenvRunner</code> and <code>antsibull\_core\.venv\.FakeVenvRunner</code>\. These methods will be removed in antsibull\-core 3\.0\.0\. Use the new <code>log\_run\(\)</code> and <code>async\_run\(\)</code> methods instead \([https\://github\.com/ansible\-community/antsibull\-core/pull/50](https\://github\.com/ansible\-community/antsibull\-core/pull/50)\)\.
* The <code>antsibull\_core\.compat</code> module deprecates the <code>metadata</code> module\. Use <code>importlib\.metadata</code> instead\, which is available from Python 3\.8 on \([https\://github\.com/ansible\-community/antsibull\-core/pull/16](https\://github\.com/ansible\-community/antsibull\-core/pull/16)\)\.
* The <code>antsibull\_core\.compat</code> module deprecates the functions <code>asyncio\_run</code>\, <code>best\_get\_loop</code>\, and <code>create\_task</code>\. Replace <code>asyncio\_run</code> with <code>asyncio\.run</code>\, <code>create\_task</code> with <code>asyncio\.create\_task</code>\, and <code>best\_get\_loop</code> with <code>asyncio\.get\_running\_loop</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/16](https\://github\.com/ansible\-community/antsibull\-core/pull/16)\)\.
* The <code>doc\_parsing\_backend</code> option from the library context is deprecated and will be removed in antsibull\-core 3\.0\.0\. Applications that need it\, such as antsibull\-docs\, must ensure they allow and validate this option themselves \([https\://github\.com/ansible\-community/antsibull\-core/pull/59](https\://github\.com/ansible\-community/antsibull\-core/pull/59)\)\.
* The fields <code>ansible\_base\_url</code>\, <code>galaxy\_url</code>\, and <code>pypi\_url</code> of the app context have been deprecated\. Use the fields <code>ansible\_core\_repo\_url</code>\, <code>galaxy\_url</code>\, and <code>pypi\_url</code>\, respectively\, of the library context instead \([https\://github\.com/ansible\-community/antsibull\-core/pull/81](https\://github\.com/ansible\-community/antsibull\-core/pull/81)\)\.

<a id="removed-features-previously-deprecated-1"></a>
### Removed Features \(previously deprecated\)

* The unused <code>antsibull\_core\.schemas\.config\.ConfigModel</code> model and the unused <code>antsibull\_core\.config\.read\_config</code> function have been removed \([https\://github\.com/ansible\-community/antsibull\-core/pull/82](https\://github\.com/ansible\-community/antsibull\-core/pull/82)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* Fix a bug in Galaxy download code when the filename is found in the cache\, but the checksum does not match\. In that case\, the collection was not copied to the destination\, and the code did not try to download the correct file \([https\://github\.com/ansible\-community/antsibull\-core/pull/76](https\://github\.com/ansible\-community/antsibull\-core/pull/76)\)\.
* Remove improper usage of <code>\@functools\.cache</code> on async functions in the <code>antsibull\_core\.ansible\_core</code> module \([https\://github\.com/ansible\-community/antsibull\-core/pull/67](https\://github\.com/ansible\-community/antsibull\-core/pull/67)\)\.
* Restrict the <code>pydantic</code> dependency to major version 1 \([https\://github\.com/ansible\-community/antsibull\-core/pull/35](https\://github\.com/ansible\-community/antsibull\-core/pull/35)\)\.
* Restrict the <code>sh</code> dependency to versions before 2\.0\.0 \([https\://github\.com/ansible\-community/antsibull\-core/pull/31](https\://github\.com/ansible\-community/antsibull\-core/pull/31)\)\.

<a id="v1-4-0"></a>
## v1\.4\.0

<a id="release-summary-9"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-6"></a>
### Minor Changes

* Fix overly restrictive file name type annotations\. Use <code>StrOrBytesPath</code> type annotation instead of <code>str</code> for functions that accept a file name \([https\://github\.com/ansible\-community/antsibull\-core/pull/14](https\://github\.com/ansible\-community/antsibull\-core/pull/14)\)\.

<a id="bugfixes-6"></a>
### Bugfixes

* Remove use of blocking IO in an async function \([https\://github\.com/ansible\-community/antsibull\-core/pull/13/](https\://github\.com/ansible\-community/antsibull\-core/pull/13/)\)\.

<a id="v1-3-1"></a>
## v1\.3\.1

<a id="release-summary-10"></a>
### Release Summary

Maintenance release to fix unwanted <code>1\.3\.0\.post0</code> release\.

<a id="v1-3-0-post0"></a>
## v1\.3\.0\.post0

<a id="release-summary-11"></a>
### Release Summary

Erroneously released version\.

<a id="v1-3-0"></a>
## v1\.3\.0

<a id="release-summary-12"></a>
### Release Summary

Feature and bugfix release\.

<a id="minor-changes-7"></a>
### Minor Changes

* Allow to write Python dependencies as <code>\_python</code> key into build and dependency files \([https\://github\.com/ansible\-community/antsibull\-core/pull/10](https\://github\.com/ansible\-community/antsibull\-core/pull/10)\)\.

<a id="bugfixes-7"></a>
### Bugfixes

* Fix async file copying helper \([https\://github\.com/ansible\-community/antsibull\-core/pull/11](https\://github\.com/ansible\-community/antsibull\-core/pull/11)\)\.

<a id="v1-2-0"></a>
## v1\.2\.0

<a id="release-summary-13"></a>
### Release Summary

Feature release\.

<a id="minor-changes-8"></a>
### Minor Changes

* Improve typing \([https\://github\.com/ansible\-community/antsibull\-core/pull/6](https\://github\.com/ansible\-community/antsibull\-core/pull/6)\)\.
* Make config file management more flexible to allow project\-specific config file format extensions for the explicitly passed configuration files \([https\://github\.com/ansible\-community/antsibull\-core/pull/7](https\://github\.com/ansible\-community/antsibull\-core/pull/7)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* The <code>DepsFile\.write\(\)</code> method will require the first parameter to be a <code>packaging\.version\.Version</code> object\, the second parameter to be a string\, and the third parameter a mapping of strings to strings\, from antsibull\-core 2\.0\.0 on \([https\://github\.com/ansible\-community/antsibull\-core/pull/6](https\://github\.com/ansible\-community/antsibull\-core/pull/6)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* Adjust signature of <code>DepsFile\.write\(\)</code> to work around bug in antsibull \([https\://github\.com/ansible\-community/antsibull\-core/pull/6](https\://github\.com/ansible\-community/antsibull\-core/pull/6)\)\.

<a id="v1-1-0"></a>
## v1\.1\.0

<a id="release-summary-14"></a>
### Release Summary

Maintenance release\.

<a id="minor-changes-9"></a>
### Minor Changes

* The files in the source repository now follow the [REUSE Specification](https\://reuse\.software/spec/)\. The only exceptions are changelog fragments in <code>changelogs/fragments/</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/5](https\://github\.com/ansible\-community/antsibull\-core/pull/5)\)\.

<a id="v1-0-1"></a>
## v1\.0\.1

<a id="release-summary-15"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-9"></a>
### Bugfixes

* Fix detection of ansible\-core devel checkouts \([https\://github\.com/ansible\-community/antsibull\-core/pull/4](https\://github\.com/ansible\-community/antsibull\-core/pull/4)\)\.

<a id="v1-0-0"></a>
## v1\.0\.0

<a id="release-summary-16"></a>
### Release Summary

First stable release\.

<a id="major-changes"></a>
### Major Changes

* From version 1\.0\.0 on\, antsibull\-core is sticking to semantic versioning and aims at providing no backwards compatibility breaking changes during a major release cycle \([https\://github\.com/ansible\-community/antsibull\-core/pull/2](https\://github\.com/ansible\-community/antsibull\-core/pull/2)\)\.

<a id="minor-changes-10"></a>
### Minor Changes

* Remove unused code \([https\://github\.com/ansible\-community/antsibull\-core/pull/1](https\://github\.com/ansible\-community/antsibull\-core/pull/1)\)\.

<a id="removed-features-previously-deprecated-2"></a>
### Removed Features \(previously deprecated\)

* Remove package <code>antsibull\_core\.utils\.transformations</code> \([https\://github\.com/ansible\-community/antsibull\-core/pull/1](https\://github\.com/ansible\-community/antsibull\-core/pull/1)\)\.

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="release-summary-17"></a>
### Release Summary

Initial release\.
