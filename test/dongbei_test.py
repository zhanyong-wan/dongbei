#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the Python module path.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import dongbei
from src.dongbei import ArithmeticExpr
from src.dongbei import LiteralExpr
from src.dongbei import BasicTokenize
from src.dongbei import CallExpr
from src.dongbei import ComparisonExpr
from src.dongbei import Expr
from src.dongbei import Keyword
from src.dongbei import ParenExpr
from src.dongbei import ParseChars
from src.dongbei import ParseExprFromStr
from src.dongbei import ParseInteger
from src.dongbei import ParseToAst
from src.dongbei import Run
from src.dongbei import STMT_ASSIGN
from src.dongbei import STMT_CALL
from src.dongbei import STMT_DEC_BY
from src.dongbei import STMT_FUNC_DEF
from src.dongbei import STMT_INC_BY
from src.dongbei import STMT_LOOP
from src.dongbei import STMT_SAY
from src.dongbei import Statement
from src.dongbei import TK_CHAR
from src.dongbei import TK_IDENTIFIER
from src.dongbei import TK_INTEGER_LITERAL
from src.dongbei import TK_STRING_LITERAL
from src.dongbei import Token
from src.dongbei import Tokenize
from src.dongbei import VariableExpr

class DongbeiParseExprTest(unittest.TestCase):
  def testParseInteger(self):
    self.assertEqual(ParseExprFromStr(u'5')[0],
                     LiteralExpr(Token(TK_INTEGER_LITERAL, 5)))
    self.assertEqual(ParseExprFromStr(u'九')[0],
                     LiteralExpr(Token(TK_INTEGER_LITERAL, 9)))
    
  def testParseStringLiteral(self):
    self.assertEqual(ParseExprFromStr(u'“ 哈  哈   ”')[0],
                     LiteralExpr(Token(TK_STRING_LITERAL, u' 哈  哈   ')))

  def testParseIdentifier(self):
    self.assertEqual(ParseExprFromStr(u'老王')[0],
                     VariableExpr(Token(TK_IDENTIFIER, u'老王')))

  def testParseParens(self):
    # Wide parens.
    self.assertEqual(ParseExprFromStr(u'（老王）')[0],
                     ParenExpr(
                         VariableExpr(Token(TK_IDENTIFIER, u'老王'))))
    # Narrow parens.
    self.assertEqual(ParseExprFromStr(u'(老王)')[0],
                     ParenExpr(
                         VariableExpr(Token(TK_IDENTIFIER, u'老王'))))

  def testParseCallExpr(self):
    self.assertEqual(ParseExprFromStr(u'整老王')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'), []))
    self.assertEqual(ParseExprFromStr(u'整老王（5）')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'),
                              [LiteralExpr(Token(TK_INTEGER_LITERAL, 5))]))
    self.assertEqual(ParseExprFromStr(u'整老王(6)')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'),
                              [LiteralExpr(Token(TK_INTEGER_LITERAL, 6))]))
    self.assertEqual(ParseExprFromStr(u'整老王(老刘，6)')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'),
                              [VariableExpr(Token(TK_IDENTIFIER, u'老刘')),
                               LiteralExpr(Token(TK_INTEGER_LITERAL, 6))]))
    self.assertEqual(ParseExprFromStr(u'整老王(“你”，老刘，6)')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'),
                              [LiteralExpr(Token(TK_STRING_LITERAL, u'你')),
                               VariableExpr(Token(TK_IDENTIFIER, u'老刘')),
                               LiteralExpr(Token(TK_INTEGER_LITERAL, 6))]))
    self.assertEqual(ParseExprFromStr(u'整老王(“你”,老刘，6)')[0],
                     CallExpr(Token(TK_IDENTIFIER, u'老王'),
                              [LiteralExpr(Token(TK_STRING_LITERAL, u'你')),
                               VariableExpr(Token(TK_IDENTIFIER, u'老刘')),
                               LiteralExpr(Token(TK_INTEGER_LITERAL, 6))]))

  def testParseTermExpr(self):
    self.assertEqual(ParseExprFromStr(u'老王乘五')[0],
                     ArithmeticExpr(
                         VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                         Keyword(u'乘'),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 5)))
                     )
    self.assertEqual(ParseExprFromStr(u'五除以老王')[0],
                     ArithmeticExpr(
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                         Keyword(u'除以'),
                         VariableExpr(Token(TK_IDENTIFIER, u'老王')))
                     )
    self.assertEqual(ParseExprFromStr(u'五除以老王乘老刘')[0],
                     ArithmeticExpr(
                         ArithmeticExpr(
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                             Keyword(u'除以'),
                             VariableExpr(Token(TK_IDENTIFIER, u'老王'))),
                         Keyword(u'乘'),
                         VariableExpr(Token(TK_IDENTIFIER, u'老刘'))
                     ))

  def testParseArithmeticExpr(self):
    self.assertEqual(ParseExprFromStr(u'5加六')[0],
                     ArithmeticExpr(
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                         Keyword(u'加'),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 6))
                     ))
    self.assertEqual(ParseExprFromStr(u'5加六乘3')[0],
                     ArithmeticExpr(
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                         Keyword(u'加'),
                         ArithmeticExpr(
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 6)),
                             Keyword(u'乘'),
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 3)))))
    self.assertEqual(ParseExprFromStr(u'5减六减老王')[0],
                     ArithmeticExpr(
                         ArithmeticExpr(
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                             Keyword(u'减'),
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 6))
                         ),
                         Keyword(u'减'),
                         VariableExpr(Token(TK_IDENTIFIER, u'老王')))
                     )

