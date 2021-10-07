#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add the repo root to the beginning of the Python module path.
# Even if the user has installed dongbei locally, the version
# next to the test file will be used.
sys.path = [os.path.join(os.path.dirname(__file__), '..')] + sys.path

from src import dongbei
from src.dongbei import ArithmeticExpr
from src.dongbei import CallExpr
from src.dongbei import ComparisonExpr
from src.dongbei import ConcatExpr
from src.dongbei import DongbeiParser
from src.dongbei import LiteralExpr
from src.dongbei import ParenExpr
from src.dongbei import ParseExprFromStr
from src.dongbei import ParseStmtFromStr
from src.dongbei import ParseToAst
from src.dongbei import TokenizeStrContainingNoKeyword
from src.dongbei import TryParseNumber
from src.dongbei import STMT_ASSIGN
from src.dongbei import STMT_CALL
from src.dongbei import STMT_CONDITIONAL
from src.dongbei import STMT_DEC_BY
from src.dongbei import STMT_FUNC_DEF
from src.dongbei import STMT_INC_BY
from src.dongbei import STMT_INFINITE_LOOP
from src.dongbei import STMT_LOOP
from src.dongbei import STMT_SAY
from src.dongbei import Statement
from src.dongbei import TK_CHAR
from src.dongbei import TK_IDENTIFIER
from src.dongbei import TK_NUMBER_LITERAL
from src.dongbei import TK_STRING_LITERAL
from src.dongbei import Token
from src.dongbei import TranslateDongbeiToPython
from src.dongbei import VariableExpr

def Keyword(value):
  return dongbei.Keyword(value, None)

def NumberLiteralExpr(value):
  return dongbei.NumberLiteralExpr(value, None)

def IdentifierToken(identifier):
  return dongbei.IdentifierToken(identifier, None)

def Tokenize(code):
  return DongbeiParser().Tokenize(code, None)

def Run(code):
  return dongbei.Run(code, None)

def StringLiteralExpr(value):
  return LiteralExpr(Token(TK_STRING_LITERAL, value, None))

class DongbeiParseExprTest(unittest.TestCase):
  def testParseNumber(self):
    self.assertEqual(ParseExprFromStr('5')[0],
                     NumberLiteralExpr(5))
    self.assertEqual(ParseExprFromStr('九')[0],
                     NumberLiteralExpr(9))
    
  def testParseStringLiteral(self):
    self.assertEqual(ParseExprFromStr('“ 哈  哈   ”')[0],
                     StringLiteralExpr(' 哈  哈   '))

  def testParseIdentifier(self):
    self.assertEqual(ParseExprFromStr('老王')[0],
                     VariableExpr('老王'))

  def testParseParens(self):
    # Wide parens.
    self.assertEqual(ParseExprFromStr('（老王）')[0],
                     ParenExpr(
                         VariableExpr('老王')))
    # Narrow parens.
    self.assertEqual(ParseExprFromStr('(老王)')[0],
                     ParenExpr(
                         VariableExpr('老王')))

  def testParseCallExpr(self):
    self.assertEqual(ParseExprFromStr('整老王')[0],
                     CallExpr('老王', []))
    self.assertEqual(ParseExprFromStr('整老王（5）')[0],
                     CallExpr('老王',
                              [NumberLiteralExpr(5)]))
    self.assertEqual(ParseExprFromStr('整老王(6)')[0],
                     CallExpr('老王',
                              [NumberLiteralExpr(6)]))
    self.assertEqual(ParseExprFromStr('整老王(老刘，6)')[0],
                     CallExpr('老王',
                              [VariableExpr('老刘'),
                               NumberLiteralExpr(6)]))
    self.assertEqual(ParseExprFromStr('整老王(“你”，老刘，6)')[0],
                     CallExpr('老王',
                              [StringLiteralExpr('你'),
                               VariableExpr('老刘'),
                               NumberLiteralExpr(6)]))
    self.assertEqual(ParseExprFromStr('整老王(“你”,老刘，6)')[0],
                     CallExpr('老王',
                              [StringLiteralExpr('你'),
                               VariableExpr('老刘'),
                               NumberLiteralExpr(6)]))

  def testParseTermExpr(self):
    self.assertEqual(ParseExprFromStr('老王乘五')[0],
                     ArithmeticExpr(
                         VariableExpr('老王'),
                         Keyword('乘'),
                         NumberLiteralExpr(5))
                     )
    self.assertEqual(ParseExprFromStr('五除以老王')[0],
                     ArithmeticExpr(
                         NumberLiteralExpr(5),
                         Keyword('除以'),
                         VariableExpr('老王'))
                     )
    self.assertEqual(ParseExprFromStr('五除以老王乘老刘')[0],
                     ArithmeticExpr(
                         ArithmeticExpr(
                             NumberLiteralExpr(5),
                             Keyword('除以'),
                             VariableExpr('老王')),
                         Keyword('乘'),
                         VariableExpr('老刘')
                     ))

  def testParseArithmeticExpr(self):
    self.assertEqual(ParseExprFromStr('5加六')[0],
                     ArithmeticExpr(
                         NumberLiteralExpr(5),
                         Keyword('加'),
                         NumberLiteralExpr(6)
                     ))
    self.assertEqual(ParseExprFromStr('5加六乘3')[0],
                     ArithmeticExpr(
                         NumberLiteralExpr(5),
                         Keyword('加'),
                         ArithmeticExpr(
                             NumberLiteralExpr(6),
                             Keyword('乘'),
                             NumberLiteralExpr(3))))
    self.assertEqual(ParseExprFromStr('5减六减老王')[0],
                     ArithmeticExpr(
                         ArithmeticExpr(
                             NumberLiteralExpr(5),
                             Keyword('减'),
                             NumberLiteralExpr(6)
                         ),
                         Keyword('减'),
                         VariableExpr('老王'))
                     )

  def testParseComparisonExpr(self):
    self.assertEqual(ParseExprFromStr('5比6还大')[0],
                     ComparisonExpr(
                         NumberLiteralExpr(5),
                         Keyword('还大'),
                         NumberLiteralExpr(6)
                     ))
    self.assertEqual(ParseExprFromStr('老王加5比6还小')[0],
                     ComparisonExpr(
                         ArithmeticExpr(
                             VariableExpr('老王'),
                             Keyword('加'),
                             NumberLiteralExpr(5)),
                         Keyword('还小'),
                         NumberLiteralExpr(6)
                     ))
    self.assertEqual(ParseExprFromStr('老王跟老刘一样一样的')[0],
                     ComparisonExpr(
                         VariableExpr('老王'),
                         Keyword('一样一样的'),
                         VariableExpr('老刘')
                     ))
    self.assertEqual(ParseExprFromStr('老王加5跟6不是一样一样的')[0],
                     ComparisonExpr(
                         ArithmeticExpr(
                             VariableExpr('老王'),
                             Keyword('加'),
                             NumberLiteralExpr(5)),
                         Keyword('不是一样一样的'),
                         NumberLiteralExpr(6)
                     ))

  def testParseConcatExpr(self):
    self.assertEqual(ParseExprFromStr('老王、2')[0],
                     ConcatExpr([
                         VariableExpr('老王'),
                         NumberLiteralExpr(2)
                     ]))
  def testParseConcatExpr(self):
    self.assertEqual(ParseExprFromStr('老王加油、2、“哈”')[0],
                     ConcatExpr([
                         ArithmeticExpr(
                             VariableExpr('老王'),
                             Keyword('加'),
                             VariableExpr('油')),
                         NumberLiteralExpr(2),
                         StringLiteralExpr('哈')
                     ]))

