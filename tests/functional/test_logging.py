# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

import os

import pytest

import twiggy.levels

import antsibull_core.logging as al


def test_library_settings(capsys):
    """Importing without calling initialize_app_logging leaves logging disabled."""
    assert al.log.min_level == twiggy.levels.DISABLED

    al.log.error('test')
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''


def test_initialize_app_logging(capsys):
    """Calling initialize_app_logging outputs WARNING and above to stderr."""
    al.initialize_app_logging()

    al.log.error('test')
    al.log.warning('second test')
    al.log.debug('third test')
    captured = capsys.readouterr()
    assert captured.err == 'ERROR:antsibull|test\nWARNING:antsibull|second test\n'
    assert captured.out == ''


def test_initialize_app_logging_debug(capsys):
    os.environ['ANTSIBULL_EARLY_DEBUG'] = '1'
    al.initialize_app_logging()

    al.log.error('test')
    al.log.warning('second test')
    al.log.debug('third test')
    captured = capsys.readouterr()
    assert captured.err == 'ERROR:antsibull|test\nWARNING:antsibull|second test\nDEBUG:antsibull|third test\n'
    assert captured.out == ''
