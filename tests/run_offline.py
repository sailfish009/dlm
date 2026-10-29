#!/usr/bin/env python3
"""Run native Python tests without network; exclude legacy loopback HTTP suite.

Socket creation/use is guarded in this Python process. Tested child drivers are
native/file/PTY-only. This is a test runner, not an OS network sandbox.
"""
from pathlib import Path
import socket
import sys
import unittest


def deny_network(*args, **kwargs):
    raise AssertionError('network access is disabled in the offline test runner')


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main():
    socket.create_connection = deny_network
    socket.getaddrinfo = deny_network
    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.socket.bind = deny_network
    directory = Path(__file__).resolve().parent
    all_cases = list(cases(unittest.defaultTestLoader.discover(str(directory), pattern='test_*.py')))
    excluded = [test for test in all_cases if test.id().startswith('test_web.')]
    selected = [test for test in all_cases if not test.id().startswith('test_web.')]
    print(f'OFFLINE: {len(selected)} tests; {len(excluded)} legacy local-HTTP tests excluded', flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
