#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei
from src.dongbei import AtomicExpr
from src.dongbei import ComparisonExpr
from src.dongbei import Expr
from src.dongbei import ParenExpr
from src.dongbei import ParseExprFromStr
from src.dongbei import Statement
from src.dongbei import Token

class DongbeiParseExprTest(unittest.TestCase):
  def testParseInteger(self):
    self.assertEqual(ParseExprFromStr(u'5')[0],
                     AtomicExpr(Token(dongbei.TK_INTEGER_LITERAL, 5)))
    self.assertEqual(ParseExprFromStr(u'九')[0],
                     AtomicExpr(Token(dongbei.TK_INTEGER_LITERAL, 9)))
    
  def testParseIdentifier(self):
    self.assertEqual(ParseExprFromStr(u'老王')[0],
                     AtomicExpr(Token(dongbei.TK_IDENTIFIER, u'老王')))

  def testParseParens(self):
    # Wide parens.
    self.assertEqual(ParseExprFromStr(u'（老王）')[0],
                     ParenExpr(
                         AtomicExpr(Token(dongbei.TK_IDENTIFIER, u'老王'))))

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
        list(dongbei.BasicTokenize(u'【 阶  乘   】')),
        [Token(dongbei.TK_IDENTIFIER, u'阶乘'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'【阶乘】（几）')),
        [Token(dongbei.TK_IDENTIFIER, u'阶乘'),
         dongbei.Keyword(u'（'),
         Token(dongbei.TK_CHAR, u'几'),
         dongbei.Keyword(u'）'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“ ”')),
        [dongbei.Keyword(u'“'),
         Token(dongbei.TK_STRING_LITERAL, u' '),
         dongbei.Keyword(u'”'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“”')),
        [dongbei.Keyword(u'“'),
         Token(dongbei.TK_STRING_LITERAL, u''),
         dongbei.Keyword(u'”'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'“ A B ”')),
        [dongbei.Keyword(u'“'),
         Token(dongbei.TK_STRING_LITERAL, u' A B '),
         dongbei.Keyword(u'”'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'老张')),
        [Token(dongbei.TK_CHAR, u'老'),
         Token(dongbei.TK_CHAR, u'张'),])
    self.assertEqual(
        list(dongbei.BasicTokenize(u'  老 张   ')),
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
         dongbei.Keyword(u'是活雷锋')])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张是 活雷\n锋 。 ')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         dongbei.Keyword(u'是活雷锋'),
         dongbei.Keyword(u'。'),
        ])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张是活雷锋。\n老王是活雷锋。\n')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         dongbei.Keyword(u'是活雷锋'),
         dongbei.Keyword(u'。'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'是活雷锋'),
         dongbei.Keyword(u'。'),
        ])
    self.assertEqual(
        list(dongbei.Tokenize(u'老张装250。\n老王装老张。\n')),
        [Token(dongbei.TK_IDENTIFIER, u'老张'),
         dongbei.Keyword(u'装'),
         Token(dongbei.TK_INTEGER_LITERAL, 250),
         dongbei.Keyword(u'。'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'装'),
         Token(dongbei.TK_IDENTIFIER, u'老张'),
         dongbei.Keyword(u'。')])
    self.assertEqual(
        list(dongbei.Tokenize(u'唠唠：“你好”。')),
        [dongbei.Keyword(u'唠唠'),
         dongbei.Keyword(u'：'),
         dongbei.Keyword(u'“'),
         Token(dongbei.TK_STRING_LITERAL, u'你好'),
         dongbei.Keyword(u'”'),
         dongbei.Keyword(u'。')])

  def testTokenizeArithmetic(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'250加13减二乘五除以九')),
        [Token(dongbei.TK_INTEGER_LITERAL, 250),
         dongbei.Keyword(u'加'),
         Token(dongbei.TK_INTEGER_LITERAL, 13),
         dongbei.Keyword(u'减'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),
         dongbei.Keyword(u'乘'),
         Token(dongbei.TK_INTEGER_LITERAL, 5),
         dongbei.Keyword(u'除以'),
         Token(dongbei.TK_INTEGER_LITERAL, 9),
        ])
    
  def testTokenizeLoop(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王从1到9磨叽：磨叽完了。')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'从'),
         Token(dongbei.TK_INTEGER_LITERAL, 1),
         dongbei.Keyword(u'到'),
         Token(dongbei.TK_INTEGER_LITERAL, 9),
         dongbei.Keyword(u'磨叽：'),
         dongbei.Keyword(u'磨叽完了'),
         dongbei.Keyword(u'。'),
        ])

  def testTokenizeCompound(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'开整了：\n  唠唠：老王。\n整完了。')),
        [dongbei.Keyword(u'开整了：'),
         dongbei.Keyword(u'唠唠'),
         dongbei.Keyword(u'：'),
         Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'。'),
         dongbei.Keyword(u'整完了'),
         dongbei.Keyword(u'。'),])

  def testTokenizingIncrements(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王走走')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'走走'),])
    self.assertEqual(
        list(dongbei.Tokenize(u'老王走两步')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'走'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),
         dongbei.Keyword(u'步'),
        ])

  def testTokenizingDecrements(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老王退退')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'退退'),])
    self.assertEqual(
        list(dongbei.Tokenize(u'老王退三步')),
        [Token(dongbei.TK_IDENTIFIER, u'老王'),
         dongbei.Keyword(u'退'),
         Token(dongbei.TK_INTEGER_LITERAL, 3),
         dongbei.Keyword(u'步'),
        ])

  def testTokenizingConcat(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'老刘、二')),
        [Token(dongbei.TK_IDENTIFIER, u'老刘'),
         dongbei.Keyword(u'、'),
         Token(dongbei.TK_INTEGER_LITERAL, 2),])

  def testTokenizingFuncDef(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'写九九表咋整：整完了。')),
        [Token(dongbei.TK_IDENTIFIER, u'写九九表'),
         dongbei.Keyword(u'咋整：'),
         dongbei.Keyword(u'整完了'),
         dongbei.Keyword(u'。'),])

  def testTokenizingFuncCall(self):
    self.assertEqual(
        list(dongbei.Tokenize(u'整写九九表')),
        [dongbei.Keyword(u'整'),
         Token(dongbei.TK_IDENTIFIER, u'写九九表'),])
    
  def testParsingIncrements(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王走走。'),
        [Statement(
            dongbei.STMT_INC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        dongbei.ParseToAst(u'老王走两步。'),
        [Statement(
            dongbei.STMT_INC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 2)])))])

  def testParsingDecrements(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王退退。'),
        [Statement(
            dongbei.STMT_DEC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        dongbei.ParseToAst(u'老王退三步。'),
        [Statement(
            dongbei.STMT_DEC_BY,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 3)])))])

  def testParsingArithmetic(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王装250加13减二乘五除以六。'),
        [Statement(
            dongbei.STMT_ASSIGN,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([
                 Token(dongbei.TK_INTEGER_LITERAL, 250),
                 dongbei.Keyword(u'加'),
                 Token(dongbei.TK_INTEGER_LITERAL, 13),
                 dongbei.Keyword(u'减'),
                 Token(dongbei.TK_INTEGER_LITERAL, 2),
                 dongbei.Keyword(u'乘'),
                 Token(dongbei.TK_INTEGER_LITERAL, 5),
                 dongbei.Keyword(u'除以'),
                 Token(dongbei.TK_INTEGER_LITERAL, 6),
             ])))])
    
  def testParsingLoop(self):
    self.assertEqual(
        dongbei.ParseToAst(u'老王从1到9磨叽：磨叽完了。'),
        [Statement(
            dongbei.STMT_LOOP,
            (Token(dongbei.TK_IDENTIFIER, u'老王'),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 1)]),
             Expr([Token(dongbei.TK_INTEGER_LITERAL, 9)]),
             []))])

  def DisabledTestParsingComparison(self):
    self.assertEquals(
        dongbei.ParseToAst(u'唠唠：2比5大。'),
        [Statement(
            dongbei.STMT_SAY,
            ComparisonExpr(2, 'GT', 5)
        )])

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
                               Expr([Token(
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
                    [Expr([Token(dongbei.TK_INTEGER_LITERAL, 5)])]))])

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

  def testLoopWithNoStatement(self):
    self.assertEqual(
        dongbei.Run(u'老张从1到2磨叽：磨叽完了。'),
        '')

  def testLoopWithMultipleStatements(self):
    self.assertEqual(
        dongbei.Run(u'老张从1到2磨叽：唠唠：老张。唠唠：老张加一。磨叽完了。'),
        '1\n2\n2\n3\n')

  def testConcat(self):
    self.assertEqual(
        dongbei.Run(u'唠唠：“牛”、二。'),
        u'牛2\n')
    self.assertEqual(
        dongbei.Run(u'唠唠：“老王”、665加一。'),
        u'老王666\n')

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

  def testFuncWithReturnValue(self):
    self.assertEqual(
        dongbei.Run(u'【加一】（几）咋整：滚犊子吧几加一。整完了。\n'
                    u'唠唠：整【加一】（二）。'),
        u'3\n')
    
  def testNormalizingBang(self):
    self.assertEqual(
        dongbei.Run(u'【加一】（几）咋整：唠唠：几加一！整完了！\n'
                    u'整【加一】（五）！'),
        u'6\n')
    
if __name__ == '__main__':
  unittest.main()
