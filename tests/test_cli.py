#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys

import pytest

from pyscaffold import cli
from pyscaffold.exceptions import OldSetuptools

from .log_helpers import find_report

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def test_parse_args():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts['project'] == "my-project"


def test_parse_args_with_old_setuptools(old_setuptools_mock):  # noqa
    args = ["my-project"]
    with pytest.raises(OldSetuptools):
        cli.parse_args(args)


def test_parse_quiet_option():
    for quiet in ("--quiet", "-q"):
        args = ["my-project", quiet]
        opts = cli.parse_args(args)
        assert opts["log_level"] == logging.CRITICAL


def test_parse_default_log_level():
    args = ["my-project"]
    opts = cli.parse_args(args)
    assert opts["log_level"] == logging.INFO


def test_parse_pretend():
    for flag in ["--pretend", "--dry-run"]:
        opts = cli.parse_args(["my-project", flag])
        assert opts["pretend"]
    opts = cli.parse_args(["my-project"])
    assert not opts["pretend"]


def test_main(tmpfolder, git_mock, caplog):  # noqa
    args = ["my-project"]
    cli.main(args)
    assert os.path.exists(args[0])

    # Check for some log messages
    assert find_report(caplog, 'invoke', 'get_default_options')
    assert find_report(caplog, 'invoke', 'verify_options_consistency')
    assert find_report(caplog, 'invoke', 'define_structure')
    assert find_report(caplog, 'invoke', 'create_structure')
    assert find_report(caplog, 'create', 'setup.py')
    assert find_report(caplog, 'create', 'requirements.txt')
    assert find_report(caplog, 'create', 'my_project/__init__.py')
    assert find_report(caplog, 'run', 'git init')
    assert find_report(caplog, 'run', 'git add')


def test_pretend_main(tmpfolder, git_mock, caplog):  # noqa
    for flag in ["--pretend", "--dry-run"]:
        args = ["my-project", flag]
        cli.main(args)
        assert not os.path.exists(args[0])

        # Check for some log messages
        assert find_report(caplog, 'invoke', 'get_default_options')
        assert find_report(caplog, 'invoke', 'verify_options_consistency')
        assert find_report(caplog, 'invoke', 'define_structure')
        assert find_report(caplog, 'invoke', 'create_structure')
        assert find_report(caplog, 'create', 'setup.py')
        assert find_report(caplog, 'create', 'requirements.txt')
        assert find_report(caplog, 'create', 'my_project/__init__.py')
        assert find_report(caplog, 'run', 'git init')
        assert find_report(caplog, 'run', 'git add')


def test_main_when_updating(tmpfolder, capsys, git_mock):  # noqa
    args = ["my-project"]
    cli.main(args)
    args = ["--update", "my-project"]
    cli.main(args)
    assert os.path.exists(args[1])
    out, _ = capsys.readouterr()
    assert "Update accomplished!" in out


def test_run(tmpfolder, git_mock):  # noqa
    sys.argv = ["pyscaffold", "my-project"]
    cli.run()
    assert os.path.exists(sys.argv[1])
