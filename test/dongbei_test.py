#!/usr/bin/python

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei

class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(dongbei.Run(''), '')

if __name__ == '__main__':
  unittest.main()
