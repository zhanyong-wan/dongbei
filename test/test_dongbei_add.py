#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""dongbei语言特殊加法功能测试"""

import unittest
import sys
import os

# 添加src目录到路径，以便导入dongbei模块
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.dongbei import *


class TestDongbeiSpecialAddition(unittest.TestCase):
    """dongbei语言特殊加法功能测试类"""

    def test_dongbei_add_function_basic(self):
        """测试_dongbei_add函数基本功能"""
        # 测试数字加数字
        self.assertEqual(_dongbei_add(1, 2), 3)
        self.assertEqual(_dongbei_add(10, -5), 5)
        self.assertEqual(_dongbei_add(1.5, 2.5), 4.0)
        
        # 测试字符串加字符串
        self.assertEqual(_dongbei_add("a", "b"), "ab")
        self.assertEqual(_dongbei_add("东北", "话"), "东北话")
        
        # 测试字符串加数字
        self.assertEqual(_dongbei_add("a", 1), "a1")
        self.assertEqual(_dongbei_add("数字:", 42), "数字:42")
        
        # 测试数字加字符串
        self.assertEqual(_dongbei_add(1, "a"), "1a")
        self.assertEqual(_dongbei_add(3.14, "是圆周率"), "3.14是圆周率")
        
        # 测试混合类型
        self.assertEqual(_dongbei_add("结果:", 100), "结果:100")
        self.assertEqual(_dongbei_add(100, "分"), "100分")

    def test_dongbei_add_function_edge_cases(self):
        """测试_dongbei_add函数边界情况"""
        # 测试布尔值
        self.assertEqual(_dongbei_add("布尔:", True), "布尔:True")
        self.assertEqual(_dongbei_add(False, "是假"), "False是假")
        
        # 测试None
        self.assertEqual(_dongbei_add("空值:", None), "空值:None")
        
        # 测试列表
        self.assertEqual(_dongbei_add("列表:", [1, 2]), "列表:[1, 2]")
        
        # 测试零和空字符串
        self.assertEqual(_dongbei_add(0, "零"), "0零")
        self.assertEqual(_dongbei_add("", "空"), "空")
        self.assertEqual(_dongbei_add("前缀", ""), "前缀")

    def test_string_number_concatenation_in_expressions(self):
        """测试表达式中的字符串-数字拼接"""
        # 测试基本的字符串和数字加法
        code = """
唠唠："结果："加42。
"""
        output = TranslateAndRun(code, "test_string_number_concat")
        self.assertIn("结果:42", output)
        
        # 测试数字和字符串加法
        code = """
唠唠：100加"分"。
"""
        output = TranslateAndRun(code, "test_number_string_concat")
        self.assertIn("100分", output)
        
        # 测试多个拼接
        code = """
唠唠："第"加1加"名"。
"""
        output = TranslateAndRun(code, "test_multiple_concat")
        self.assertIn("第1名", output)

    def test_real_world_scenario(self):
        """测试真实场景：老王搬东西的例子"""
        code = """
老王是活雷锋。
老王装"a"。
老王加13。
老王加" 牛逼"。
唠唠：老王。
"""
        output = TranslateAndRun(code, "test_real_world")
        self.assertIn("a13 牛逼", output)

    def test_arithmetic_operation_mapping(self):
        """测试算术运算映射是否正确"""
        # 确保加法映射到我们的自定义函数
        self.assertEqual(ARITHMETIC_OPERATION_TO_PYTHON[KW_PLUS], "_dongbei_add")
        
        # 确保其他运算不受影响
        self.assertEqual(ARITHMETIC_OPERATION_TO_PYTHON[KW_MINUS], "-")
        self.assertEqual(ARITHMETIC_OPERATION_TO_PYTHON[KW_TIMES], "*")
        self.assertEqual(ARITHMETIC_OPERATION_TO_PYTHON[KW_DIVIDE_BY], "/")

    def test_arithmetic_expr_translation(self):
        """测试算术表达式翻译是否正确使用_dongbei_add"""
        # 测试加法表达式翻译
        expr = ArithmeticExpr(
            LiteralExpr(Token(TK_STRING_LITERAL, "a", None)),
            Keyword(KW_PLUS, None),
            LiteralExpr(Token(TK_NUMBER_LITERAL, 1, None))
        )
        
        python_code = expr.ToPython()
        self.assertEqual(python_code, '_dongbei_add("a", 1)')
        
        # 测试其他运算不受影响
        expr = ArithmeticExpr(
            LiteralExpr(Token(TK_NUMBER_LITERAL, 5, None)),
            Keyword(KW_MINUS, None),
            LiteralExpr(Token(TK_NUMBER_LITERAL, 3, None))
        )
        
        python_code = expr.ToPython()
        self.assertEqual(python_code, "5 - 3")

    def test_complex_concatenation_scenarios(self):
        """测试复杂拼接场景"""
        # 测试多个不同类型拼接
        code = """
【结果】装"分数："加95加"分，等级："加"A"。
唠唠：【结果】。
"""
        output = TranslateAndRun(code, "test_complex_concat")
        self.assertIn("分数:95分，等级:A", output)
        
        # 测试在循环中的拼接
        code = """
从1到3磨叽：
    唠唠："第"加【i】加"次循环"。
磨叽完了。
"""
        output = TranslateAndRun(code, "test_loop_concat")
        self.assertIn("第1次循环", output)
        self.assertIn("第2次循环", output)
        self.assertIn("第3次循环", output)

    def test_backwards_compatibility(self):
        """测试向后兼容性 - 确保纯数字加法仍然工作"""
        code = """
唠唠：1加2。
唠唠：3.5加2.5。
"""
        output = TranslateAndRun(code, "test_backwards_compat")
        # 纯数字加法应该仍然是数学加法
        self.assertIn("3", output)  # 1+2=3
        self.assertIn("6.0", output)  # 3.5+2.5=6.0


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
