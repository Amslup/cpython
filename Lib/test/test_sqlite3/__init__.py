import test.support
from test.support import import_helper
from test.support import load_package_tests

# Skip test if _sqlite3 module not installed
import_helper.import_module('_sqlite3')

import unittest
import os
import sqlite3

def load_tests(*args):
    pkg_dir = os.path.dirname(__file__)
    return load_package_tests(pkg_dir, *args)

if test.support.verbose:
    print("test_sqlite3: testing with version",
          "{!r}, sqlite_version {!r}".format(sqlite3.version,
                                             sqlite3.sqlite_version))
