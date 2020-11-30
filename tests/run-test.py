#!/usr/bin/env python

import sys

import pytest


def run_all(argv=None):
    # always insert coverage when running tests through setup.py
    if argv is None:
        argv = [
            '--cov', 'fiqs', '--verbose',
            '--junitxml', 'junit.xml', '--cov-report', 'xml',
            '-m', 'not docker and not performance',
        ]
    else:
        argv = argv[1:]

    sys.exit(pytest.main(argv))


if __name__ == '__main__':
    run_all(sys.argv)