class DongbeiParseStatementTest(unittest.TestCase):
  def testParseConditional(self):
    self.assertEqual(
        ParseStmtFromStr('寻思：老王比五还大？要行咧就唠唠：老王。')[0],
        Statement(STMT_CONDITIONAL,
                  (ComparisonExpr(
                      VariableExpr('老王'),
                      Keyword('还大'),
                      NumberLiteralExpr(5)),
                   # then-branch
                   Statement(STMT_SAY,
                             VariableExpr('老王')),
                   # else-branch
                   None
                  )))
  
class DongbeiTest(unittest.TestCase):
  def testRunEmptyProgram(self):
    self.assertEqual(Run(''), '')

  def testRunHelloWorld(self):
    self.assertEqual(
        Run('唠唠：“这旮旯儿嗷嗷美好哇！”。'),
        '这旮旯儿嗷嗷美好哇！\n')

  def testRunHelloWorld2(self):
    self.assertEqual(
        Run('唠唠：“你那旮旯儿也挺美好哇！”。'),
        '你那旮旯儿也挺美好哇！\n')

  def testVarDecl(self):
    self.assertEqual(
        Run('老张是活雷锋。'), '')

  def testVarAssignment(self):
    self.assertEqual(
        Run('老张是活雷锋。\n老张装250。\n唠唠：老张。'), '250\n')

  def testVarQuotesAreOptional(self):
    self.assertEqual(
        Run('老张装二。唠唠：【老张】。'), '2\n')

  def testColonCanBeNarrow(self):
    self.assertEqual(
        Run('老张装二。唠唠:【老张】。'), '2\n')

  def testTokenize(self):
    self.assertEqual(
        Tokenize('# 123456\n老张'),
        [IdentifierToken('老张')])
    self.assertEqual(
        Tokenize('老张'),
        [IdentifierToken('老张')])
    self.assertEqual(
        TryParseNumber('老张'),
        (None, '老张'))
    self.assertEqual(
        list(TokenizeStrContainingNoKeyword('老张', None)),
        [IdentifierToken('老张')])
    self.assertEqual(
        Tokenize('老张是活雷锋'),
        [IdentifierToken('老张'),
         Keyword('是活雷锋')])
    self.assertEqual(
        Tokenize('老张是 活雷\n锋 。 '),
        [IdentifierToken('老张'),
         Keyword('是活雷锋'),
         Keyword('。'),
        ])
    self.assertEqual(
        Tokenize('老张是活雷锋。\n老王是活雷锋。\n'),
        [IdentifierToken('老张'),
         Keyword('是活雷锋'),
         Keyword('。'),
         IdentifierToken('老王'),
         Keyword('是活雷锋'),
         Keyword('。'),
        ])
    self.assertEqual(
        Tokenize('老张装250。\n老王装老张。\n'),
        [IdentifierToken('老张'),
         Keyword('装'),
         Token(TK_NUMBER_LITERAL, 250, None),
         Keyword('。'),
         IdentifierToken('老王'),
         Keyword('装'),
         IdentifierToken('老张'),
         Keyword('。')])
    self.assertEqual(
        Tokenize('唠唠：“你好”。'),
        [Keyword('唠唠'),
         Keyword('：'),
         Keyword('“'),
         Token(TK_STRING_LITERAL, '你好', None),
         Keyword('”'),
         Keyword('。')])

  def testTokenizeArithmetic(self):
    self.assertEqual(
        Tokenize('250加13减二乘五除以九'),
        [Token(TK_NUMBER_LITERAL, 250, None),
         Keyword('加'),
         Token(TK_NUMBER_LITERAL, 13, None),
         Keyword('减'),
         Token(TK_NUMBER_LITERAL, 2, None),
         Keyword('乘'),
         Token(TK_NUMBER_LITERAL, 5, None),
         Keyword('除以'),
         Token(TK_NUMBER_LITERAL, 9, None),
        ])
    
  def testTokenizeLoop(self):
    self.assertEqual(
        Tokenize('老王从1到9磨叽：磨叽完了。'),
        [IdentifierToken('老王'),
         Keyword('从'),
         Token(TK_NUMBER_LITERAL, 1, None),
         Keyword('到'),
         Token(TK_NUMBER_LITERAL, 9, None),
         Keyword('磨叽：'),
         Keyword('磨叽完了'),
         Keyword('。'),
        ])

  def testTokenizeCompound(self):
    self.assertEqual(
        Tokenize('开整：\n  唠唠：老王。\n整完了。'),
        [Keyword('开整：'),
         Keyword('唠唠'),
         Keyword('：'),
         IdentifierToken('老王'),
         Keyword('。'),
         Keyword('整完了'),
         Keyword('。'),])

  def testTokenizingIncrements(self):
    self.assertEqual(
        Tokenize('老王走走'),
        [IdentifierToken('老王'),
         Keyword('走走'),])
    self.assertEqual(
        Tokenize('老王走两步'),
        [IdentifierToken('老王'),
         Keyword('走'),
         Token(TK_NUMBER_LITERAL, 2, None),
         Keyword('步'),
        ])

  def testTokenizingDecrements(self):
    self.assertEqual(
        Tokenize('老王稍稍'),
        [IdentifierToken('老王'),
         Keyword('稍稍'),])
    self.assertEqual(
        Tokenize('老王稍三步'),
        [IdentifierToken('老王'),
         Keyword('稍'),
         Token(TK_NUMBER_LITERAL, 3, None),
         Keyword('步'),
        ])

  def testTokenizingConcat(self):
    self.assertEqual(
        Tokenize('老刘、二'),
        [IdentifierToken('老刘'),
         Keyword('、'),
         Token(TK_NUMBER_LITERAL, 2, None),])

  def testTokenizingFuncDef(self):
    self.assertEqual(
        Tokenize('写九九表咋整：整完了。'),
        [IdentifierToken('写九九表'),
         Keyword('咋整：'),
         Keyword('整完了'),
         Keyword('。'),])

  def testTokenizingFuncCall(self):
    self.assertEqual(
        Tokenize('整写九九表'),
        [Keyword('整'),
         IdentifierToken('写九九表'),])
    
  def testParsingIncrements(self):
    self.assertEqual(
        ParseToAst('老王走走。'),
        [Statement(
            STMT_INC_BY,
            (VariableExpr('老王'),
             NumberLiteralExpr(1)))])
    self.assertEqual(
        ParseToAst('老王走两步。'),
        [Statement(
            STMT_INC_BY,
            (VariableExpr('老王'),
             NumberLiteralExpr(2)))])

  def testParsingDecrements(self):
    self.assertEqual(
        ParseToAst('老王稍稍。'),
        [Statement(
            STMT_DEC_BY,
            (VariableExpr('老王'),
             NumberLiteralExpr(1)))])
    self.assertEqual(
        ParseToAst('老王稍三步。'),
        [Statement(
            STMT_DEC_BY,
            (VariableExpr('老王'),
             NumberLiteralExpr(3)))])

  def testParsingLoop(self):
    self.assertEqual(
        ParseToAst('老王从1到9磨叽：磨叽完了。'),
        [Statement(
            STMT_LOOP,
            (VariableExpr('老王'),
             NumberLiteralExpr(1),
             NumberLiteralExpr(9),
             NumberLiteralExpr(1),
             []))])
    self.assertEqual(
        ParseToAst('老王从二到十一步七蹿磨叽：磨叽完了。'),
        [Statement(
            STMT_LOOP,
            (VariableExpr('老王'),
             NumberLiteralExpr(2),
             NumberLiteralExpr(10),
             NumberLiteralExpr(7),
             []))])
    self.assertEqual(
        ParseToAst('老王从二到十一步七减一蹿磨叽：磨叽完了。'),
        [Statement(
            STMT_LOOP,
            (VariableExpr('老王'),
             NumberLiteralExpr(2),
             NumberLiteralExpr(10),
             ArithmeticExpr(
                NumberLiteralExpr(7),
                Keyword('减'),
                NumberLiteralExpr(1)),
             []))])
    self.assertEqual(
        ParseToAst('老王从一而终磨叽：磨叽完了。'),
        [Statement(
            STMT_INFINITE_LOOP,
            (VariableExpr('老王'),
             []))])
    self.assertEqual(
        ParseToAst('老张在苹果总部磨叽：磨叽完了。'),
        [Statement(
            STMT_INFINITE_LOOP,
            (VariableExpr('老张'),
             []))])

  def testParsingComparison(self):
    self.assertEquals(
        ParseToAst('唠唠：2比5还大。'),
        [Statement(
            STMT_SAY,
            ComparisonExpr(NumberLiteralExpr(2),
                           Keyword('还大'),
                           NumberLiteralExpr(5)
            ))])

  def testParsingFuncDef(self):
    self.assertEqual(
        ParseToAst('写九九表咋整：整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (IdentifierToken('写九九表'),
                    [],  # Formal parameters.
                    []  # Function body.
                   ))])
    self.assertEqual(
        ParseToAst('写九九表咋整：唠唠：1。整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (IdentifierToken('写九九表'),
                    [],  # Formal parameters.
                    # Function body.
                    [Statement(STMT_SAY,
                               LiteralExpr(Token(
                                   TK_NUMBER_LITERAL, 1, None)))]
                   ))])
    
  def testParsingFuncDefWithParam(self):
    self.assertEqual(
        ParseToAst('【阶乘】（那啥）咋整：整完了。'),
        [Statement(STMT_FUNC_DEF,
                   (IdentifierToken('阶乘'),
                    [IdentifierToken('那啥')],  # Formal parameters.
                    []  # Function body.
                   ))])
    
  def testParsingFuncCallWithParam(self):
    self.assertEqual(
        ParseToAst('整【阶乘】（五）。'),
        [Statement(STMT_CALL,
                   CallExpr('阶乘',
                            [NumberLiteralExpr(5)]))])

  def testVarAssignmentFromVar(self):
    self.assertEqual(
        Run('老张是活雷锋。\n老王是活雷锋。\n'
            '老张装250。\n老王装老张。\n唠唠：老王。'), '250\n')

  def testAssignmentToArrayElement(self):
    self.assertEqual(
        Run('''
张家庄都是活雷锋。
张家庄来了个五。
张家庄的老大 装 张家庄的老大乘二。
唠唠：张家庄。'''),
      '「10」\n')

  def testIncrements(self):
    self.assertEqual(
        Run('老张是活雷锋。老张装二。老张走走。唠唠：老张。'),
        '3\n')
    self.assertEqual(
        Run('老张是活雷锋。老张装三。老张走五步。唠唠：老张。'),
        '8\n')
    self.assertEqual(
        Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄的老大走走。
唠唠：张家庄的老大。
张家庄的老大走五步。
唠唠：张家庄的老大。
'''),
        '''3
8
''')

  def testDecrements(self):
    self.assertEqual(
        Run('老张是活雷锋。老张装二。老张稍稍。唠唠：老张。'),
        '1\n')
    self.assertEqual(
        Run('老张是活雷锋。老张装三。老张稍五步。唠唠：老张。'),
        '-2\n')
    self.assertEqual(
        Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄的老大稍稍。
唠唠：张家庄的老大。
张家庄的老大稍五步。
唠唠：张家庄的老大。
'''),
        '''1
-4
''')

  def testLoop(self):
    self.assertEqual(
        Run('老张从1到3磨叽：唠唠：老张。磨叽完了。'),
        '1\n2\n3\n')

  def testRangeLoop(self):
    self.assertEqual(
        Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄来了个五。
张家庄来了个一。
老张在张家庄磨叽：
  唠唠：老张。
磨叽完了。
'''),
        '''2
5
1
''')

  def testLoopWithNoStatement(self):
    self.assertEqual(
        Run('老张从1到2磨叽：磨叽完了。'),
        '')

  def testLoopWithMultipleStatements(self):
    self.assertEqual(
        Run('老张从1到2磨叽：唠唠：老张。唠唠：老张加一。磨叽完了。'),
        '1\n2\n2\n3\n')

  def testLoopWithContinueAndBreak(self):
    self.assertEqual(
      Run('''
老张从一到十磨叽：
  寻思：老张跟二一样一样的？
  要行咧就接着磨叽。
  唠唠：“老张是”、老张。
  寻思：老张比五还大？
  要行咧就尥蹶子。
磨叽完了。
'''),
      '''老张是1
老张是3
老张是4
老张是5
老张是6
''')

  def testInfiniteLoop(self):
    self.assertEqual(
      Run('''
老王装一。
老张从一而终磨叽：
唠唠：老张、“和”、老王。
老王装老王加一。
寻思：老王比三还大？
要行咧就尥蹶子。
磨叽完了。
'''),
      '''1和1
1和2
1和3
''')

  def testInfiniteLoopEgg(self):
    self.assertEqual(
      Run('''
老王装一。
老张在苹果总部磨叽：
唠唠：老张、“和”、老王。
老王装老王加一。
寻思：老王比三还大？
要行咧就尥蹶子。
磨叽完了。
'''),
      '''1和1
1和2
1和3
''')

  def testLoopWithCompositeVariable(self):
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄的老大从一到三磨叽：
唠唠：张家庄。
磨叽完了。
'''),
      '''「1」
「2」
「3」
''')
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个二。
李家村都是活雷锋。
李家村来了个三。
李家村来了个五。
李家村来了个250。
张家庄的老大在李家村磨叽：
唠唠：张家庄。
磨叽完了。
'''),
      '''「3」