class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(Run(''), '')

  def testRunHelloWorld(self):
    self.assertEqual(
        Run(u'唠唠：“这旮旯儿嗷嗷美好哇！”。'),
        u'这旮旯儿嗷嗷美好哇！\n')

  def testRunHelloWorld2(self):
    self.assertEqual(
        Run(u'唠唠：“你那旮旯儿也挺美好哇！”。'),
        u'你那旮旯儿也挺美好哇！\n')

  def testVarDecl(self):
    self.assertEqual(
        Run(u'老张是活雷锋。'), '')

  def testVarAssignment(self):
    self.assertEqual(
        Run(u'老张是活雷锋。\n老张装250。\n唠唠：老张。'), '250\n')

  def testTokenize(self):
    self.assertEqual(
        list(BasicTokenize(u'【阶乘】')),
        [Token(TK_IDENTIFIER, u'阶乘'),])
    self.assertEqual(
        list(BasicTokenize(u'【 阶  乘   】')),
        [Token(TK_IDENTIFIER, u'阶乘'),])
    self.assertEqual(
        list(BasicTokenize(u'【阶乘】（几）')),
        [Token(TK_IDENTIFIER, u'阶乘'),
         Keyword(u'（'),
         Token(TK_CHAR, u'几'),
         Keyword(u'）'),])
    self.assertEqual(
        list(BasicTokenize(u'“ ”')),
        [Keyword(u'“'),
         Token(TK_STRING_LITERAL, u' '),
         Keyword(u'”'),])
    self.assertEqual(
        list(BasicTokenize(u'“”')),
        [Keyword(u'“'),
         Token(TK_STRING_LITERAL, u''),
         Keyword(u'”'),])
    self.assertEqual(
        list(BasicTokenize(u'“ A B ”')),
        [Keyword(u'“'),
         Token(TK_STRING_LITERAL, u' A B '),
         Keyword(u'”'),])
    self.assertEqual(
        list(BasicTokenize(u'老张')),
        [Token(TK_CHAR, u'老'),
         Token(TK_CHAR, u'张'),])
    self.assertEqual(
        list(BasicTokenize(u'  老 张   ')),
        [Token(TK_CHAR, u'老'),
         Token(TK_CHAR, u'张'),])
    self.assertEqual(
        list(Tokenize(u'# 123456\n老张')),
        [Token(TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        list(Tokenize(u'老张')),
        [Token(TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        ParseInteger(u'老张'),
        (None, u'老张'))
    self.assertEqual(
        list(ParseChars(u'老张')),
        [Token(TK_IDENTIFIER, u'老张')])
    self.assertEqual(
        list(Tokenize(u'老张是活雷锋')),
        [Token(TK_IDENTIFIER, u'老张'),
         Keyword(u'是活雷锋')])
    self.assertEqual(
        list(Tokenize(u'老张是 活雷\n锋 。 ')),
        [Token(TK_IDENTIFIER, u'老张'),
         Keyword(u'是活雷锋'),
         Keyword(u'。'),
        ])
    self.assertEqual(
        list(Tokenize(u'老张是活雷锋。\n老王是活雷锋。\n')),
        [Token(TK_IDENTIFIER, u'老张'),
         Keyword(u'是活雷锋'),
         Keyword(u'。'),
         Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'是活雷锋'),
         Keyword(u'。'),
        ])
    self.assertEqual(
        list(Tokenize(u'老张装250。\n老王装老张。\n')),
        [Token(TK_IDENTIFIER, u'老张'),
         Keyword(u'装'),
         Token(TK_INTEGER_LITERAL, 250),
         Keyword(u'。'),
         Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'装'),
         Token(TK_IDENTIFIER, u'老张'),
         Keyword(u'。')])
    self.assertEqual(
        list(Tokenize(u'唠唠：“你好”。')),
        [Keyword(u'唠唠'),
         Keyword(u'：'),
         Keyword(u'“'),
         Token(TK_STRING_LITERAL, u'你好'),
         Keyword(u'”'),
         Keyword(u'。')])

  def testTokenizeArithmetic(self):
    self.assertEqual(
        list(Tokenize(u'250加13减二乘五除以九')),
        [Token(TK_INTEGER_LITERAL, 250),
         Keyword(u'加'),
         Token(TK_INTEGER_LITERAL, 13),
         Keyword(u'减'),
         Token(TK_INTEGER_LITERAL, 2),
         Keyword(u'乘'),
         Token(TK_INTEGER_LITERAL, 5),
         Keyword(u'除以'),
         Token(TK_INTEGER_LITERAL, 9),
        ])
    
  def testTokenizeLoop(self):
    self.assertEqual(
        list(Tokenize(u'老王从1到9磨叽：磨叽完了。')),
        [Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'从'),
         Token(TK_INTEGER_LITERAL, 1),
         Keyword(u'到'),
         Token(TK_INTEGER_LITERAL, 9),
         Keyword(u'磨叽：'),
         Keyword(u'磨叽完了'),
         Keyword(u'。'),
        ])

  def testTokenizeCompound(self):
    self.assertEqual(
        list(Tokenize(u'开整了：\n  唠唠：老王。\n整完了。')),
        [Keyword(u'开整了：'),
         Keyword(u'唠唠'),
         Keyword(u'：'),
         Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'。'),
         Keyword(u'整完了'),
         Keyword(u'。'),])

  def testTokenizingIncrements(self):
    self.assertEqual(
        list(Tokenize(u'老王走走')),
        [Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'走走'),])
    self.assertEqual(
        list(Tokenize(u'老王走两步')),
        [Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'走'),
         Token(TK_INTEGER_LITERAL, 2),
         Keyword(u'步'),
        ])

  def testTokenizingDecrements(self):
    self.assertEqual(
        list(Tokenize(u'老王退退')),
        [Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'退退'),])
    self.assertEqual(
        list(Tokenize(u'老王退三步')),
        [Token(TK_IDENTIFIER, u'老王'),
         Keyword(u'退'),
         Token(TK_INTEGER_LITERAL, 3),
         Keyword(u'步'),
        ])

  def testTokenizingConcat(self):
    self.assertEqual(
        list(Tokenize(u'老刘、二')),
        [Token(TK_IDENTIFIER, u'老刘'),
         Keyword(u'、'),
         Token(TK_INTEGER_LITERAL, 2),])

  def testTokenizingFuncDef(self):
    self.assertEqual(
        list(Tokenize(u'写九九表咋整：整完了。')),
        [Token(TK_IDENTIFIER, u'写九九表'),
         Keyword(u'咋整：'),
         Keyword(u'整完了'),
         Keyword(u'。'),])

  def testTokenizingFuncCall(self):
    self.assertEqual(
        list(Tokenize(u'整写九九表')),
        [Keyword(u'整'),
         Token(TK_IDENTIFIER, u'写九九表'),])
    
  def testParsingIncrements(self):
    self.assertEqual(
        ParseToAst(u'老王走走。'),
        [Statement(
            STMT_INC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([Token(TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        ParseToAst(u'老王走两步。'),
        [Statement(
            STMT_INC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([Token(TK_INTEGER_LITERAL, 2)])))])

  def testParsingDecrements(self):
    self.assertEqual(
        ParseToAst(u'老王退退。'),
        [Statement(
            STMT_DEC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([Token(TK_INTEGER_LITERAL, 1)])))])
    self.assertEqual(
        ParseToAst(u'老王退三步。'),
        [Statement(
            STMT_DEC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([Token(TK_INTEGER_LITERAL, 3)])))])

  def testParsingArithmetic(self):
    self.assertEqual(
        ParseToAst(u'老王装250加13减二乘五除以六。'),
        [Statement(
            STMT_ASSIGN,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([
                 Token(TK_INTEGER_LITERAL, 250),
                 Keyword(u'加'),
                 Token(TK_INTEGER_LITERAL, 13),
                 Keyword(u'减'),
                 Token(TK_INTEGER_LITERAL, 2),
                 Keyword(u'乘'),
                 Token(TK_INTEGER_LITERAL, 5),
                 Keyword(u'除以'),
                 Token(TK_INTEGER_LITERAL, 6),
             ])))])
    
  def testParsingLoop(self):
    self.assertEqual(
        ParseToAst(u'老王从1到9磨叽：磨叽完了。'),
        [Statement(
            STMT_LOOP,
            (Token(TK_IDENTIFIER, u'老王'),
             Expr([Token(TK_INTEGER_LITERAL, 1)]),
             Expr([Token(TK_INTEGER_LITERAL, 9)]),
             []))])

  def DisabledTestParsingComparison(self):
    self.assertEquals(
        ParseToAst(u'唠唠：2比5大。'),
        [Statement(
            STMT_SAY,
            ComparisonExpr(2, 'GT', 5)
        )])

  def testParsingFuncDef(self):
    self.assertEqual(
        ParseToAst(u'写九九表咋整：整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (Token(TK_IDENTIFIER, u'写九九表'),
                    [],  # Formal parameters.
                    []  # Function body.
                   ))])
    self.assertEqual(
        ParseToAst(u'写九九表咋整：唠唠：1。整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (Token(TK_IDENTIFIER, u'写九九表'),
                    [],  # Formal parameters.
                    # Function body.
                    [Statement(STMT_SAY,
                               Expr([Token(
                                   TK_INTEGER_LITERAL, 1)]))]
                   ))])
    
  def testParsingFuncDefWithParam(self):
    self.assertEqual(
        ParseToAst(u'【阶乘】（几）咋整：整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (Token(TK_IDENTIFIER, u'阶乘'),
                    [Token(TK_IDENTIFIER, u'几')],  # Formal parameters.
                    []  # Function body.
                   ))])
    
  def testParsingFuncCallWithParam(self):
    self.assertEqual(
        ParseToAst(u'整【阶乘】（五）。'),
        [Statement(STMT_CALL,
                   (Token(TK_IDENTIFIER, u'阶乘'),
                    [Expr([Token(TK_INTEGER_LITERAL, 5)])]))])

  def testVarAssignmentFromVar(self):
    self.assertEqual(
        Run(u'老张是活雷锋。\n老王是活雷锋。\n'
                    u'老张装250。\n老王装老张。\n唠唠：老王。'), '250\n')

  def testIncrements(self):
    self.assertEqual(
        Run(u'老张是活雷锋。老张装二。老张走走。唠唠：老张。'),
        '3\n')
    self.assertEqual(
        Run(u'老张是活雷锋。老张装三。老张走五步。唠唠：老张。'),
        '8\n')

  def testDecrements(self):
    self.assertEqual(
        Run(u'老张是活雷锋。老张装二。老张退退。唠唠：老张。'),
        '1\n')
    self.assertEqual(
        Run(u'老张是活雷锋。老张装三。老张退五步。唠唠：老张。'),
        '-2\n')

  def testLoop(self):
    self.assertEqual(
        Run(u'老张从1到3磨叽：唠唠：老张。磨叽完了。'),
        '1\n2\n3\n')

  def testLoopWithNoStatement(self):
    self.assertEqual(
        Run(u'老张从1到2磨叽：磨叽完了。'),
        '')

  def testLoopWithMultipleStatements(self):
    self.assertEqual(
        Run(u'老张从1到2磨叽：唠唠：老张。唠唠：老张加一。磨叽完了。'),
        '1\n2\n2\n3\n')

  def testConcat(self):
    self.assertEqual(
        Run(u'唠唠：“牛”、二。'),
        u'牛2\n')
    self.assertEqual(
        Run(u'唠唠：“老王”、665加一。'),
        u'老王666\n')

  def testRunFunc(self):
    self.assertEqual(
        Run(u'埋汰咋整：唠唠：“你虎了吧唧”。整完了。'),
        u'')
    self.assertEqual(
        Run(u'埋汰咋整：唠唠：“你虎了吧唧”。整完了。整埋汰。'),
        u'你虎了吧唧\n')

  def testFuncCallWithParam(self):
    self.assertEqual(
        Run(u'【加一】（几）咋整：唠唠：几加一。整完了。\n'
                    u'整【加一】（五）。'),
        u'6\n')

  def testFuncWithReturnValue(self):
    self.assertEqual(
        Run(u'【加一】（几）咋整：滚犊子吧几加一。整完了。\n'
                    u'唠唠：整【加一】（二）。'),
        u'3\n')
    
  def testNormalizingBang(self):
    self.assertEqual(
        Run(u'【加一】（几）咋整：唠唠：几加一！整完了！\n'
                    u'整【加一】（五）！'),
        u'6\n')
    
if __name__ == '__main__':
  unittest.main()
