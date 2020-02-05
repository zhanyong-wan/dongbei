#!/usr/bin/env python3
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
from src.dongbei import ConcatExpr
from src.dongbei import Keyword
from src.dongbei import ParenExpr
from src.dongbei import ParseChars
from src.dongbei import ParseExprFromStr
from src.dongbei import ParseInteger
from src.dongbei import ParseStmtFromStr
from src.dongbei import ParseToAst
from src.dongbei import Run
from src.dongbei import STMT_ASSIGN
from src.dongbei import STMT_CALL
from src.dongbei import STMT_CONDITIONAL
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

  def testParseComparisonExpr(self):
    self.assertEqual(ParseExprFromStr(u'5比6大')[0],
                     ComparisonExpr(
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 5)),
                         Keyword(u'大'),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 6))
                     ))
    self.assertEqual(ParseExprFromStr(u'老王加5比6小')[0],
                     ComparisonExpr(
                         ArithmeticExpr(
                             VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                             Keyword(u'加'),
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 5))),
                         Keyword(u'小'),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 6))
                     ))
    self.assertEqual(ParseExprFromStr(u'老王跟老刘一样一样的')[0],
                     ComparisonExpr(
                         VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                         Keyword(u'一样一样的'),
                         VariableExpr(Token(TK_IDENTIFIER, u'老刘'))
                     ))
    self.assertEqual(ParseExprFromStr(u'老王加5跟6不是一样一样的')[0],
                     ComparisonExpr(
                         ArithmeticExpr(
                             VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                             Keyword(u'加'),
                             LiteralExpr(Token(TK_INTEGER_LITERAL, 5))),
                         Keyword(u'不是一样一样的'),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 6))
                     ))

  def testParseConcatExpr(self):
    self.assertEqual(ParseExprFromStr(u'老王、2')[0],
                     ConcatExpr([
                         VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 2))
                     ]))
  def testParseConcatExpr(self):
    self.assertEqual(ParseExprFromStr(u'老王加油、2、“哈”')[0],
                     ConcatExpr([
                         ArithmeticExpr(
                             VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                             Keyword(u'加'),
                             VariableExpr(Token(TK_IDENTIFIER, u'油'))),
                         LiteralExpr(Token(TK_INTEGER_LITERAL, 2)),
                         LiteralExpr(Token(TK_STRING_LITERAL, u'哈'))
                     ]))