「5」
「250」
''')
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄的老大从一而终磨叽：
唠唠：张家庄。
尥蹶子。
磨叽完了。
'''),
      '''「1」
''')
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄的老大在苹果总部磨叽：
唠唠：张家庄。
尥蹶子。
磨叽完了。
'''),
      '''「1」
''')

  def testPrintBool(self):
    self.assertEqual(
        Run('老王是活雷锋。唠唠：老王。唠唠：老王啥也不是。'),
        '啥也不是\n没毛病\n')
    self.assertEqual(
        Run('唠唠：五比二还大。'),
        '没毛病\n')
    self.assertEqual(
        Run('唠唠：五比二还大、五比二还小、一跟2一样一样的、1跟二不是一样一样的。'),
        '没毛病有毛病有毛病没毛病\n')

  def testAssert(self):
    self.assertEqual(
      Run('''保准三加二比五减一还大。'''),
      '')
    self.assertEqual(
      Run('''保准三加二比五减一还小。'''),
      '''
整叉劈了：该着 3加2比5减1还小，咋有毛病了咧？
''')
    self.assertEqual(
      Run('''辟谣三加二比五减一还大。'''),
      '''
整叉劈了：3加2比5减1还大 不应该啊，咋有毛病了咧？
''')
    self.assertEqual(
      Run('''辟谣三加二比五减一还小。'''),
      '')

  def testRaise(self):
    self.assertEqual(
      Run('''整叉劈了：“小朋友请回避！”。'''),
     '''
