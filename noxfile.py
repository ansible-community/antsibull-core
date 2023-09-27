# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 Maxwell G <maxwell@gtmx.me>

import contextlib
import os
import tempfile
from pathlib import Path

import nox

IN_CI = "GITHUB_ACTIONS" in os.environ
ALLOW_EDITABLE = os.environ.get("ALLOW_EDITABLE", str(not IN_CI)).lower() in (
    "1",
    "true",
)

# Always install latest pip version
os.environ["VIRTUALENV_DOWNLOAD"] = "1"
nox.options.sessions = "lint", "test", "coverage"


def install(session: nox.Session, *args, editable=False, **kwargs):
    # nox --no-venv
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn(f"No venv. Skipping installation of {args}")
        return
    # Don't install in editable mode in CI or if it's explicitly disabled.
    # This ensures that the wheel contains all of the correct files.
    if editable and ALLOW_EDITABLE:
        args = ("-e", *args)
    # TODO: Remove this once aiohttp's extension module supports Python 3.12
    if session.python == "3.12":
        kwargs.setdefault("env", {})["AIOHTTP_NO_EXTENSIONS"] = "1"

    session.install(*args, "-U", **kwargs)


@nox.session(python=["3.9", "3.10", "3.11", "3.12"])
def test(session: nox.Session):
    install(
        session,
        ".[test, coverage]",
        editable=True,
    )
    covfile = Path(session.create_tmp(), ".coverage")
    more_args = []
    if session.python == "3.12":
        more_args.append("--error-for-skips")
    session.run(
        "pytest",
        "--cov-branch",
        "--cov=antsibull_core",
        "--cov-report",
        "term-missing",
        *more_args,
        *session.posargs,
        env={"COVERAGE_FILE": f"{covfile}", **session.env},
    )


@nox.session
def coverage(session: nox.Session):
    install(session, ".[coverage]", editable=True)
    combined = map(str, Path().glob(".nox/*/tmp/.coverage"))
    # Combine the results into a single .coverage file in the root
    session.run("coverage", "combine", "--keep", *combined)
    # Create a coverage.xml for codecov
    session.run("coverage", "xml")
    # Display the combined results to the user
    session.run("coverage", "report", "-m")


@nox.session
def lint(session: nox.Session):
    session.notify("formatters")
    session.notify("codeqa")
    session.notify("typing")


@nox.session
def formatters(session: nox.Session):
    install(session, ".[formatters]")
    posargs = list(session.posargs)
    if IN_CI:
        posargs.append("--check")
    session.run("isort", *posargs, "src", "tests", "noxfile.py")
    session.run("black", *posargs, "src", "tests", "noxfile.py")


@nox.session
def codeqa(session: nox.Session):
    install(session, ".[codeqa]", editable=True)
    session.run("flake8", "src", *session.posargs)
    session.run("pylint", "--rcfile", ".pylintrc.automated", "src/antsibull_core")
    session.run("reuse", "lint")
    session.run("antsibull-changelog", "lint")


@nox.session
def typing(session: nox.Session):
    # pyre does not work when we don't install ourself in editable mode 🙄.
    install(session, "-e", ".[typing]")
    session.run("mypy", "src/antsibull_core")

    purelib = session.run(
        "python",
        "-c",
        "import sysconfig; print(sysconfig.get_path('purelib'))",
        silent=True,
    ).strip()
    platlib = session.run(
        "python",
        "-c",
        "import sysconfig; print(sysconfig.get_path('platlib'))",
        silent=True,
    ).strip()
    session.run(
        "pyre",
        "--source-directory",
        "src",
        "--search-path",
        purelib,
        "--search-path",
        platlib,
        "--search-path",
        "stubs/",
    )


def check_no_modifications(session: nox.Session) -> None:
    modified = session.run(
        "git",
        "status",
        "--porcelain=v1",
        "--untracked=normal",
        external=True,
        silent=True,
    )
    if modified:
        session.error(
            "There are modified or untracked files. "
            "Commit, restore, or remove them before running this"
        )


@contextlib.contextmanager
def isolated_src(session: nox.Session):
    """
    Create an isolated directory that only contains the latest git HEAD
    """
    with tempfile.TemporaryDirectory() as _tmpdir:
        tmp = Path(_tmpdir)
        session.run(
            "git",
            "archive",
            "HEAD",
            f"--output={tmp / 'HEAD.tar'}",
            "--prefix=build/",
            external=True,
        )
        with session.chdir(tmp):
            session.run("tar", "-xf", "HEAD.tar", external=True)
        with session.chdir(tmp / "build"):
            yield


@nox.session
def bump(session: nox.Session):
    check_no_modifications(session)
    if len(session.posargs) not in (1, 2):
        session.error(
            "Must specify 1-2 positional arguments: nox -e bump -- <version> "
            "[ <release_summary_message> ]."
            " If release_summary_message has not been specified, "
            "a file changelogs/fragments/<version>.yml must exist"
        )
    version = session.posargs[0]
    fragment_file = Path(f"changelogs/fragments/{version}.yml")
    if len(session.posargs) == 1:
        if not fragment_file.is_file():
            session.error(
                f"Either {fragment_file} must already exist, "
                "or two positional arguments must be provided."
            )
    install(session, "antsibull-changelog[toml]", "hatch")
    current_version = session.run("hatch", "version", silent=True).strip()
    if version != current_version:
        session.run("hatch", "version", version)
    if len(session.posargs) > 1:
        fragment = session.run(
            "python",
            "-c",
            "import yaml ; "
            f"print(yaml.dump(dict(release_summary={repr(session.posargs[1])})))",
            silent=True,
        )
        with open(fragment_file, "w") as fp:
            print(fragment, file=fp)
        session.run("git", "add", "pyproject.toml", str(fragment_file), external=True)
        session.run("git", "commit", "-m", f"Prepare {version}.", external=True)
    session.run("antsibull-changelog", "release")
    session.run(
        "git",
        "add",
        "CHANGELOG.rst",
        "changelogs/changelog.yaml",
        "changelogs/fragments/",
        # pyproject.toml is not committed in the last step
        # when the release_summary fragment is created manually
        "pyproject.toml",
        external=True,
    )
    install(session, ".")  # Smoke test
    session.run("git", "commit", "-m", f"Release {version}.", external=True)
    session.run(
        "git",
        "tag",
        "-a",
        "-m",
        f"antsibull-core {version}",
        "--edit",
        version,
        external=True,
    )
    dist = Path.cwd() / "dist"
    with isolated_src(session):
        session.run("hatch", "build", "--clean", str(dist))


@nox.session
def publish(session: nox.Session):
    check_no_modifications(session)
    install(session, "hatch")
    session.run("hatch", "publish", *session.posargs)
    session.run("hatch", "version", "post")
    session.run("git", "add", "pyproject.toml", external=True)
    session.run("git", "commit", "-m", "Post-release version bump.", external=True)