class DongbeiParseStatementTest(unittest.TestCase):
  def testParseConditional(self):
    self.assertEqual(
        ParseStmtFromStr(u'瞅瞅：老王比五大吗？要行咧就唠唠：老王。')[0],
        Statement(STMT_CONDITIONAL,
                  (ComparisonExpr(
                      VariableExpr(Token(TK_IDENTIFIER, u'老王')),
                      Keyword(u'大'),
                      LiteralExpr(Token(TK_INTEGER_LITERAL, 5))),
                   # then-branch
                   Statement(STMT_SAY,
                             VariableExpr(Token(TK_IDENTIFIER, u'老王'))),
                   # else-branch
                   None
                  )))
  
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
        list(Tokenize(u'开整：\n  唠唠：老王。\n整完了。')),
        [Keyword(u'开整：'),
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
             LiteralExpr(Token(TK_INTEGER_LITERAL, 1))))])
    self.assertEqual(
        ParseToAst(u'老王走两步。'),
        [Statement(
            STMT_INC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             LiteralExpr(Token(TK_INTEGER_LITERAL, 2))))])

  def testParsingDecrements(self):
    self.assertEqual(
        ParseToAst(u'老王退退。'),
        [Statement(
            STMT_DEC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             LiteralExpr(Token(TK_INTEGER_LITERAL, 1))))])
    self.assertEqual(
        ParseToAst(u'老王退三步。'),
        [Statement(
            STMT_DEC_BY,
            (Token(TK_IDENTIFIER, u'老王'),
             LiteralExpr(Token(TK_INTEGER_LITERAL, 3))))])

  def testParsingLoop(self):
    self.assertEqual(
        ParseToAst(u'老王从1到9磨叽：磨叽完了。'),
        [Statement(
            STMT_LOOP,
            (Token(TK_IDENTIFIER, u'老王'),
             LiteralExpr(Token(TK_INTEGER_LITERAL, 1)),
             LiteralExpr(Token(TK_INTEGER_LITERAL, 9)),
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
                               LiteralExpr(Token(
                                   TK_INTEGER_LITERAL, 1)))]
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
                   CallExpr(Token(TK_IDENTIFIER, u'阶乘'),
                            [LiteralExpr(Token(TK_INTEGER_LITERAL, 5))]))])

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

  def testPrintBool(self):
    self.assertEqual(
        Run(u'唠唠：五比二大。'),
        u'对\n')
    self.assertEqual(
        Run(u'唠唠：五比二大、五比二小、一跟2一样一样的、1跟二不是一样一样的。'),
        u'对错错对\n')

  def testIntegerLiteral(self):
    self.assertEqual(
      Run(u'唠唠：零。'),
      u'0\n')
    self.assertEqual(
      Run(u'唠唠：一。'),
      u'1\n')
    self.assertEqual(
      Run(u'唠唠：二。'),
      u'2\n')
    self.assertEqual(
      Run(u'唠唠：两。'),
      u'2\n')
    self.assertEqual(
      Run(u'唠唠：俩。'),
      u'2\n')
    self.assertEqual(
      Run(u'唠唠：三。'),
      u'3\n')
    self.assertEqual(
      Run(u'唠唠：仨。'),
      u'3\n')
    self.assertEqual(
      Run(u'唠唠：四。'),
      u'4\n')
    self.assertEqual(
      Run(u'唠唠：五。'),
      u'5\n')
    self.assertEqual(
      Run(u'唠唠：六。'),
      u'6\n')
    self.assertEqual(
      Run(u'唠唠：七。'),
      u'7\n')
    self.assertEqual(
      Run(u'唠唠：八。'),
      u'8\n')
    self.assertEqual(
      Run(u'唠唠：九。'),
      u'9\n')
    self.assertEqual(
      Run(u'唠唠：十。'),
      u'10\n')

  def testArithmetic(self):
    self.assertEqual(
      Run(u'唠唠：五加二。'),
      u'7\n')
    self.assertEqual(
      Run(u'唠唠：五减二。'),
      u'3\n')
    self.assertEqual(
      Run(u'唠唠：五乘二。'),
      u'10\n')
    self.assertEqual(
      Run(u'唠唠：十除以二。'),
      u'5.0\n')
    self.assertEqual(
      Run(u'唠唠：五加七乘二。'),
      u'19\n')
    self.assertEqual(
      Run(u'唠唠：（五加七）乘二。'),
      u'24\n')
    self.assertEqual(
      Run(u'唠唠：(五加七)乘二。'),
      u'24\n')
    self.assertEqual(
      Run(u'唠唠：(五减（四减三）)乘二。'),
      u'8\n')

  def testConcat(self):
    self.assertEqual(
        Run(u'唠唠：“牛”、二。'),
        u'牛2\n')
    self.assertEqual(
        Run(u'唠唠：“老王”、665加一。'),
        u'老王666\n')

  def testCompound(self):
    self.assertEqual(
        Run(u'开整：整完了。'),
        u'')
    self.assertEqual(
        Run(u'开整：唠唠：1。整完了。'),
        u'1\n')
    self.assertEqual(
        Run(u'开整：唠唠：1。唠唠：2。整完了。'),
        u'1\n2\n')

  def testRunConditional(self):
    self.assertEqual(
        Run(u'瞅瞅：5比2大吗？要行咧就唠唠：“OK”。'),
        u'OK\n')
    self.assertEqual(
        Run(u'瞅瞅：5比2大吗？要行咧就开整：\n'
            u'整完了。'),
        u'')
    self.assertEqual(
        Run(u'瞅瞅：5比2大吗？\n'
            u'要行咧就开整：\n'
            u'    唠唠：5。\n'
            u'整完了。'),
        u'5\n')
    self.assertEqual(
        Run(u'瞅瞅：5比6大吗？要行咧就唠唠：“OK”。\n'
            u'要不行咧就唠唠：“不OK”。'),
        u'不OK\n')
    self.assertEqual(
        Run(u'瞅瞅：5比6大吗？\n'
            u'要行咧就唠唠：“OK”。\n'
            u'要不行咧就开整：\n'
            u'  唠唠：“不OK”。\n'
            u'  唠唠：“还是不OK”。\n'
            u'整完了。'),
        u'不OK\n还是不OK\n')
    # Else should match the last If.
    self.assertEqual(
        Run(u'''
          瞅瞅：2比1大吗？   # condition 1: True
          要行咧就瞅瞅：2比3大吗？  # condition 2: False
              要行咧就唠唠：“A”。  # for condition 2
              要不行咧就唠唠：“B”。# for condition 2
          '''),
        u'B\n')

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

  def testRecursiveFunc(self):
    self.assertEqual(
        Run(u'''
【阶乘】（几）咋整：
瞅瞅：几比一小吗？
要行咧就滚犊子吧一。
滚犊子吧几乘整【阶乘】（几减一）。
整完了。

唠唠：整【阶乘】（五）。
        '''),
        u'120\n')

  def testMultiArgFunc(self):
    self.assertEqual(
        Run(u'''
求和（甲，乙）咋整：
  滚犊子吧 甲加乙。
整完了。

唠唠：整求和（五，七）。
        '''),
        u'12\n')
    self.assertEqual(
        Run(u'''
求和（甲，乙）咋整：
  唠唠：甲加乙。
整完了。

整求和（五，七）。
        '''),
        u'12\n')

  def testNormalizingBang(self):
    self.assertEqual(
        Run(u'【加一】（几）咋整：唠唠：几加一！整完了！\n'
                    u'整【加一】（五）！'),
        u'6\n')
    
if __name__ == '__main__':
  unittest.main()