整叉劈了：小朋友请回避！
''')
    self.assertEqual(
      Run('''小王装2。整叉劈了：小王、“小朋友请回避！”。'''),
     '''
整叉劈了：2小朋友请回避！
''')

  def testDelete(self):
    self.assertEqual(
      Run('老王是活雷锋。老王装二。削老王！唠唠：老王。'),
      '啥也不是\n')
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个二。
张家庄来了个三。
削张家庄的老大！
唠唠：张家庄。
'''),
      '「啥也不是, 3」\n')

  def testNumberLiteral(self):
    self.assertEqual(
      Run('唠唠：零。'),
      '0\n')
    self.assertEqual(
      Run('唠唠：鸭蛋。'),
      '0\n')
    self.assertEqual(
      Run('唠唠：一。'),
      '1\n')
    self.assertEqual(
      Run('唠唠：二。'),
      '2\n')
    self.assertEqual(
      Run('唠唠：两。'),
      '2\n')
    self.assertEqual(
      Run('唠唠：俩。'),
      '2\n')
    self.assertEqual(
      Run('唠唠：三。'),
      '3\n')
    self.assertEqual(
      Run('唠唠：仨。'),
      '3\n')
    self.assertEqual(
      Run('唠唠：四。'),
      '4\n')
    self.assertEqual(
      Run('唠唠：五。'),
      '5\n')
    self.assertEqual(
      Run('唠唠：六。'),
      '6\n')
    self.assertEqual(
      Run('唠唠：七。'),
      '7\n')
    self.assertEqual(
      Run('唠唠：八。'),
      '8\n')
    self.assertEqual(
      Run('唠唠：九。'),
      '9\n')
    self.assertEqual(
      Run('唠唠：十。'),
      '10\n')
    self.assertEqual(
      Run('唠唠：-10.5。'),
      '-10.5\n')
    self.assertEqual(
      Run('唠唠：5.。'),
      '5.0\n')
    self.assertEqual(
      Run('唠唠：-10。'),
      '-10\n')
    self.assertEqual(
      Run('唠唠：拉饥荒十。'),
      '-10\n')
    self.assertEqual(
      Run('唠唠：拉饥荒零。'),
      '0\n')

  def testArithmetic(self):
    self.assertEqual(
      Run('唠唠：五加二。'),
      '7\n')
    self.assertEqual(
      Run('唠唠：五减二。'),
      '3\n')
    self.assertEqual(
      Run('唠唠：五乘二。'),
      '10\n')
    self.assertEqual(
      Run('唠唠：十除以二。'),
      '5.0\n')
    self.assertEqual(
      Run('唠唠：十齐整整地除以三。'),
      '3\n')
    self.assertEqual(
      Run('唠唠：十刨掉一堆堆三。'),
      '1\n')
    self.assertEqual(
      Run('唠唠：十刨掉一堆堆五。'),
      '0\n')
    self.assertEqual(
      Run('唠唠：五加七乘二。'),
      '19\n')
    self.assertEqual(
      Run('唠唠：（五加七）乘二。'),
      '24\n')
    self.assertEqual(
      Run('唠唠：(五加七)乘二。'),
      '24\n')
    self.assertEqual(
      Run('唠唠：(五减（四减三）)乘二。'),
      '8\n')
    self.assertEqual(
      Run('唠唠：拉饥荒（五加二）。'),
      '-7\n')
    self.assertEqual(
      Run('''
      张家庄都是活雷锋。
      张家庄来了个42。
      唠唠：拉饥荒张家庄的老大。
      '''),
      '-42\n')

  def testConcat(self):
    self.assertEqual(
        Run('唠唠：“牛”、二。'),
        '牛2\n')
    self.assertEqual(
        Run('唠唠：“老王”、665加一。'),
        '老王666\n')

  def testCompound(self):
    self.assertEqual(
        Run('开整：整完了。'),
        '')
    self.assertEqual(
        Run('开整：唠唠：1。整完了。'),
        '1\n')
    self.assertEqual(
        Run('开整：唠唠：1。唠唠：2。整完了。'),
        '1\n2\n')

  def testRunConditional(self):
    self.assertEqual(
        Run('寻思：5比2还大？要行咧就唠唠：“OK”。'),
        'OK\n')
    self.assertEqual(
        Run('寻思：5比2还大？要行咧就开整：\n'
            '整完了。'),
        '')
    self.assertEqual(
        Run('寻思：5比2还大？\n'
            '要行咧就开整：\n'
            '    唠唠：5。\n'
            '整完了。'),
        '5\n')
    self.assertEqual(
        Run('寻思：5比6还大？要行咧就唠唠：“OK”。\n'
            '要不行咧就唠唠：“不OK”。'),
        '不OK\n')
    self.assertEqual(
        Run('寻思：5比6还大？\n'
            '要行咧就唠唠：“OK”。\n'
            '要不行咧就开整：\n'
            '  唠唠：“不OK”。\n'
            '  唠唠：“还是不OK”。\n'
            '整完了。'),
        '不OK\n还是不OK\n')
    # Else should match the last If.
    self.assertEqual(
        Run('''
          寻思：2比1还大？   # condition 1: True
          要行咧就寻思：2比3还大？  # condition 2: False
              要行咧就唠唠：“A”。  # for condition 2
              要不行咧就唠唠：“B”。# for condition 2
          '''),
        'B\n')

  def testRunFunc(self):
    self.assertEqual(
        Run('埋汰咋整：唠唠：“你虎了吧唧”。整完了。'),
        '')
    self.assertEqual(
        Run('埋汰咋整：唠唠：“你虎了吧唧”。整完了。整埋汰。'),
        '你虎了吧唧\n')

  def testFuncCallWithParam(self):
    self.assertEqual(
        Run('【加一】（那啥）咋整：唠唠：那啥加一。整完了。\n'
                    '整【加一】（五）。'),
        '6\n')

  def testFuncWithReturnValue(self):
    self.assertEqual(
        Run('【加一】（那啥）咋整：滚犊子吧那啥加一。整完了。\n'
                    '唠唠：整【加一】（二）。'),
        '3\n')

  def testNestedFunc(self):
    self.assertEqual(
      Run('''
写三三表咋整：
  老王从一到三磨叽：
    王三表咋整：  # 定义一个套在“写三三表”套路里的套路。
      老张从老王到三磨叽：  # 内层套路可以引用外层套路的活雷锋。
        唠唠：老王、“*”、老张、“=”、老王乘老张。
      磨叽完了。
    整完了。  # 内层套路定义结束。
    整王三表。  # 使用内层套路。
  磨叽完了。
整完了。

整写三三表。'''),
      '''1*1=1
1*2=2
1*3=3
2*2=4
2*3=6
3*3=9
''')
    
  def testArray(self):
    self.assertEqual(
        Run('''
张家庄都是活雷锋。  # 张家庄是个群众变量。初始值是「」。
唠唠：张家庄。
张家庄来了个二加三。  # 张家庄现在 = 「5」。
唠唠：张家庄。
张家庄来了个“大”。   # 张家庄现在 = 「5, '大'」
唠唠：张家庄。
唠唠：张家庄有几个坑。
唠唠：张家庄的老大。  # 第一个人（5）。
唠唠：张家庄的老（三减一）。  # 第二个人（'大'）。
唠唠：张家庄的老幺。  # 最后一个人（'大'）。
李家村都是活雷锋。  # 李家村也是个群众变量。初始值是「」。
李家村来了个三。  # 李家村现在 = 「3」。
李家村来了个张家庄。  # 群众的一个元素本身可以是群众。李家村现在 = 「3, 「5, '大'」」。
唠唠：李家村。
唠唠：李家村的老幺的老大。  # 5。
削张家庄。  # 张家庄现在啥也不是。
唠唠：张家庄。
'''),
        '''「」
「5」
「5, '大'」
2
5
大
大
「3, 「5, '大'」」
5
啥也不是
''')

  def testNestedArray(self):
    self.assertEqual(
      Run('''
      张家庄 装 「「一，二」，「三」」。
      唠唠：张家庄的老二的老大。
      '''),
      '''3
''')

  def testSubList(self):
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个三。
张家庄来了个五。
张家庄来了个六。
唠唠：张家庄掐头。
唠唠：张家庄去尾。
唠唠：张家庄。
'''),
          '''「5, 6」
