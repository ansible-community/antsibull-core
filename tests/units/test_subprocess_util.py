# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)

import logging as stdlog
from unittest.mock import MagicMock, call

import pytest
import twiggy

import antsibull_core.subprocess_util
from antsibull_core import logging


def test_log_run() -> None:
    logger = MagicMock()
    args = ("bash", "-ec", "echo 123 && echo 456 >&2")
    proc = antsibull_core.subprocess_util.log_run(args, logger)
    assert proc.args == args
    assert proc.returncode == 0
    assert proc.stdout == "123\n"
    assert proc.stderr == "456\n"
    calls = [call(f"Running subprocess: {args}"), call("stderr: 456")]
    assert logger.debug.call_args_list == calls


def test_log_run_multi() -> None:
    logger = MagicMock()
    command = """
    for i in {1..15}; do
        echo "$i: Hello, stdout"
        echo "$i: Hello, stderr" >&2
    done
    """
    args = ("bash", "-ec", command)
    proc = antsibull_core.subprocess_util.log_run(args, logger, "info", "warn")
    assert proc.args == args
    assert proc.returncode == 0

    logger.debug.assert_called_once_with(f"Running subprocess: {args}")
    assert logger.warn.call_count == 15
    assert logger.info.call_count == 15
    expected_out: list[str] = []
    expected_err: list[str] = []
    for index, inp in enumerate(logger.info.call_args_list):
        msg = f"{index+1}: Hello, stdout"
        expected_out.append(msg)
        assert inp == call("stdout: " + msg)
    for index, inp in enumerate(logger.warn.call_args_list):
        msg = f"{index+1}: Hello, stderr"
        expected_err.append(msg)
        assert inp == call("stderr: " + msg)
    assert proc.stdout == "\n".join(expected_out) + "\n"
    assert proc.stderr == "\n".join(expected_err) + "\n"


@pytest.mark.parametrize(
    "count",
    [
        8 * 1024 * 1024 - 1,  # should not trigger long line code
        8 * 1024 * 1024,  # should not trigger long line code
        8 * 1024 * 1024 + 1,
        8 * 1024 * 1024 + 10,
        9 * 1024 * 1024,
    ],
)
def test_log_run_long_line(count: int) -> None:
    args = (
        "sh",
        "-c",
        f"dd if=/dev/zero of=/dev/stdout bs={count} count=1 ; echo ; echo foo",
    )
    proc = antsibull_core.subprocess_util.log_run(args)
    assert proc.args == args
    assert proc.returncode == 0
    assert proc.stdout == ("\u0000" * count) + "\nfoo\n"


def test_log_run_callback() -> None:
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    async def add_to_stderr(string: str, /) -> None:
        stderr_lines.append(string)

    antsibull_core.subprocess_util.log_run(
        ["sh", "-c", "echo Never; echo gonna >&2; echo give"],
        None,
        stdout_lines.append,
        add_to_stderr,
    )
    assert stdout_lines == ["Never", "give"]
    assert stderr_lines == ["gonna"]


def test_log_run_brackets_twiggy(capsys: pytest.CaptureFixture) -> None:
    try:
        logging.initialize_app_logging()
        msg = "{abc} {x} }{}"
        args = ("echo", msg)
        antsibull_core.subprocess_util.log_run(
            args, logger=logging.log, stdout_loglevel="error"
        )
        _, stderr = capsys.readouterr()
        assert stderr == f"ERROR:antsibull|stdout: {msg}\n"
    finally:
        logging.log.min_level = twiggy.levels.DISABLED


def test_log_run_percent_logging(capsys: pytest.CaptureFixture) -> None:
    logger = stdlog.Logger("test_logger")
    logger.setLevel(stdlog.WARNING)
    ch = stdlog.StreamHandler()
    ch.setLevel(stdlog.WARNING)
    formatter = stdlog.Formatter("%(levelname)s:%(name)s|%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    msg = "%s %(abc)s % %%"
    args = ("echo", msg)
    antsibull_core.subprocess_util.log_run(args, logger=logger, stdout_loglevel="error")
    _, stderr = capsys.readouterr()
    assert stderr == f"ERROR:test_logger|stdout: {msg}\n"
