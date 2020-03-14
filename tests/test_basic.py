#!/usr/bin/env python

from __future__ import print_function

import unittest

# The purpose is to test survol and import it as an external package.
class SurvolSimpleTest(unittest.TestCase):
    """
    Testing import.
    """

    def test_simple_import(self):
        import survol

if __name__ == '__main__':
    unittest.main()