「3, 5」
「3, 5, 6」
''')

  def testArrayAppend(self):
    self.assertEqual(
      Run('''
张家庄都是活雷锋。  # 「」
李家村都是活雷锋。  # 「」
李家村来了个张家庄。  # 「「」」
李家村的老大来了个五。  # 「「5」」
唠唠：张家庄。
唠唠：李家村。
'''),
      '''「5」
「「5」」
''')

  def testArrayExtend(self):
    self.assertEqual(
      Run('''
张家庄都是活雷锋。  # 「」
李家村都是活雷锋。  # 「」
李家村来了个二。  # 「2」
李家村来了个五。  # 「2, 5」
张家庄来了群李家村。 # 「2, 5」
张家庄来了群李家村。 # 「2, 5, 2, 5」
唠唠：张家庄。
'''),
      '''「2, 5, 2, 5」
''')

  def testArrayLiteral(self):
    self.assertEqual(
      Run('''
        张家庄 装 「」。
        唠唠：张家庄。
      '''),
      '「」\n')
    self.assertEqual(
      Run('''
        张家庄 装 路银「」。
        唠唠：张家庄。
      '''),
      '「」\n')
    self.assertEqual(
      Run('''
        张家庄 装 「1，二加三，五减一」。
        唠唠：张家庄。
      '''),
      '「1, 5, 4」\n')
    self.assertEqual(
      Run('''
        张家庄 都是活雷锋。
        张家庄 来了群 「1，二加三，五减一」。
        唠唠：张家庄。
        张家庄 来了群 「」。
        唠唠：张家庄。
        张家庄 来了群路银 「7，8」。
        唠唠：张家庄。
      '''),
      '''「1, 5, 4」
