#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei

class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(dongbei.Run(''), '')

  def testRunHelloWorld(self):
    self.assertEqual(
        dongbei.Run(u'唠：“这嘎哒嗷嗷美好哇！”'),
        u'这嘎哒嗷嗷美好哇！\n')

  def testRunHelloWorld2(self):
    self.assertEqual(
        dongbei.Run(u'唠：“你那嘎哒也挺美好哇！”'),
        u'你那嘎哒也挺美好哇！\n')

  def testVarDecl(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。'), '')

  def testVarAssignment(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。\n老张装250。'), '250')

if __name__ == '__main__':
  unittest.main()
