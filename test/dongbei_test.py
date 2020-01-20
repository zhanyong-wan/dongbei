#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei

Token = dongbei.Token

class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(dongbei.Run(''), '')

  def testRunHelloWorld(self):
    self.assertEqual(
        dongbei.Run(u'唠：“这嘎哒嗷嗷美好哇！”。'),
        u'这嘎哒嗷嗷美好哇！\n')

  def testRunHelloWorld2(self):
    self.assertEqual(
        dongbei.Run(u'唠：“你那嘎哒也挺美好哇！”。'),
        u'你那嘎哒也挺美好哇！\n')

  def testVarDecl(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。'), '')

  def testVarAssignment(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。\n老张装250。\n唠：老张。'), '250\n')

  def testTokenize(self):
    self.assertEqual(
        list(dongbei.BasicTokenize(u'老张')),
        [Token(dongbei.TK_CHAR, u'老'),
         Token(dongbei.TK_CHAR, u'张'),])
    self.assertEqual(
        list(dongbei.Tokenize(u'# 123456\n老张')),
        [Token(dongbei.TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张')),
        [Token(dongbei.TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        dongbei.ParseInteger(u'老张'),
        (None, u'老张'))
    self.assertEqual(
        list(dongbei.ParseChars(u'老张')),
        [Token(dongbei.TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张是活雷锋')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         Token(dongbei.TK_KEYWORD, u'是活雷锋')])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张是活雷锋。\n老王是活雷锋。\n')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         Token(dongbei.TK_KEYWORD, u'是活雷锋'),
         Token(dongbei.TK_KEYWORD, u'。'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'是活雷锋'),
         Token(dongbei.TK_KEYWORD, u'。'),
        ])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张装250。\n老王装老张。\n')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         Token(dongbei.TK_KEYWORD, u'装'),
         Token(dongbei.TK_INTEGER_LITERAL, 250),
         Token(dongbei.TK_KEYWORD, u'。'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'装'),
         Token(dongbei.TK_IDENTIFIER, u'老张'),
         Token(dongbei.TK_KEYWORD, u'。')])
    self.assertEqual(
        list(dongbei.Tokenize(u'唠：“你好”。')),
        [Token(dongbei.TK_KEYWORD, u'唠'),
         Token(dongbei.TK_KEYWORD, u'：'),
         Token(dongbei.TK_KEYWORD, u'“'),
         Token(dongbei.TK_STRING_LITERAL, u'你好'),
         Token(dongbei.TK_KEYWORD, u'”'),
         Token(dongbei.TK_KEYWORD, u'。')])

  def testTokenizeLoop(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王从1到9磨叽：')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'从'),
         Token(dongbei.TK_INTEGER_LITERAL, 1),
         Token(dongbei.TK_KEYWORD, u'到'),
         Token(dongbei.TK_INTEGER_LITERAL, 9),
         Token(dongbei.TK_KEYWORD, u'磨叽：')])

  def testTokenizeCompound(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'开整了：\n  唠：老王。\n整完了。')),
        [Token(dongbei.TK_KEYWORD, u'开整了：'),
         Token(dongbei.TK_KEYWORD, u'唠'),
         Token(dongbei.TK_KEYWORD, u'：'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'。'),
         Token(dongbei.TK_KEYWORD, u'整完了。'),])

  def testTokenizingIncrements(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王走走')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'走走'),])
    self.assertEqual(
        list(dongbei.Tokenize(u'老王走两步')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'走'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),
         Token(dongbei.TK_KEYWORD, u'步'),
        ])

  def testTokenizingDecrements(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王退退')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'退退'),])
    self.assertEqual(
        list(dongbei.Tokenize(u'老王退三步')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'退'),
         Token(dongbei.TK_INTEGER_LITERAL, 3),
         Token(dongbei.TK_KEYWORD, u'步'),
        ])
    
  def testVarAssignmentFromVar(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。\n老王是活雷锋。\n'
                    u'老张装250。\n老王装老张。\n唠：老王。'), '250\n')

if __name__ == '__main__':
  unittest.main()