「1, 5, 4」
「1, 5, 4, 7, 8」
''')

  def testDel(self):
    self.assertTrue(
      '整叉劈了' in
      Run('''
老王是活雷锋。
炮决老王。
唠唠：老王。
'''))
    self.assertEqual(
      Run('''
张家庄都是活雷锋。
张家庄来了个五。
张家庄来了个六。
炮决张家庄的老大。
唠唠：张家庄。
'''),
      '''「6」
''')

  def testRecursiveFunc(self):
    self.assertEqual(
        Run('''
【阶乘】（那啥）咋整：
寻思：那啥比一还小？
要行咧就滚犊子吧一。
滚犊子吧那啥乘整【阶乘】（那啥减一）。
整完了。

唠唠：整【阶乘】（五）。
        '''),
        '120\n')

  def testMultiArgFunc(self):
    self.assertEqual(
        Run('''
求和（甲，乙）咋整：
  滚犊子吧 甲加乙。
整完了。

唠唠：整求和（五，七）。
        '''),
        '12\n')
    self.assertEqual(
        Run('''
求和（甲，乙）咋整：
  唠唠：甲加乙。
整完了。

整求和（五，七）。
        '''),
        '12\n')

  def testNormalizingBang(self):
    self.assertEqual(
        Run('【加一】（那啥）咋整：唠唠：那啥加一！整完了！\n'
                    '整【加一】（五）！'),
        '6\n')

  def testImport(self):
    self.assertEqual(
      Run('''
      翠花，上 re。
      寻思：整re.match（“a.*”，“abc”）？
      要行咧就唠唠：“OK”。
      '''),
      'OK\n')

  def testCommandLine(self):
    self.assertTrue(
      'dongbei_test.py' in
      Run('''唠唠：最高指示。'''))

  def testClassDef(self):
    self.assertEqual(
      TranslateDongbeiToPython('''
      无产阶级的接班银Foo阶级咋整：
      整完了。
      ''', None),
      '''class Foo:
  pass''')
    self.assertEqual(
      TranslateDongbeiToPython('''
      Xyz阶级的接班银Foo阶级咋整：
      整完了。
      ''', None),
      '''class Foo(Xyz):
  pass''')

  def testCtorDef(self):
    self.assertEqual(
      TranslateDongbeiToPython('''
      无产阶级的接班银有名阶级咋整：
        新对象咋整：
        整完了。
      整完了。
      ''', None),
      '''class 有名:

  def __init__(self):
    pass''')

    self.assertEqual(
      TranslateDongbeiToPython('''
      有名阶级的接班银特有名阶级咋整：
        新对象（名字）咋整：
          俺的名字装名字。
        整完了。
      整完了。
      ''', None),
      '''class 特有名(有名):

  def __init__(self, 名字):
    (self).名字 = 名字''')
  
  def testCtorCall(self):
    self.assertEqual(
      Run('''
      无产阶级的接班银有名阶级咋整：
        新对象咋整：
          俺的名字装“无名”。
        整完了。
      整完了。

      老林 装 有名 的新对象。
      唠唠：老林的名字。
      '''),
      '''无名
