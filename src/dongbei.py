#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""dongbei语言执行器 {version}

用法：
    dongbei.py [--xudao] 源程序文件名...

要是命令行包含 --xudao（絮叨），在执行前先打印对应的 Python 代码。
"""

import io
import re
import sys

XUDAO_FLAG = '--xudao'
DONGBEI_VERSION = '0.0.5'

KW_APPEND = '来了个'
KW_ASSERT = '保准'
KW_ASSERT_FALSE = '辟谣'
KW_BANG = '！'
KW_BASE_INIT = '领导的新对象'
KW_BECOME = '装'
KW_BEGIN = '开整：'
KW_BREAK = '尥蹶子'
KW_CALL = '整'
KW_CHECK = '寻思：'
KW_CLASS = '阶级'
KW_CLOSE_BRACKET = '」'
KW_CLOSE_PAREN = '）'
KW_CLOSE_PAREN_NARROW = ')'
KW_CLOSE_QUOTE = '”'
KW_COLON = '：'
KW_COLON_NARROW = ':'
KW_COMMA = '，'
KW_COMMA_NARROW = ','
KW_COMPARE = '比'
KW_COMPARE_WITH = '跟'
KW_CONCAT = '、'
KW_CONTINUE = '接着磨叽'
KW_DEC = '稍稍'
KW_DEC_BY = '稍'
KW_DEL = '炮决'
KW_DOT = '的'
KW_SET_NONE = '削'
KW_DERIVED = '的接班银'
KW_DIVIDE_BY = '除以'
KW_ELSE = '要不行咧就'
KW_END = '整完了'
KW_END_LOOP = '磨叽完了'
KW_EQUAL = '一样一样的'
KW_EXTEND = '来了群'
KW_FROM = '从'
KW_DEF = '咋整：'
KW_GREATER = '还大'
KW_IMPORT = '翠花，上'
KW_IN = '在'
KW_INC = '走走'
KW_INC_BY = '走'
KW_INDEX_1 = '的老大'
KW_INDEX_LAST = '的老幺'
KW_INDEX = '的老'
KW_1_INFINITE_LOOP = '从一而终磨叽：'
KW_1_INFINITE_LOOP_EGG = '在苹果总部磨叽：'  # 彩蛋
KW_INTEGER_DIVIDE_BY = '齐整整地除以'
KW_IS_LIST = '都是活雷锋'
KW_IS_NONE = '啥也不是'
KW_IS_VAR = '是活雷锋'
KW_LENGTH = '有几个坑'
KW_LESS = '还小'
KW_LOOP = '磨叽：'
KW_MINUS = '减'
KW_MODULO = '刨掉一堆堆'
KW_NEGATE = '拉饥荒'
KW_NEW_OBJECT_OF = '的新对象'
KW_NOT_EQUAL = '不是一样一样的'
KW_OPEN_BRACKET = '「'
KW_OPEN_BRACKET_VERBOSE = '路银「'
KW_OPEN_PAREN = '（'
KW_OPEN_PAREN_NARROW = '('
KW_OPEN_QUOTE = '“'
KW_PERIOD = '。'
KW_PLUS = '加'
KW_RAISE = '整叉劈了：'
KW_REMOVE_HEAD = '掐头'
KW_REMOVE_TAIL = '去尾'
KW_RETURN = '滚犊子吧'
KW_SAY = '唠唠'
KW_STEP = '步'
KW_THEN = '？要行咧就'
KW_TIMES = '乘'
KW_TUPLE = '抱团'
KW_TO = '到'

KEYWORDS = (
  KW_APPEND,
  KW_ASSERT,
  KW_ASSERT_FALSE,
  KW_BANG,
  KW_BASE_INIT,
  KW_BECOME,
  KW_BEGIN,
  KW_BREAK,
  KW_CHECK,
  KW_CLASS,
  KW_CLOSE_BRACKET,
  KW_CLOSE_PAREN,
  KW_CLOSE_PAREN_NARROW,
  KW_CLOSE_QUOTE,
  KW_COLON,
  KW_COLON_NARROW,
  KW_COMMA,
  KW_COMMA_NARROW,
  KW_COMPARE,
  KW_COMPARE_WITH,
  KW_CONCAT,
  KW_CONTINUE,
  KW_DEC,
  KW_DEC_BY,
  KW_DEL,
  KW_DERIVED,
  KW_SET_NONE,
  KW_DIVIDE_BY,
  KW_ELSE,
  KW_EXTEND,
  KW_END,   # must match 整完了 before matching 整
  KW_RAISE,  # must match 整劈叉了 before matching 整
  KW_CALL,  # 整
  KW_END_LOOP,
  KW_EQUAL,
  KW_1_INFINITE_LOOP,  # must match 从一而终磨叽 before 从
  KW_FROM,
  KW_DEF,
  KW_GREATER,
  KW_IMPORT,
  KW_1_INFINITE_LOOP_EGG,  # must match 在苹果总部磨叽 before 在
  KW_IN,
  KW_INC,
  KW_INC_BY,
  KW_INDEX_1,  # must match 的老大 before 的老
  KW_INDEX_LAST,  # must match 的老幺 before 的老
  KW_INDEX,  # must match 的老 before 的
  KW_NEW_OBJECT_OF,  # must match 的新对象 before 的
  KW_DOT,
  KW_INTEGER_DIVIDE_BY,
  KW_IS_LIST,
  KW_IS_NONE,
  KW_IS_VAR,
  KW_LENGTH,
  KW_LESS,
  KW_LOOP,
  KW_MINUS,
  KW_MODULO,
  KW_NEGATE,
  KW_NOT_EQUAL,
  KW_OPEN_BRACKET,
  KW_OPEN_BRACKET_VERBOSE,
  KW_OPEN_PAREN,
  KW_OPEN_PAREN_NARROW,
  KW_OPEN_QUOTE,
  KW_PERIOD,
  KW_PLUS,
  KW_REMOVE_HEAD,
  KW_REMOVE_TAIL,
  KW_RETURN,
  KW_SAY,
  KW_STEP,
  KW_THEN,
  KW_TIMES,
  KW_TUPLE,
  KW_TO,
)

# Maps a keyword to its normalized form.
KEYWORD_TO_NORMALIZED_KEYWORD = {
  KW_BANG: KW_PERIOD,
  KW_OPEN_PAREN_NARROW: KW_OPEN_PAREN,
  KW_CLOSE_PAREN_NARROW: KW_CLOSE_PAREN,
  KW_COLON_NARROW: KW_COLON,
  KW_COMMA_NARROW: KW_COMMA,
  KW_OPEN_BRACKET_VERBOSE: KW_OPEN_BRACKET,
}

# Types of tokens.
TK_KEYWORD = 'KEYWORD'
TK_IDENTIFIER = 'IDENTIFIER'
TK_STRING_LITERAL = 'STRING'
TK_INTEGER_LITERAL = 'INTEGER'
TK_NONE_LITERAL = 'NONE'
TK_CHAR = 'CHAR'

# Statements.
STMT_APPEND = 'APPEND'
STMT_ASSERT = 'ASSERT'
STMT_ASSERT_FALSE = 'ASSERT_FALSE'
STMT_ASSIGN = 'ASSIGN'
STMT_BREAK = 'BREAK'
STMT_CALL = 'CALL'
STMT_CLASS_DEF = 'CLASS'
STMT_COMPOUND = 'COMPOUND'
STMT_CONDITIONAL = 'CONDITIONAL'
STMT_CONTINUE = 'CONTINUE'
STMT_DEC_BY = 'DEC_BY'
STMT_DEL = 'DEL'
STMT_SET_NONE = 'SET_NONE'
STMT_EXPR = 'EXPR'  # an expression statement
STMT_EXTEND = 'EXTEND'
STMT_FUNC_DEF = 'FUNC_DEF'
STMT_IMPORT = 'IMPORT'
STMT_INC_BY = 'INC_BY'
STMT_INFINITE_LOOP = 'INFINITE_LOOP'
STMT_LIST_VAR_DECL = 'LIST_VAR_DECL'
STMT_LOOP = 'LOOP'
STMT_RAISE = 'RAISE'
STMT_RANGE_LOOP = 'RANGE_LOOP'
STMT_RETURN = 'RETURN'
STMT_SAY = 'SAY'
STMT_VAR_DECL = 'VAR_DECL'

class _Dongbei_Error(Exception):
  """An error in a dongbei program."""

  def __init__(self, message):
    self.message = message

class Token:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return f'{self.kind} <{self.value}>'

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return (isinstance(other, Token) and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

def IdentifierToken(name):
  return Token(TK_IDENTIFIER, name)

class Expr:
  def __init__(self):
    pass

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return type(self) == type(other) and self.Equals(other)

  def Equals(self, other):
    """Returns true if self and other (which is guaranteed to have the same type) are equal."""
    raise Exception('%s must implement Equals().' % (type(self),))

  def __ne__(self, other):
    return not (self == other)

  def ToDongbei(self):
    """Returns the dongbei code for this expression."""
    raise Exception(f'{type(self)} must implement ToDongbei().')

  def ToPython(self):
    """Translates this expression to Python."""
    raise Exception('%s must implement ToPython().' % (type(self),))

def _dongbei_repr(value):
  """Converts a value to its dongbei repr."""
  if value is None:
    return KW_IS_NONE
  if type(value) == bool:
    return ID_TRUE if value else ID_FALSE
  if type(value) == list:
    return '「' + ', '.join(map(_dongbei_repr, value)) + '」'
  if type(value) == tuple:
    return f'（%s{KW_TUPLE}）' % (KW_COMPARE_WITH.join(_dongbei_repr(field) for field in value),)
  return repr(value)

def _dongbei_str(value):
  """Converts a value to its dongbei string."""
  if type(value) == str:
    return value
  return _dongbei_repr(value)

class ConcatExpr(Expr):
  def __init__(self, exprs):
    self.exprs = exprs

  def __str__(self):
    return 'CONCAT_EXPR<%s>' % (self.exprs,)

  def Equals(self, other):
    return self.exprs == other.exprs

  def ToDongbei(self):
    return KW_CONCAT.join(expr.ToDongbei() for expr in self.exprs)

  def ToPython(self):
    return ' + '.join('_dongbei_str(%s)' % (
        expr.ToPython(),) for expr in self.exprs)

class LengthExpr(Expr):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return f'LENGTH<{self.expr}>'

  def Equals(self, other):
    return self.expr == other.expr

  def ToDongbei(self):
    return f'{self.expr.ToDongbei()}{KW_LENGTH}'
  
  def ToPython(self):
    return f'len({self.expr.ToPython()})'

class NegateExpr(Expr):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return f'NEGATE<{self.expr}>'

  def Equals(self, other):
    return self.expr == other.expr

  def ToDongbei(self):
    code = self.expr.ToDongbei()
    return f'{KW_NEGATE} {code}'
  
  def ToPython(self):
    code = self.expr.ToPython()
    return f'-({code})'

class SubListExpr(Expr):
  def __init__(self, list, remove_at_head, remove_at_tail):
    self.list = list
    self.remove_at_head = remove_at_head
    self.remove_at_tail = remove_at_tail

  def __str__(self):
    return f'SUBLIST<{self.list}, {self.remove_at_head}, {self.remove_at_tail}>'

  def Equals(self, other):
    return (self.list == other.list and
            self.remove_at_head == other.remove_at_head and
            self.remove_at_tail == other.remove_at_tail)

  def ToDongbei(self):
    code = self.list.ToDongbei()
    if self.remove_at_head:
      code += KW_REMOVE_HEAD
    if self.remove_at_tail:
      code += KW_REMOVE_TAIL
    return code
  
  def ToPython(self):
    start_index = 1 if self.remove_at_head else 0
    end_index = -1 if self.remove_at_tail else None
    return f'({self.list.ToPython()})[{start_index} : {end_index}]'

class IndexExpr(Expr):
  def __init__(self, list_expr, index_expr):
    self.list_expr = list_expr
    self.index_expr = index_expr

  def __str__(self):
    return f'INDEX_EXPR<{self.list_expr}, {self.index_expr}>'

  def Equals(self, other):
    return self.list_expr == other.list_expr and self.index_expr == other.index_expr

  def ToDongbei(self):
    list_expr = self.list_expr.ToDongbei()
    index_expr = self.index_expr.ToDongbei()
    return f'{list_expr}{KW_INDEX}{index_expr}'

  def ToPython(self):
    return f'({self.list_expr.ToPython()})[({self.index_expr.ToPython()}) - 1]'

class ObjectPropertyExpr(Expr):
  def __init__(self, object, property):
    self.object = object
    self.property = property

  def __str__(self):
    return f'PROPERTY_EXPR<{self.object}, {self.property}>'

  def Equals(self, other):
    return self.object == other.object and self.property == other.property

  def ToDongbei(self):
    obj = self.object.ToDongbei()
    prop = f'【{self.property.value}】'
    return f'{obj}{KW_DOT}{prop}'

  def ToPython(self):
    obj = self.object.ToPython()
    prop = GetPythonVarName(self.property.value)
    return f'({obj}).{prop}'

class MethodCallExpr(Expr):
  def __init__(self, object, call_expr):
    self.object = object
    self.call_expr = call_expr

  def __str__(self):
    return f'METHOD_CALL_EXPR<{self.object}, {self.call_expr}>'

  def Equals(self, other):
    return self.object == other.object and self.call_expr == other.call_expr

  def ToDongbei(self):
    obj = self.object.ToDongbei()
    call = self.call_expr.ToDongbei()
    return obj + call

  def ToPython(self):
    obj = self.object.ToPython()
    call = self.call_expr.ToPython()
    return f'({obj}).{call}'

ARITHMETIC_OPERATION_TO_PYTHON = {
    KW_PLUS: '+',
    KW_MINUS: '-',
    KW_TIMES: '*',
    KW_DIVIDE_BY: '/',
    KW_INTEGER_DIVIDE_BY: '//',
    KW_MODULO: '%',
    }

class ArithmeticExpr(Expr):
  def __init__(self, op1, operation, op2):
    self.op1 = op1
    self.operation = operation
    self.op2 = op2

  def __str__(self):
    return 'ARITHMETIC_EXPR<%s, %s, %s>' % (
        self.op1, self.operation, self.op2)

  def Equals(self, other):
    return (self.op1 == other.op1 and
            self.operation == other.operation and
            self.op2 == other.op2)

  def ToDongbei(self):
    return f'{self.op1.ToDongbei()}{self.operation.value}{self.op2.ToDongbei()}'

  def ToPython(self):
    return '%s %s %s' % (self.op1.ToPython(),
                         ARITHMETIC_OPERATION_TO_PYTHON[
                             self.operation.value],
                         self.op2.ToPython())

class LiteralExpr(Expr):
  def __init__(self, token):
    self.token = token

  def __str__(self):
    return 'LITERAL_EXPR<%s>' % (self.token,)

  def Equals(self, other):
    return self.token == other.token

  def ToDongbei(self):
    if self.token.kind == TK_INTEGER_LITERAL:
      return str(self.token.value)
    if self.token.kind == TK_STRING_LITERAL:
      return '“%s”' % (self.token.value,)
    if self.token.kind == TK_NONE_LITERAL:
      return KW_IS_NONE
    raise Exception('Unexpected token kind %s' % (self.token.kind,))

  def ToPython(self):
    if self.token.kind == TK_INTEGER_LITERAL:
      return str(self.token.value)
    if self.token.kind == TK_STRING_LITERAL:
      return '"%s"' % (self.token.value,)
    if self.token.kind == TK_NONE_LITERAL:
      return 'None'
    raise Exception('Unexpected token kind %s' % (self.token.kind,))

class TupleExpr(Expr):
  def __init__(self, tuple):
    self.tuple = tuple

  def __str__(self):
    return 'TUPLE_EXPR<%s>' % (self.tuple,)

  def Equals(self, other):
    return self.tuple == other.tuple

  def ToDongbei(self):
    if not self.tuple:
      return KW_TUPLE

    return (KW_COMPARE_WITH.join(field.ToDongbei() for field in self.tuple) +
            KW_TUPLE)

  def ToPython(self):
    if len(self.tuple) == 1:
      return f'({self.tuple[0].ToPython()},)'
    
    return '(%s)' % (', '.join(field.ToPython() for field in self.tuple))

def IntegerLiteralExpr(value):
  return LiteralExpr(Token(TK_INTEGER_LITERAL, value))

def StringLiteralExpr(value):
  return LiteralExpr(Token(TK_STRING_LITERAL, value))

class VariableExpr(Expr):
  def __init__(self, var):
    self.var = var

  def __str__(self):
    return 'VARIABLE_EXPR<%s>' % (self.var,)

  def Equals(self, other):
    return self.var == other.var

  def ToDongbei(self):
    return f'【{self.var}】'

  def ToPython(self):
    return GetPythonVarName(self.var)

class ParenExpr(Expr):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return 'PAREN_EXPR<%s>' % (self.expr,)

  def Equals(self, other):
    return self.expr == other.expr

  def ToDongbei(self):
    return f'（{self.expr.ToDongbei()}）'

  def ToPython(self):
    return '(%s)' % (self.expr.ToPython(),)

class CallExpr(Expr):
  def __init__(self, func, args):
    self.func = func
    self.args = args

  def __str__(self):
    return 'CALL_EXPR<%s>(%s)' % (
        self.func, ', '.join(str(arg) for arg in self.args))

  def Equals(self, other):
    return (self.func == other.func and
            self.args == other.args)

  def ToDongbei(self):
    code = f'{KW_CALL}{self.func}'
    if self.args:
      code += '（' + '，'.join(arg.ToDongbei() for arg in self.args) + '）'
    return code

  def ToPython(self):
    return '%s(%s)' % (
        GetPythonVarName(self.func),
        ', '.join(arg.ToPython() for arg in self.args))

class NewObjectExpr(Expr):
  def __init__(self, class_id, args):
    self.class_id = class_id
    self.args = args

  def __str__(self):
    return 'NEW_OBJECT_EXPR<%s>(%s)' % (
        self.class_id, ', '.join(str(arg) for arg in self.args))

  def Equals(self, other):
    return (self.class_id == other.class_id and
            self.args == other.args)

  def ToDongbei(self):
    code = f'{self.class_id.value}{KW_NEW_OBJECT_OF}'
    if self.args:
      code += '（' + '，'.join(arg.ToDongbei() for arg in self.args) + '）'
    return code

  def ToPython(self):
    return '%s(%s)' % (
        GetPythonVarName(self.class_id.value),
        ', '.join(arg.ToPython() for arg in self.args))

class ListExpr(Expr):
  def __init__(self, exprs):
    self.exprs = exprs

  def __str__(self):
    return 'LIST(%s)' % (
        ', '.join(str(expr) for expr in self.exprs))

  def Equals(self, other):
    return self.exprs == other.exprs

  def ToDongbei(self):
    return (KW_OPEN_BRACKET +
            '，'.join(expr.ToDongbei() for expr in self.exprs) +
            KW_CLOSE_BRACKET)

  def ToPython(self):
    return '[%s]' % (
        ', '.join(expr.ToPython() for expr in self.exprs))

# Maps a dongbei comparison keyword to the Python version.
COMPARISON_KEYWORD_TO_PYTHON = {
    KW_GREATER: '>',
    KW_LESS: '<',
    KW_EQUAL: '==',
    KW_NOT_EQUAL: '!=',
    }

class ComparisonExpr(Expr):
  def __init__(self, op1, relation, op2):
    self.op1 = op1
    self.relation = relation
    self.op2 = op2

  def __str__(self):
    return 'COMPARISON_EXPR(%s, %s, %s)' % (
        self.op1, self.relation, self.op2)

  def Equals(self, other):
    return (self.op1 == other.op1 and
            self.relation == other.relation and
            self.op2 == other.op2)

  def ToDongbei(self):
    code = self.op1.ToDongbei()
    if self.relation.value == KW_IS_NONE:
      return code + KW_IS_NONE
    if self.relation.value in (KW_GREATER, KW_LESS):
      connector = KW_COMPARE
    else:
      connector = KW_COMPARE_WITH
    return code + connector + self.op2.ToDongbei() + self.relation.value

  def ToPython(self):
    if self.relation.value == KW_IS_NONE:
      return f'({self.op1.ToPython()}) is None'
    elif self.relation.value == KW_IS_VAR:
      if isinstance(self.op1, VariableExpr):
        return f'"{self.op1.var}" in locals()'
      else:
        return 'False'
    elif self.relation.value == KW_IS_LIST:
      return f'isinstance({self.op1.ToPython()}, list)'
    return '%s %s %s' % (self.op1.ToPython(),
                         COMPARISON_KEYWORD_TO_PYTHON[self.relation.value],
                         self.op2.ToPython())

class Statement:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    value_str = str(self.value)
    return '%s <%s>' % (self.kind, value_str)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return (isinstance(other, Statement) and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

def Keyword(str):
  """Returns a keyword token whose value is the given string."""
  return Token(TK_KEYWORD, str)

def TokenizeStringLiteralAndRest(code):
  """Returns a list of tokens."""

  tokens = []
  close_quote_pos = code.find(KW_CLOSE_QUOTE)
  if close_quote_pos < 0:
    tokens.append(Token(TK_STRING_LITERAL, code))
    return tokens

  tokens.append(Token(TK_STRING_LITERAL, code[:close_quote_pos]))
  tokens.append(Keyword(KW_CLOSE_QUOTE))
  tokens.extend(BasicTokenize(code[close_quote_pos + len(KW_CLOSE_QUOTE):]))
  return tokens

def SkipWhitespaceAndComment(code):
  while True:
    old_len = len(code)
    code = code.lstrip()
    if code.startswith('#'):  # comment
      code = re.sub(r'^.*', '', code)  # Ignore the comment line.
    if len(code) == old_len:  # cannot skip any further.
      return code

def TryParseKeyword(keyword, code):
  """Returns (parsed keyword string, remaining code)."""
  orig_code = code
  for char in keyword:
    code = SkipWhitespaceAndComment(code)
    if not code.startswith(char):
      return None, orig_code
    code = code[1:]
  return keyword, code

def BasicTokenize(code):
  """Returns a list of tokens from the dongbei code."""

  tokens = []
  code = SkipWhitespaceAndComment(code)
  if not code:
    return tokens

  # Parse 【标识符】.
  m = re.match('^(【(.*?)】)', code)
  if m:
    id = re.sub(r'\s+', '', m.group(2))  # Ignore whitespace.
    tokens.append(IdentifierToken(id))
    tokens.extend(BasicTokenize(code[len(m.group(1)):]))
    return tokens
    
  # Try to parse a keyword at the beginning of the code.
  for keyword in KEYWORDS:
    kw, remaining_code = TryParseKeyword(keyword, code)
    if kw:
      keyword = KEYWORD_TO_NORMALIZED_KEYWORD.get(keyword, keyword)
      last_token = Keyword(keyword)
      tokens.append(last_token)
      if last_token == Keyword(KW_OPEN_QUOTE):
        tokens.extend(TokenizeStringLiteralAndRest(remaining_code))
      else:
        tokens.extend(BasicTokenize(remaining_code.lstrip()))
      return tokens

  tokens.append(Token(TK_CHAR, code[0]))
  tokens.extend(BasicTokenize(code[1:]))
  return tokens
  

CHINESE_DIGITS = {
    '鸭蛋': 0,
    '零': 0,
    '一': 1,
    '二': 2,
    '俩': 2,
    '两': 2,
    '三': 3,
    '仨': 3,
    '四': 4,
    '五': 5,
    '六': 6,
    '七': 7,
    '八': 8,
    '九': 9,
    '十': 10,
    }

def TryParseInteger(str):
  """Returns (integer, remainder)."""

  m = re.match(r'^(-?[0-9]+)(.*)', str)
  if m:
    return int(m.group(1)), m.group(2)
  for chinese_digit, value in CHINESE_DIGITS.items():
    if str.startswith(chinese_digit):
      return value, str[len(chinese_digit):]
  return None, str
    
def TokenizeStrContainingNoKeyword(chars):
  """Returns a list of tokens."""
  tokens = []
  integer, rest = TryParseInteger(chars)
  if integer is not None:
    tokens.append(Token(TK_INTEGER_LITERAL, integer))
  if rest:
    tokens.append(IdentifierToken(rest))
  return tokens

class DongbeiParser(object):
  def __init__(self):
    self.code = None
    self.tokens = []  # remaining tokens

  def Tokenize(self, code, src_file=None):
    self.code = code
    return self._Tokenize()

  def _Tokenize(self):
    """Tokenizes self.code into tokens."""
    tokens = []
    last_token = Token(None, None)
    chars = ''
    for token in BasicTokenize(self.code):
      last_last_token = last_token
      last_token = token
      if token.kind == TK_CHAR:
        if last_last_token.kind == TK_CHAR:
          chars += token.value
          continue
        else:
          chars = token.value
          continue
      else:
        if last_last_token.kind == TK_CHAR:
          # A sequence of consecutive TK_CHARs ended.
          tokens.extend(TokenizeStrContainingNoKeyword(chars))
        tokens.append(token)
        chars = ''
    tokens.extend(TokenizeStrContainingNoKeyword(chars))
    return tokens

  def TranslateTokensToAst(self, tokens):
    self.tokens = tokens
    statements = self.ParseStmts()
    assert not self.tokens, ('多余符号：%s' % (self.tokens,))
    return statements

  def ParseStmts(self):
    """Returns a statement list, mutating self.tokens."""

    stmts = []
    while True:
      stmt = self.TryParseStmt()
      if not stmt:
        return stmts
      stmts.append(stmt)

  def TryParseStmt(self):
    """Returns statement, mutating self.tokens)."""

    orig_tokens = self.tokens

    # Parse 翠花，上
    imp = self.TryConsumeKeyword(KW_IMPORT)
    if imp:
      module = self.ConsumeTokenType(TK_IDENTIFIER)
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_IMPORT, module)

    # Parse 开整：
    begin = self.TryConsumeKeyword(KW_BEGIN)
    if begin:
      stmts = self.ParseStmts()
      if not stmts:
        stmts = []
      self.ConsumeKeyword(KW_END)
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_COMPOUND, stmts)

    # Parse 保准
    assert_ = self.TryConsumeKeyword(KW_ASSERT)
    if assert_:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_ASSERT, expr)

    # Parse 辟谣
    assert_ = self.TryConsumeKeyword(KW_ASSERT_FALSE)
    if assert_:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_ASSERT_FALSE, expr)

    # Parse 整叉劈了
    raise_ = self.TryConsumeKeyword(KW_RAISE)
    if raise_:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_RAISE, expr)

    # Parse 削：
    set_none = self.TryConsumeKeyword(KW_SET_NONE)
    if set_none:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_SET_NONE, expr)

    # Parse 炮决：
    del_ = self.TryConsumeKeyword(KW_DEL)
    if del_:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_DEL, expr)

    # Parse 唠唠：
    say = self.TryConsumeKeyword(KW_SAY)
    if say:
      self.ConsumeKeyword(KW_COLON)
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_SAY, expr)

    # Parse 整
    call_expr = self.TryParseCallExpr()
    if call_expr:
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_CALL, call_expr)

    # Parse 滚犊子吧
    ret = self.TryConsumeKeyword(KW_RETURN)
    if ret:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_RETURN, expr)

    # Parse 接着磨叽
    cont = self.TryConsumeKeyword(KW_CONTINUE)
    if cont:
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_CONTINUE, None)

    # Parse 尥蹶子
    break_ = self.TryConsumeKeyword(KW_BREAK)
    if break_:
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_BREAK, None)

    # Parse 寻思
    check = self.TryConsumeKeyword(KW_CHECK)
    if check:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_THEN)
      then_stmt = self.ParseStmt()
      # Parse the optional else-branch.
      kw_else = self.TryConsumeKeyword(KW_ELSE)
      if kw_else:
        else_stmt = self.ParseStmt()
      else:
        else_stmt = None
      return Statement(STMT_CONDITIONAL, (expr, then_stmt, else_stmt))

    func_def = self.TryParseFuncDef()
    if func_def:
      return func_def

    # Parse an identifier name.
    id = self.TryConsumeTokenType(TK_IDENTIFIER)
    if id:
      # Code below is for statements that start with an identifier.

      # Parse 是活雷锋
      is_var = self.TryConsumeKeyword(KW_IS_VAR)
      if is_var:
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_VAR_DECL, id)

      # Parse 都是活雷锋
      is_list = self.TryConsumeKeyword(KW_IS_LIST)
      if is_list:
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_LIST_VAR_DECL, id)

      # Parse 阶级
      class_ = self.TryConsumeKeyword(KW_CLASS)
      if class_:
        self.ConsumeKeyword(KW_DERIVED)
        subclass = self.ConsumeTokenType(TK_IDENTIFIER)
        self.ConsumeKeyword(KW_CLASS)
        self.ConsumeKeyword(KW_DEF)
        methods = self.ParseMethodDefs()
        self.ConsumeKeyword(KW_END)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_CLASS_DEF, (subclass, id, methods))

    self.tokens = orig_tokens
    expr1 = self.TryParseExpr()
    if expr1:
      # Code below is fof statements that start with an expression.
    
      # Parse 从...到...磨叽
      from_ = self.TryConsumeKeyword(KW_FROM)
      if from_:
        from_expr = self.ParseExpr()
        self.ConsumeKeyword(KW_TO)
        to_expr = self.ParseExpr()
        self.ConsumeKeyword(KW_LOOP)
        stmts = self.ParseStmts()
        self.ConsumeKeyword(KW_END_LOOP)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_LOOP, (expr1, from_expr, to_expr, stmts))

      # Parse 在...磨叽
      in_ = self.TryConsumeKeyword(KW_IN)
      if in_:
        range_expr = self.ParseExpr()
        self.ConsumeKeyword(KW_LOOP)
        stmts = self.ParseStmts()
        self.ConsumeKeyword(KW_END_LOOP)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_RANGE_LOOP, (expr1, range_expr, stmts))

      # Parse 从一而终磨叽 or the '1 Infinite Loop' 彩蛋
      infinite_loop = self.TryConsumeKeyword(KW_1_INFINITE_LOOP)
      if not infinite_loop:
        infinite_loop = self.TryConsumeKeyword(KW_1_INFINITE_LOOP_EGG)
      if infinite_loop:
        stmts = self.ParseStmts()
        self.ConsumeKeyword(KW_END_LOOP)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_INFINITE_LOOP, (expr1, stmts))

      # Parse 装
      become = self.TryConsumeKeyword(KW_BECOME)
      if become:
        expr = self.ParseExpr()
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_ASSIGN, (expr1, expr))

      # Parse 来了个
      append = self.TryConsumeKeyword(KW_APPEND)
      if append:
        expr = self.ParseExpr()
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_APPEND, (expr1, expr))

      # Parse 来了群
      extend = self.TryConsumeKeyword(KW_EXTEND)
      if extend:
        expr = self.ParseExpr()
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_EXTEND, (expr1, expr))

      # Parse 走走
      inc = self.TryConsumeKeyword(KW_INC)
      if inc:
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_INC_BY,
                         (expr1, IntegerLiteralExpr(1)))

      # Parse 走X步
      inc = self.TryConsumeKeyword(KW_INC_BY)
      if inc:
        expr = self.ParseExpr()
        self.ConsumeKeyword(KW_STEP)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_INC_BY, (expr1, expr))

      # Parse 稍稍
      dec = self.TryConsumeKeyword(KW_DEC)
      if dec:
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_DEC_BY,
                         (expr1, IntegerLiteralExpr(1)))

      # Parse 稍X步
      dec = self.TryConsumeKeyword(KW_DEC_BY)
      if dec:
        expr = self.ParseExpr()
        self.ConsumeKeyword(KW_STEP)
        self.ConsumeKeyword(KW_PERIOD)
        return Statement(STMT_DEC_BY, (expr1, expr))

      # Treat the expression as a statement.
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_EXPR, expr1)

    self.tokens = orig_tokens
    return None

  def TryConsumeKeyword(self, keyword):
    token = self.TryConsumeToken(Keyword(keyword))
    return token

  def TryParseObjectExpr(self):
    """Returns (expr, remaining tokens)."""

    # Do we see 抱团？
    tuple = self.TryConsumeKeyword(KW_TUPLE)
    if tuple:
      return TupleExpr(())
    
    # Do we see an integer literal?
    num = self.TryConsumeTokenType(TK_INTEGER_LITERAL)
    if num:
      return LiteralExpr(num)

    # Do we see a None literal?
    is_none = self.TryConsumeKeyword(KW_IS_NONE)
    if is_none:
      return LiteralExpr(Token(TK_NONE_LITERAL, None))

    # Do we see a string literal?
    open_quote = self.TryConsumeKeyword(KW_OPEN_QUOTE)
    if open_quote:
      str = self.ConsumeTokenType(TK_STRING_LITERAL)
      self.ConsumeKeyword(KW_CLOSE_QUOTE)
      return LiteralExpr(str)

    # Do we see an identifier?
    id = self.TryConsumeTokenType(TK_IDENTIFIER)
    if id:
      new_obj = self.TryConsumeKeyword(KW_NEW_OBJECT_OF)
      if not new_obj:
        return VariableExpr(id.value)
      args = []
      open_paren = self.TryConsumeKeyword(KW_OPEN_PAREN)
      if open_paren:
        args = self.ParseExprList()
        self.ConsumeKeyword(KW_CLOSE_PAREN)
      return NewObjectExpr(id, args)

    # Do we see a parenthesis?
    open_paren = self.TryConsumeKeyword(KW_OPEN_PAREN)
    if open_paren:
      expr = self.ParseExpr()
      self.ConsumeKeyword(KW_CLOSE_PAREN)
      return ParenExpr(expr)

    # Do we see a function call?
    call_expr = self.TryParseCallExpr()
    if call_expr:
      return call_expr
    
    # Do we see a list literal?
    open_bracket = self.TryConsumeKeyword(KW_OPEN_BRACKET)
    if open_bracket:
      exprs = self.ParseExprList()
      self.ConsumeKeyword(KW_CLOSE_BRACKET)
      return ListExpr(exprs)

    return None

  def TryParseAtomicExpr(self):
    negate = self.TryConsumeKeyword(KW_NEGATE)
    if negate:
      expr = self.TryParseAtomicExpr()
      return NegateExpr(expr)

    obj = self.TryParseObjectExpr()
    if not obj:
      return None

    expr = obj
    while True:
      pre_index_tokens = self.tokens

      # Parse 的老大
      index1 = self.TryConsumeKeyword(KW_INDEX_1)
      if index1:
        # dongbei 数组是从1开始的。
        expr = IndexExpr(expr, IntegerLiteralExpr(1))
        continue

      # Parse 的老幺
      index_last = self.TryConsumeKeyword(KW_INDEX_LAST)
      if index_last:
        # 0 - 1 = -1
        expr = IndexExpr(expr, IntegerLiteralExpr(0))
        continue

      # Parse 的老
      index = self.TryConsumeKeyword(KW_INDEX)
      if index:
        # Parse an ObjectExpr.
        obj = self.TryParseObjectExpr()
        if obj:
          expr = IndexExpr(expr, obj)
        else:
          # We have a trailing 的老 without an object expression to follow it.
          self.tokens = pre_index_tokens
          break

      # Parse 的
      dot = self.TryConsumeKeyword(KW_DOT)
      if dot:
        property_ = self.ConsumeTokenType(TK_IDENTIFIER)
        expr = ObjectPropertyExpr(expr, property_)
        continue

      # Parse method call.
      call = self.TryParseCallExpr()
      if call:
        expr = MethodCallExpr(expr, call)
        continue

      # Parse 有几个坑
      length = self.TryConsumeKeyword(KW_LENGTH)
      if length:
        expr = LengthExpr(expr)
        continue

      # Parse 掐头
      remove_head = self.TryConsumeKeyword(KW_REMOVE_HEAD)
      if remove_head:
        expr = SubListExpr(expr, 1, None)
        continue

      # Parse 去尾
      remove_tail = self.TryConsumeKeyword(KW_REMOVE_TAIL)
      if remove_tail:
        expr = SubListExpr(expr, None, 1)
        continue
      
      # Found neither 的老 or 有几个坑 after the expression.
      break

    return expr

  def TryParseTermExpr(self):
    factor = self.TryParseAtomicExpr()
    if not factor:
      return None

    factors = [factor]  # All factors of the term.
    operators = []  # Operators between the factors. The len of this is len(factors) - 1.

    while True:
      pre_operator_tokens = self.tokens
      operator = self.TryConsumeKeyword(KW_TIMES)
      if not operator:
        operator = self.TryConsumeKeyword(KW_DIVIDE_BY)
      if not operator:
        operator = self.TryConsumeKeyword(KW_INTEGER_DIVIDE_BY)
      if not operator:
        operator = self.TryConsumeKeyword(KW_MODULO)
      if not operator:
        break

      factor = self.TryParseAtomicExpr()
      if factor:
        operators.append(operator)
        factors.append(factor)
      else:
        # We have a trailing operator without a factor to follow it.
        self.tokens = pre_operator_tokens
        break

    assert len(factors) == len(operators) + 1
    expr = factors[0]
    for i, operator in enumerate(operators):
      expr = ArithmeticExpr(expr, operator, factors[i + 1])
    return expr

  def TryParseArithmeticExpr(self):
    term = self.TryParseTermExpr()
    if not term:
      return None

    terms = [term]  # All terms of the expression.
    operators = []  # Operators between the terms. The len of this is len(terms) - 1.

    while True:
      pre_operator_tokens = self.tokens
      operator = self.TryConsumeKeyword(KW_PLUS)
      if not operator:
        operator = self.TryConsumeKeyword(KW_MINUS)
      if not operator:
        break

      term = self.TryParseTermExpr()
      if term:
        operators.append(operator)
        terms.append(term)
      else:
        # We have a trailing operator without a term to follow it.
        self.tokens = pre_operator_tokens
        break

    assert len(terms) == len(operators) + 1
    expr = terms[0]
    for i, operator in enumerate(operators):
      expr = ArithmeticExpr(expr, operator, terms[i + 1])
    return expr

  def TryParseCallExpr(self):
    """Returns call_expr, mutating self.tokens."""
    call = self.TryConsumeKeyword(KW_CALL)
    if not call:
      return None

    base_init = self.TryConsumeKeyword(KW_BASE_INIT)
    if base_init:
      func_name = 'super().__init__'
    else:
      func = self.ConsumeTokenType(TK_IDENTIFIER)
      func_name = func.value

    open_paren = self.TryConsumeKeyword(KW_OPEN_PAREN)
    args = []
    if open_paren:
      args = self.ParseExprList()
      self.ConsumeKeyword(KW_CLOSE_PAREN)
    return CallExpr(func_name, args)
  
  def TryParseTupleExpr(self):
    orig_tokens = self.tokens
    expr = self.TryParseCompOrArithExpr()
    if not expr:
      self.tokens = orig_tokens
      return None

    # Do we see 抱团?
    tuple = self.TryConsumeKeyword(KW_TUPLE)
    if tuple:
      return TupleExpr((expr,))

    # Do we see 跟？
    and_ = self.TryConsumeKeyword(KW_COMPARE_WITH)
    if and_:
      rest_of_tuple = self.TryParseTupleExpr()
      if rest_of_tuple:
        return TupleExpr((expr,) + rest_of_tuple.tuple)

    self.tokens = orig_tokens
    return None

  def TryParseNonConcatExpr(self):
    tuple = self.TryParseTupleExpr()
    if tuple:
      return tuple
    expr = self.TryParseCompOrArithExpr()
    return expr

  def TryParseExpr(self):
    nc_expr = self.TryParseNonConcatExpr()
    if not nc_expr:
      return None

    nc_exprs = [nc_expr]
    while True:
      pre_operator_tokens = self.tokens
      concat = self.TryConsumeKeyword(KW_CONCAT)
      if not concat:
        break

      nc_expr = self.TryParseNonConcatExpr()
      if nc_expr:
        nc_exprs.append(nc_expr)
      else:
        # We have a trailing concat operator without an expression to follow it.
        self.tokens = pre_operator_tokens
        break

    if len(nc_exprs) == 1:
      return nc_exprs[0]

    return ConcatExpr(nc_exprs)

  def ParseExpr(self):
    expr = self.TryParseExpr()
    assert expr, '指望一个表达式，但是啥也没有；%s' % self.tokens[:5]
    return expr

  def TryParseCompOrArithExpr(self):
    arith = self.TryParseArithmeticExpr()
    if not arith:
      return None
    post_arith_tokens = self.tokens

    cmp = self.TryConsumeKeyword(KW_COMPARE)
    if cmp:
      arith2 = self.ParseArithmeticExpr()
      relation = self.TryConsumeKeyword(KW_GREATER)
      if not relation:
        relation = self.ConsumeKeyword(KW_LESS)
      return ComparisonExpr(arith, relation, arith2)

    cmp = self.TryConsumeKeyword(KW_COMPARE_WITH)
    if cmp:
      arith2 = self.TryParseArithmeticExpr()
      if not arith2:
        self.tokens = post_arith_tokens
        return arith
      relation = self.TryConsumeKeyword(KW_EQUAL)
      if not relation:
        relation = self.TryConsumeKeyword(KW_NOT_EQUAL)
        if not relation:
          self.tokens = post_arith_tokens
          return arith
      return ComparisonExpr(arith, relation, arith2)

    cmp = self.TryConsumeKeyword(KW_IS_NONE)
    if cmp:
      return ComparisonExpr(arith, Keyword(KW_IS_NONE), None)

    cmp = self.TryConsumeKeyword(KW_IS_VAR)
    if cmp:
      return ComparisonExpr(arith, Keyword(KW_IS_VAR), None)

    cmp = self.TryConsumeKeyword(KW_IS_LIST)
    if cmp:
      return ComparisonExpr(arith, Keyword(KW_IS_LIST), None)

    return arith

  def ParseArithmeticExpr(self):
    expr = self.TryParseArithmeticExpr()
    assert expr, '期望 ArithmeticExpr。落空了：%s' % (self.tokens[:5],)
    return expr

  def TryParseFuncDef(self, is_method=False):
    orig_tokens = self.tokens
    id = self.TryConsumeTokenType(TK_IDENTIFIER)
    if not id:
      return None

    open_paren = self.TryConsumeKeyword(KW_OPEN_PAREN)
    params = [IdentifierToken(ID_SELF)] if is_method else []
    if open_paren:
      while True:
        param = self.ConsumeTokenType(TK_IDENTIFIER)
        params.append(param)
        close_paren = self.TryConsumeKeyword(KW_CLOSE_PAREN)
        if close_paren:
          break
        self.ConsumeKeyword(KW_COMMA)
        
      func_def = self.ConsumeToken(Keyword(KW_DEF))
      stmts = self.ParseStmts()
      self.ConsumeKeyword(KW_END)
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_FUNC_DEF, (id, params, stmts))

    # not open_paren
    func_def = self.TryConsumeKeyword(KW_DEF)
    if func_def:
      stmts = self.ParseStmts()
      self.ConsumeKeyword(KW_END)
      self.ConsumeKeyword(KW_PERIOD)
      return Statement(STMT_FUNC_DEF, (id, params, stmts))

    self.tokens = orig_tokens
    return None

  def ParseMethodDefs(self):
    methods = []
    while True:
      method = self.TryParseFuncDef(is_method=True)
      if method:
        methods.append(method)
      else:
        return methods

  def ParseStmt(self):
    stmt = self.TryParseStmt()
    assert stmt, '期望语句，落空了：%s' % (self.tokens[:5],)
    return stmt

  def TryConsumeTokenType(self, tk_type):
    if not self.tokens:
      return None
    if self.tokens[0].kind == tk_type:
      token = self.tokens[0]
      self.tokens = self.tokens[1:]
      return token
    return None

  def ConsumeTokenType(self, tk_type):
    tk = self.TryConsumeTokenType(tk_type)
    if tk is None:
      sys.exit('期望 %s，实际是 %s' % (tk_type, self.tokens[0]))
    return tk
      
  def TryConsumeToken(self, token):
    if not self.tokens:
      return None
    if token != self.tokens[0]:
      return None
    self.tokens = self.tokens[1:]
    return token

  def ConsumeToken(self, token):
    if not self.tokens:
      sys.exit('语句结束太早。')
    if token != self.tokens[0]:
      sys.exit('期望符号 %s，实际却是 %s。' %
              (token, self.tokens[0]))
    self.tokens = self.tokens[1:]
    return token

  def ConsumeKeyword(self, keyword):
    return self.ConsumeToken(Keyword(keyword))

  def ParseExprList(self):
    """Parses a comma-separated expression list."""

    exprs = []
    tokens_after_expr_list = self.tokens
    while True:
      expr = self.TryParseExpr()
      tokens_after_expr_list = self.tokens
      if expr:
        exprs.append(expr)
      else:
        # Couldn't parse an expression.
        self.tokens = tokens_after_expr_list
        return exprs
      self.tokens = tokens_after_expr_list
      comma = self.TryConsumeKeyword(KW_COMMA)
      if not comma:
        self.tokens = tokens_after_expr_list
        return exprs

  # End of class DongbeiParser

ID_ARGV = '最高指示'
ID_INIT = '新对象'
ID_SELF = '俺'
ID_YOU_SAY = '你吱声'
ID_TRUE = '没毛病'
ID_FALSE = '有毛病'

# Maps a dongbei identifier to its corresponding Python identifier.
_dongbei_var_to_python_var = {
  ID_ARGV: 'sys.argv',
  ID_INIT: '__init__',
  ID_SELF: 'self',
  ID_YOU_SAY: 'input',
  ID_TRUE: 'True',
  ID_FALSE: 'False',
}

def GetPythonVarName(var):
  if var in _dongbei_var_to_python_var:
    return _dongbei_var_to_python_var[var]

  return var

# Expression grammar:
#
#   Expr ::= NonConcatExpr |
#            Expr 、 NonConcatExpr
#   NonConcatExpr ::= TupleExpr | CompOrArithExpr
#   CompOrArithExpr ::= ComparisonExpr | ArithmeticExpr
#   TupleExpr ::= CompOrArithExpr 抱团 |
#                 CompOrArithExpr 跟 TupleExpr
#   ComparisonExpr ::= ArithmeticExpr 比 ArithmeticExpr 还大 |
#                      ArithmeticExpr 比 ArithmeticExpr 还小 |
#                      ArithmeticExpr 跟 ArithmeticExpr 一样一样的 |
#                      ArithmeticExpr 跟 ArithmeticExpr 不是一样一样的
#   ArithmeticExpr ::= TermExpr |
#                      ArithmeticExpr 加 TermExpr |
#                      ArithmeticExpr 减 TermExpr
#   TermExpr ::= AtomicExpr |
#                TermExpr 乘 AtomicExpr |
#                TermExpr 除以 AtomicExpr |
#                TermExpr 齐整整地除以 AtomicExpr
#   AtomicExpr ::= ObjectExpr | AtomicExpr 的老 ObjectExpr | AtomicExpr 的 Identifier |
#                  AtomicExpr CallExpr | AtomicExpr 有几个坑 |
#                  AtomicExpr 掐头 | AtomicExpr 去尾 | NegateExpr
#   NegateExpr ::= 拉饥荒 AtomicExpr
#   ObjectExpr ::= 抱团 | LiteralExpr | VariableExpr | ParenExpr | CallExpr |
#                  「 ExprList 」 |
#                  Identifier 的新对象 | Identifier 的新对象（ExprList）
#   ParenExpr ::= （ Expr ）
#   CallExpr ::= 整 Identifier |
#                整 Identifier（ExprList）
#   ExprList ::= Expr |
#                Expr，ExprList

# Not meant to be in DongbeiParser.
def ParseExprFromStr(str):
  parser = DongbeiParser()
  parser.tokens = parser.Tokenize(str)
  return parser.ParseExpr(), parser.tokens

# Not meant to be in DongbeiParser.
def TryParseExprFromStr(str):
  parser = DongbeiParser()
  parser.tokens = parser.Tokenize(str)
  return parser.TryParseExpr(), parser.tokens

# Not meant to be in DongbeiParser.
def ParseStmtFromStr(str):
  parser = DongbeiParser()
  parser.tokens = parser.Tokenize(str)
  return parser.ParseStmt(), parser.tokens

def TranslateStatementToPython(stmt, indent = ''):
  """Translates the statements to Python code, without trailing newline."""
  
  if stmt.kind == STMT_VAR_DECL:
    var_token = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = None' % (var,)

  if stmt.kind == STMT_LIST_VAR_DECL:
    var_token = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = []' % (var,)

  if stmt.kind == STMT_ASSIGN:
    var_expr, expr = stmt.value
    var = var_expr.ToPython()
    return indent + '%s = %s' % (var, expr.ToPython())

  if stmt.kind == STMT_APPEND:
    var_expr, expr = stmt.value
    var = var_expr.ToPython()
    return indent + '(%s).append(%s)' % (var, expr.ToPython())

  if stmt.kind == STMT_EXTEND:
    var_expr, expr = stmt.value
    var = var_expr.ToPython()
    return indent + '(%s).extend(%s)' % (var, expr.ToPython())

  if stmt.kind == STMT_SAY:
    expr = stmt.value
    return indent + '_dongbei_print(%s)' % (expr.ToPython(),)

  if stmt.kind == STMT_INC_BY:
    var_expr, expr = stmt.value
    var = var_expr.ToPython()
    return indent + f'{var} += {expr.ToPython()}'

  if stmt.kind == STMT_DEC_BY:
    var_expr, expr = stmt.value
    var = var_expr.ToPython()
    return indent + '%s -= %s' % (var, expr.ToPython())

  if stmt.kind == STMT_LOOP:
    var_expr, from_val, to_val, stmts = stmt.value
    var = var_expr.ToPython()
    loop = indent + 'for %s in range(%s, (%s) + 1):' % (
        var, from_val.ToPython(),
        to_val.ToPython())
    for s in stmts:
      loop += '\n' + TranslateStatementToPython(s, indent + '  ')
    if not stmts:
      loop += '\n' + indent + '  pass'
    return loop

  if stmt.kind == STMT_RANGE_LOOP:
    var_expr, range_expr, stmts = stmt.value
    var = var_expr.ToPython()
    loop = indent + 'for %s in %s:' % (
        var, range_expr.ToPython())
    for s in stmts:
      loop += '\n' + TranslateStatementToPython(s, indent + '  ')
    if not stmts:
      loop += '\n' + indent + '  pass'
    return loop

  if stmt.kind == STMT_INFINITE_LOOP:
    var_expr, stmts = stmt.value
    var = var_expr.ToPython()
    loop = indent + 'for %s in _dongbei_1_infinite_loop():' % (var,)
    for s in stmts:
      loop += '\n' + TranslateStatementToPython(s, indent + '  ')
    if not stmts:
      loop += '\n' + indent + '  pass'
    return loop

  if stmt.kind == STMT_FUNC_DEF:
    func_token, params, stmts = stmt.value
    func_name = GetPythonVarName(func_token.value)
    param_names = map(lambda tk: GetPythonVarName(tk.value), params)
    code = indent + 'def %s(%s):' % (func_name, ', '.join(param_names))
    for s in stmts:
      code += '\n' + TranslateStatementToPython(s, indent + '  ')
    if not stmts:
      code += '\n' + indent + '  pass'
    return code

  if stmt.kind == STMT_CALL:
    func = stmt.value.func
    args = stmt.value.args
    func_name = GetPythonVarName(func)
    code = indent + '%s(%s)' % (func_name,
                                ', '.join(arg.ToPython() for arg in args))
    return code

  if stmt.kind == STMT_RETURN:
    return indent + 'return ' + stmt.value.ToPython()

  if stmt.kind == STMT_COMPOUND:
    code = indent + 'if True:'
    stmts = stmt.value
    if stmts:
      for s in stmts:
        code += '\n' + TranslateStatementToPython(s, indent + '  ')
    else:
      code += '\n' + indent + '  pass'
    return code

  if stmt.kind == STMT_CONDITIONAL:
    condition, then_stmt, else_stmt = stmt.value
    code = indent + 'if %s:\n' % (condition.ToPython(),)
    code += TranslateStatementToPython(then_stmt, indent + '  ')
    if else_stmt:
      code += '\n' + indent + 'else:\n'
      code += TranslateStatementToPython(else_stmt, indent + '  ')
    return code

  if stmt.kind == STMT_SET_NONE:
    return indent + stmt.value.ToPython() + ' = None'

  if stmt.kind == STMT_DEL:
    return indent + 'del ' + stmt.value.ToPython()

  if stmt.kind == STMT_IMPORT:
    return indent + f'import {stmt.value.value}'

  if stmt.kind == STMT_BREAK:
    return indent + 'break'

  if stmt.kind == STMT_CONTINUE:
    return indent + 'continue'

  if stmt.kind == STMT_ASSERT:
    return indent + f'assert {stmt.value.ToPython()}, "该着 {stmt.value.ToDongbei()}，咋有毛病了咧？"'

  if stmt.kind == STMT_ASSERT_FALSE:
    return indent + f'assert not ({stmt.value.ToPython()}), "{stmt.value.ToDongbei()} 不应该啊，咋有毛病了咧？"'

  if stmt.kind == STMT_RAISE:
    return indent + f'raise _Dongbei_Error({stmt.value.ToPython()})'

  if stmt.kind == STMT_CLASS_DEF:
    subclass, baseclass, methods = stmt.value
    baseclass_decl = ''
    if baseclass.value != '无产':
      baseclass_decl = '(' + GetPythonVarName(baseclass.value) + ')'
    code = indent + f'class {GetPythonVarName(subclass.value)}{baseclass_decl}:\n'
    if not methods:
      return code + indent + '  pass'
    for method in methods:
      code += '\n' + TranslateStatementToPython(method, indent + '  ')
    return code

  if stmt.kind == STMT_EXPR:
    return indent + stmt.value.ToPython()

  sys.exit('俺不懂 %s 语句咋执行。' % (stmt.kind))

# Not meant to be in DongbeiParser.
def ParseToAst(code):
  parser = DongbeiParser()
  tokens = parser.Tokenize(code)
  return parser.TranslateTokensToAst(tokens)

_dongbei_output = ''
def _dongbei_append_output(s):
  global _dongbei_output
  _dongbei_output += s

def _dongbei_print(value):
  s = _dongbei_str(value)
  print(s)
  _dongbei_append_output(s + '\n')

def _dongbei_1_infinite_loop():
  while True:
    yield 1

def TranslateDongbeiToPython(code, src_file=None):
  parser = DongbeiParser()
  tokens = parser.Tokenize(code, src_file)
  statements = parser.TranslateTokensToAst(tokens)

  py_code = []
  for s in statements:
    py_code.append(TranslateStatementToPython(s))
  return '\n'.join(py_code)

def Run(code, src_file=None, xudao=False):
  py_code = TranslateDongbeiToPython(code, src_file=src_file)
  if xudao:
    print('Python 代码：')
    print('%s' % (py_code,))
    print('运行结果：')
  global _dongbei_output
  _dongbei_output = ''
  # See https://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
  # Use the same dictionary for local and global definitions.
  # Needed for defining recursive dongbei functions.
  try:
    exec(py_code, globals(), globals())
  except Exception as e:
    _dongbei_print(f'\n整叉劈了：{e}')
  return _dongbei_output

def main():
  if len(sys.argv) == 1:
    sys.exit(__doc__.format(version=DONGBEI_VERSION))

  xudao = False
  if XUDAO_FLAG in sys.argv:
    xudao = True
    sys.argv.remove(XUDAO_FLAG)

  program = sys.argv[0]
  if program.endswith('.py') or program.endswith('/dongbei') or program == 'dongbei':
    # Running the program by explicitly invoking the interpreter.
    # Remove the interpreter name s.t. the dongbei program only sees the
    # name of itself as the program name.
    del sys.argv[0]
    program = sys.argv[0]
  
  with io.open(program, 'r', encoding='utf-8') as src_file:
    if xudao:
      print(f'执行 {program} ...')
    Run(src_file.read(), src_file=program, xudao=xudao)

if __name__ == '__main__':
  main()

