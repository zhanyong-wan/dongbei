#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei

Expression = dongbei.Expression
Statement = dongbei.Statement
Token = dongbei.Token

class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(dongbei.Run(''), '')

  def testRunHelloWorld(self):
    self.assertEqual(
        dongbei.Run(u'唠唠：“这旮旯儿嗷嗷美好哇！”。'),
        u'这旮旯儿嗷嗷美好哇！\n')

  def testRunHelloWorld2(self):
    self.assertEqual(
        dongbei.Run(u'唠唠：“你那旮旯儿也挺美好哇！”。'),
        u'你那旮旯儿也挺美好哇！\n')

  def testVarDecl(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。'), '')

  def testVarAssignment(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。\n老张装250。\n唠唠：老张。'), '250\n')

  def testTokenize(self):
    self.assertEqual(
        list(dongbei.BasicTokenize(u'【阶乘】')),
        [Token(dongbei.TK_IDENTIFIER, u'阶乘'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'【阶乘】（几）')),
        [Token(dongbei.TK_IDENTIFIER, u'阶乘'),
         Token(dongbei.TK_KEYWORD, u'（'),
         Token(dongbei.TK_CHAR, u'几'),
         Token(dongbei.TK_KEYWORD, u'）'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“ ”')),
        [Token(dongbei.TK_KEYWORD, u'“'),
         Token(dongbei.TK_STRING_LITERAL, u' '),
         Token(dongbei.TK_KEYWORD, u'”'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“”')),
        [Token(dongbei.TK_KEYWORD, u'“'),
         Token(dongbei.TK_STRING_LITERAL, u''),
         Token(dongbei.TK_KEYWORD, u'”'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“ A B ”')),
        [Token(dongbei.TK_KEYWORD, u'“'),
         Token(dongbei.TK_STRING_LITERAL, u' A B '),
         Token(dongbei.TK_KEYWORD, u'”'),])
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
        list(dongbei.Tokenize(u'唠唠：“你好”。')),
        [Token(dongbei.TK_KEYWORD, u'唠唠'),
         Token(dongbei.TK_KEYWORD, u'：'),
         Token(dongbei.TK_KEYWORD, u'“'),
         Token(dongbei.TK_STRING_LITERAL, u'你好'),
         Token(dongbei.TK_KEYWORD, u'”'),
         Token(dongbei.TK_KEYWORD, u'。')])

  def testTokenizeArithmetic(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'250加13减二乘五除以九')),
        [Token(dongbei.TK_INTEGER_LITERAL, 250),
         Token(dongbei.TK_KEYWORD, u'加'),
         Token(dongbei.TK_INTEGER_LITERAL, 13),
         Token(dongbei.TK_KEYWORD, u'减'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),
         Token(dongbei.TK_KEYWORD, u'乘'),
         Token(dongbei.TK_INTEGER_LITERAL, 5),
         Token(dongbei.TK_KEYWORD, u'除以'),
         Token(dongbei.TK_INTEGER_LITERAL, 9),
        ])
    
  def testTokenizeLoop(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王从1到9磨叽：磨叽完了。')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         Token(dongbei.TK_KEYWORD, u'从'),
         Token(dongbei.TK_INTEGER_LITERAL, 1),
         Token(dongbei.TK_KEYWORD, u'到'),
         Token(dongbei.TK_INTEGER_LITERAL, 9),
         Token(dongbei.TK_KEYWORD, u'磨叽：'),
         Token(dongbei.TK_KEYWORD, u'磨叽完了。'),
        ])

  def testTokenizeCompound(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'开整了：\n  唠唠：老王。\n整完了。')),
        [Token(dongbei.TK_KEYWORD, u'开整了：'),
         Token(dongbei.TK_KEYWORD, u'唠唠'),
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

  def testTokenizingConcat(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老刘还有二')),
        [Token(dongbei.TK_IDENTIFIER, u'老刘'),
         Token(dongbei.TK_KEYWORD, u'还有'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),])

  def testTokenizingFuncDef(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'写九九表咋整：整完了。')),
        [Token(dongbei.TK_IDENTIFIER, u'写九九表'),
         Token(dongbei.TK_KEYWORD, u'咋整：'),
         Token(dongbei.TK_KEYWORD, u'整完了。'),])

  def testTokenizingFuncCall(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'整写九九表')),
        [Token(dongbei.TK_KEYWORD, u'整'),
         Token(dongbei.TK_IDENTIFIER, u'写九九表'),])
    
  def testParsingIncrements(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王走走。'),
        [Statement(
            dongbei.STMT_INC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        dongbei.ParseToAst(u'老王走两步。'),
        [Statement(
            dongbei.STMT_INC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 2)])))])

  def testParsingDecrements(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王退退。'),
        [Statement(
            dongbei.STMT_DEC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        dongbei.ParseToAst(u'老王退三步。'),
        [Statement(
            dongbei.STMT_DEC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 3)])))])

  def testParsingArithmetic(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王装250加13减二乘五除以六。'),
        [Statement(
            dongbei.STMT_ASSIGN,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([
                 Token(dongbei.TK_INTEGER_LITERAL, 250),
                 Token(dongbei.TK_KEYWORD, u'加'),
                 Token(dongbei.TK_INTEGER_LITERAL, 13),
                 Token(dongbei.TK_KEYWORD, u'减'),
                 Token(dongbei.TK_INTEGER_LITERAL, 2),
                 Token(dongbei.TK_KEYWORD, u'乘'),
                 Token(dongbei.TK_INTEGER_LITERAL, 5),
                 Token(dongbei.TK_KEYWORD, u'除以'),
                 Token(dongbei.TK_INTEGER_LITERAL, 6),
             ])))])
    
  def testParsingLoop(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王从1到9磨叽：磨叽完了。'),
        [Statement(
            dongbei.STMT_LOOP,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 1)]),
             Expression([Token(dongbei.TK_INTEGER_LITERAL, 9)]),
             []))])

  def testParsingFuncDef(self):
    self.assertEqual(
        dongbei.ParseToAst(u'写九九表咋整：整完了。'),
        [Statement(dongbei.STMT_FUNC_DEF,
                   (Token(dongbei.TK_IDENTIFIER, u'写九九表'),
                    [],  # Formal parameters.
                    []  # Function body.
                   ))])
    self.assertEqual(
        dongbei.ParseToAst(u'写九九表咋整：唠唠：1。整完了。'),
        [Statement(dongbei.STMT_FUNC_DEF,
                   (Token(dongbei.TK_IDENTIFIER, u'写九九表'),
                    [],  # Formal parameters.
                    # Function body.
                    [Statement(dongbei.STMT_SAY,
                               Expression([Token(
                                   dongbei.TK_INTEGER_LITERAL, 1)]))]
                   ))])
    
  def testParsingFuncDefWithParam(self):
    self.assertEqual(
        dongbei.ParseToAst(u'【阶乘】（几）咋整：整完了。'),
        [Statement(dongbei.STMT_FUNC_DEF,
                   (Token(dongbei.TK_IDENTIFIER, u'阶乘'),
                    [Token(dongbei.TK_IDENTIFIER, u'几')],  # Formal parameters.
                    []  # Function body.
                   ))])
    
  def testParsingFuncCallWithParam(self):
    self.assertEqual(
        dongbei.ParseToAst(u'整【阶乘】（五）。'),
        [Statement(dongbei.STMT_CALL,
                   (Token(dongbei.TK_IDENTIFIER, u'阶乘'),
                    [Expression([Token(dongbei.TK_INTEGER_LITERAL, 5)])]))])

  def testVarAssignmentFromVar(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。\n老王是活雷锋。\n'
                    u'老张装250。\n老王装老张。\n唠唠：老王。'), '250\n')

  def testIncrements(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。老张装二。老张走走。唠唠：老张。'),
        '3\n')
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。老张装三。老张走五步。唠唠：老张。'),
        '8\n')

  def testDecrements(self):
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。老张装二。老张退退。唠唠：老张。'),
        '1\n')
    self.assertEqual(
        dongbei.Run(u'老张是活雷锋。老张装三。老张退五步。唠唠：老张。'),
        '-2\n')

  def testLoop(self):
    self.assertEqual(
        dongbei.Run(u'老张从1到3磨叽：唠唠：老张。磨叽完了。'),
        '1\n2\n3\n')

  def testConcat(self):
    self.assertEqual(
        dongbei.Run(u'唠唠：“牛”还有二。'),
        u'牛2\n')

  def testRunFunc(self):
    self.assertEqual(
        dongbei.Run(u'埋汰咋整：唠唠：“你虎了吧唧”。整完了。'),
        u'')
    self.assertEqual(
        dongbei.Run(u'埋汰咋整：唠唠：“你虎了吧唧”。整完了。整埋汰。'),
        u'你虎了吧唧\n')

  def testFuncCallWithParam(self):
    self.assertEqual(
        dongbei.Run(u'【加一】（几）咋整：唠唠：几加一。整完了。\n'
                    u'整【加一】（五）。'),
        u'6\n')
    
if __name__ == '__main__':
  unittest.main()