''')
    self.assertEqual(
      Run('''
      无产阶级的接班银有名阶级咋整：
        新对象（名字）咋整：
          俺的名字装名字。
        整完了。
      整完了。

      老林 装 有名 的新对象（“林蛋大”）。
      唠唠：老林的名字。
      '''),
      '''林蛋大
''')
  
  def testCallBaseCtor(self):
    self.assertEqual(
      Run('''
无产 阶级的接班银 有名 阶级咋整：
  新对象（名字）咋整：
    俺的名字 装 名字。
  整完了。
整完了。

有名 阶级的接班银 特有名 阶级咋整：
  新对象咋整：
    整 领导的新对象（“赵英俊”）。
    俺的 年龄 装 25。
  整完了。
整完了。

老赵 装 特有名 的新对象。
唠唠：老赵 的 名字。
唠唠：老赵 的 年龄。 
      '''),
      '''赵英俊
25
''')
    self.assertEqual(
      Run('''
无产 阶级的接班银 有名 阶级咋整：
  新对象咋整：
    俺的名字 装 “有名”。
  整完了。
整完了。

有名 阶级的接班银 特有名 阶级咋整：
  新对象咋整：
    整 领导的新对象。
  整完了。
整完了。

老赵 装 特有名 的新对象。
唠唠：老赵 的 名字。
      '''),
      '''有名
