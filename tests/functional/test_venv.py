# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)

import os.path
import sys
from unittest import mock

import pytest

from antsibull_core import subprocess_util
from antsibull_core.venv import FakeVenvRunner, VenvRunner, get_clean_environment


def test_venv_clean_env(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "/jfjfjfjfjfjfjfjfj")
    assert "PYTHONPATH" not in get_clean_environment()


def test_venv_run_init(tmp_path):
    with mock.patch("antsibull_core.subprocess_util.async_log_run") as log_run:
        runner = VenvRunner("asdfgh", tmp_path)
        assert runner.name == "asdfgh"
        assert runner.top_dir == tmp_path
        assert runner.venv_dir == str(tmp_path / "asdfgh")
        pip = os.path.join(runner.venv_dir, "bin", "pip")
        log_run.assert_called_once_with(
            [pip, "install", "--upgrade", "pip"],
            None,
            None,
            "debug",
            True,
            errors="strict",
            env=get_clean_environment(),
        )


def test_venv_log_run_error(tmp_path):
    runner = VenvRunner("zxcvb", tmp_path)
    echo = os.path.join(runner.venv_dir, "bin", "echo")
    with pytest.raises(ValueError, match=rf"^{echo!r} does not exist!"):
        runner.log_run(["echo", "This won't work!"])


def test_venv_log_run_error2(tmp_path):
    runner = VenvRunner("zxcvb", tmp_path)
    echo = "/usr/bin/echo"
    with pytest.raises(ValueError, match=rf"^{echo!r} must not be an absolute path!"):
        runner.log_run([echo, "This also won't work!"])


def test_fake_venv_python():
    with mock.patch.object(
        subprocess_util, "async_log_run", wraps=subprocess_util.async_log_run
    ) as log_run:
        args = ["python", "-c", 'import antsibull_core; print("Hello, world!")']
        p = FakeVenvRunner().log_run(args)
        assert p.stdout == "Hello, world!\n"

        args = args.copy()
        args[0] = sys.executable
        log_run.assert_called_once_with(
            args,
            None,
            None,
            "debug",
            True,
            errors="strict",
        )