''')

  def testClassMethod(self):
    # Calling a method in an expression.
    self.assertEqual(
      Run('''
无产 阶级的接班银 有名 阶级咋整：
  新对象（名字）咋整：
    俺的名字 装 名字。
  整完了。

  显呗咋整：
    唠唠：“我你都不认识啊？我是那啥”、俺的名字、“！”。
    滚犊子吧 俺的名字！
  整完了。
整完了。

老赵 装 有名 的新对象（“赵英俊”）。
唠唠：老赵 整 显呗。 
      '''),
      '''我你都不认识啊？我是那啥赵英俊！
赵英俊
''')
    # Calling a method in a statement.
    self.assertEqual(
      Run('''
无产 阶级的接班银 有名 阶级咋整：
  新对象（名字）咋整：
    俺的名字 装 名字。
  整完了。

  显呗咋整：
    唠唠：“我你都不认识啊？我是那啥”、俺的名字、“！”。
    滚犊子吧 俺的名字！
  整完了。
整完了。

老赵 装 有名 的新对象（“赵英俊”）。
老赵 整 显呗。 
      '''),
      '''我你都不认识啊？我是那啥赵英俊！
''')

  def testBoolLiteral(self):
    self.assertEqual(
      Run('''
      老王 装 没毛病。
      寻思：老王？
      要行咧就 唠唠：“老王没毛病！”。
      '''),
      '''老王没毛病！
''')
    self.assertEqual(
      Run('''
      老王 装 有毛病。
      寻思：老王？
      要行咧就 唠唠：“老王没毛病！”。
      要不行咧就 唠唠：“老王有毛病！”。
      '''),
      '''老王有毛病！
''')

  def testNoneLiteral(self):
    self.assertEqual(
      Run('''
      老王 装 啥也不是。
      唠唠：老王。
      寻思：老王？
      要行咧就 唠唠：“老王没毛病！”。
      要不行咧就 唠唠：“老王有毛病！”。
      '''),
      '''啥也不是
老王有毛病！
''')

  def testTuple(self):
    self.assertEqual(
      Run('''
      老王装抱团。
      唠唠：老王。
      '''),
      '''（抱团）
''')
    self.assertEqual(
      Run('''
      老王装三加一抱团。
      唠唠：老王。
      '''),
      '''（4抱团）
''')
    self.assertEqual(
      Run('''
      老王装 四 跟 五 抱团。
      唠唠：老王。
      '''),
      '''（4跟5抱团）
''')
    self.assertEqual(
      Run('''
      老王装 四 跟 五 跟 七 抱团。
      唠唠：老王。
      '''),
      '''（4跟5跟7抱团）
''')
    self.assertEqual(
      Run('''
      老王装 四 跟 五跟二一样一样的 抱团。
      唠唠：老王。
      '''),
      '''（4跟有毛病抱团）
''')
    self.assertEqual(
      Run('''
      老王装 五减一 跟 五跟二一样一样的 抱团。
      唠唠：老王。
      '''),
      '''（4跟有毛病抱团）
''')
    self.assertEqual(
      Run('''
      老王装 五减一 跟 五跟二一样一样的 跟 七跟七一样一样的 抱团。
      唠唠：老王。
      '''),
      '''（4跟有毛病跟没毛病抱团）
''')
    self.assertEqual(
      Run('''
      老王 装 五减一 跟 五跟二一样一样的 抱团。
      老张 装 老王的老大。
      老李 装 老王的老二。
      唠唠：老王。
      唠唠：老王 有几个坑。
      唠唠：老张。
      唠唠：老李。
      '''),
      '''（4跟有毛病抱团）
2
4
有毛病
''')


if __name__ == '__main__':
  unittest.main()
