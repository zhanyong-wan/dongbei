#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""dongbei语言执行器

用法：
    dongbei.py [--xudao] 源程序文件名...

要是命令行包含 --xudao（絮叨），在执行前先打印对应的 Python 代码。
"""

import io
import re
import sys

XUDAO_FLAG = '--xudao'

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
  close_quote_pos = code.find(KW_CLOSE_QUOTE)
  if close_quote_pos < 0:
    yield Token(TK_STRING_LITERAL, code)
    return

  yield Token(TK_STRING_LITERAL, code[:close_quote_pos])
  yield Keyword(KW_CLOSE_QUOTE)
  for tk in BasicTokenize(code[close_quote_pos + len(KW_CLOSE_QUOTE):]):
    yield tk    

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
  code = SkipWhitespaceAndComment(code)
  if not code:
    return

  # Parse 【标识符】.
  m = re.match('^(【(.*?)】)', code)
  if m:
    id = re.sub(r'\s+', '', m.group(2))  # Ignore whitespace.
    yield IdentifierToken(id)
    for tk in BasicTokenize(code[len(m.group(1)):]):
      yield tk
    return
    
  # Try to parse a keyword at the beginning of the code.
  for keyword in KEYWORDS:
    kw, remaining_code = TryParseKeyword(keyword, code)
    if kw:
      keyword = KEYWORD_TO_NORMALIZED_KEYWORD.get(keyword, keyword)
      last_token = Keyword(keyword)
      yield last_token
      if last_token == Keyword(KW_OPEN_QUOTE):
        for tk in TokenizeStringLiteralAndRest(remaining_code):
          yield tk
      else:
        for tk in BasicTokenize(remaining_code.lstrip()):
          yield tk
      return

  yield Token(TK_CHAR, code[0])
  for tk in BasicTokenize(code[1:]):
    yield tk
  

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
  integer, rest = TryParseInteger(chars)
  if integer is not None:
    yield Token(TK_INTEGER_LITERAL, integer)
  if rest:
    yield IdentifierToken(rest)

def Tokenize(code):
  last_token = Token(None, None)
  chars = ''
  for token in BasicTokenize(code):
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
        for tk in TokenizeStrContainingNoKeyword(chars):
          yield tk
      yield token
      chars = ''
  for tk in TokenizeStrContainingNoKeyword(chars):
    yield tk

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

def TryConsumeTokenType(tk_type, tokens):
  if not tokens:
    return None, tokens
  if tokens[0].kind == tk_type:
    return tokens[0], tokens[1:]
  return None, tokens

def ConsumeTokenType(tk_type, tokens):
  tk, tokens = TryConsumeTokenType(tk_type, tokens)
  if tk is None:
    sys.exit('期望 %s，实际是 %s' % (tk_type, tokens[0]))
  return tk, tokens
    
def TryConsumeToken(token, tokens):
  if not tokens:
    return None, tokens
  if token != tokens[0]:
    return None, tokens
  return token, tokens[1:]

def TryConsumeKeyword(keyword, tokens):
  return TryConsumeToken(Keyword(keyword), tokens)

def ConsumeToken(token, tokens):
  if not tokens:
    sys.exit('语句结束太早。')
  if token != tokens[0]:
    sys.exit('期望符号 %s，实际却是 %s。' %
             (token, tokens[0]))
  return token, tokens[1:]

def ConsumeKeyword(keyword, tokens):
  return ConsumeToken(Keyword(keyword), tokens)

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

def ParseExprList(tokens):
  """Parses a comma-separated expression list."""

  exprs = []
  tokens_after_expr_list = tokens
  while True:
    expr, tokens_after_expr_list = TryParseExpr(tokens)
    if expr:
      exprs.append(expr)
    else:
      # Couldn't parse an expression.
      return exprs, tokens_after_expr_list
    comma, tokens = TryConsumeKeyword(KW_COMMA, tokens_after_expr_list)
    if not comma:
      return exprs, tokens_after_expr_list

def TryParseCallExpr(tokens):
  """Returns (call_expr, remaining tokens)."""
  call, tokens = TryConsumeKeyword(KW_CALL, tokens)
  if not call:
    return None, tokens

  base_init, tokens = TryConsumeKeyword(KW_BASE_INIT, tokens)
  if base_init:
    func_name = 'super().__init__'
  else:
    func, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    func_name = func.value

  open_paren, tokens = TryConsumeKeyword(KW_OPEN_PAREN, tokens)
  args = []
  if open_paren:
    args, tokens = ParseExprList(tokens)
    _, tokens = ConsumeKeyword(KW_CLOSE_PAREN, tokens)
  return CallExpr(func_name, args), tokens
 
def TryParseObjectExpr(tokens):
  """Returns (expr, remaining tokens)."""

  # Do we see 抱团？
  tuple, tokens = TryConsumeKeyword(KW_TUPLE, tokens)
  if tuple:
    return TupleExpr(()), tokens
  
  # Do we see an integer literal?
  num, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if num:
    return LiteralExpr(num), tokens

  # Do we see a None literal?
  is_none, tokens = TryConsumeKeyword(KW_IS_NONE, tokens)
  if is_none:
    return LiteralExpr(Token(TK_NONE_LITERAL, None)), tokens

  # Do we see a string literal?
  open_quote, tokens = TryConsumeKeyword(KW_OPEN_QUOTE, tokens)
  if open_quote:
    str, tokens = ConsumeTokenType(TK_STRING_LITERAL, tokens)
    _, tokens = ConsumeKeyword(KW_CLOSE_QUOTE, tokens)
    return LiteralExpr(str), tokens

  # Do we see an identifier?
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if id:
    new_obj, tokens = TryConsumeKeyword(KW_NEW_OBJECT_OF, tokens)
    if not new_obj:
      return VariableExpr(id.value), tokens
    args = []
    open_paren, tokens = TryConsumeKeyword(KW_OPEN_PAREN, tokens)
    if open_paren:
      args, tokens = ParseExprList(tokens)
      _, tokens = ConsumeKeyword(KW_CLOSE_PAREN, tokens)
    return NewObjectExpr(id, args), tokens

  # Do we see a parenthesis?
  open_paren, tokens = TryConsumeKeyword(KW_OPEN_PAREN, tokens)
  if open_paren:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_CLOSE_PAREN, tokens)
    return ParenExpr(expr), tokens

  # Do we see a function call?
  call_expr, tokens = TryParseCallExpr(tokens)
  if call_expr:
    return call_expr, tokens
  
  # Do we see a list literal?
  open_bracket, tokens = TryConsumeKeyword(KW_OPEN_BRACKET, tokens)
  if open_bracket:
    exprs, tokens = ParseExprList(tokens)
    _, tokens = ConsumeKeyword(KW_CLOSE_BRACKET, tokens)
    return ListExpr(exprs), tokens

  return None, tokens

def TryParseAtomicExpr(tokens):
  negate, tokens = TryConsumeKeyword(KW_NEGATE, tokens)
  if negate:
    expr, tokens = TryParseAtomicExpr(tokens)
    return NegateExpr(expr), tokens

  obj, tokens = TryParseObjectExpr(tokens)
  if not obj:
    return None, tokens

  expr = obj
  while True:
    pre_index_tokens = tokens

    # Parse 的老大
    index1, tokens = TryConsumeKeyword(KW_INDEX_1, tokens)
    if index1:
      # dongbei 数组是从1开始的。
      expr = IndexExpr(expr, IntegerLiteralExpr(1))
      continue

    # Parse 的老幺
    index_last, tokens = TryConsumeKeyword(KW_INDEX_LAST, tokens)
    if index_last:
      # 0 - 1 = -1
      expr = IndexExpr(expr, IntegerLiteralExpr(0))
      continue

    # Parse 的老
    index, tokens = TryConsumeKeyword(KW_INDEX, tokens)
    if index:
      # Parse an ObjectExpr.
      obj, tokens = TryParseObjectExpr(tokens)
      if obj:
        expr = IndexExpr(expr, obj)
      else:
        # We have a trailing 的老 without an object expression to follow it.
        tokens = pre_index_tokens
        break

    # Parse 的
    dot, tokens = TryConsumeKeyword(KW_DOT, tokens)
    if dot:
      property_, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
      expr = ObjectPropertyExpr(expr, property_)
      continue

    # Parse method call.
    call, tokens = TryParseCallExpr(tokens)
    if call:
      expr = MethodCallExpr(expr, call)
      continue

    # Parse 有几个坑
    length, tokens = TryConsumeKeyword(KW_LENGTH, tokens)
    if length:
      expr = LengthExpr(expr)
      continue

    # Parse 掐头
    remove_head, tokens = TryConsumeKeyword(KW_REMOVE_HEAD, tokens)
    if remove_head:
      expr = SubListExpr(expr, 1, None)
      continue

    # Parse 去尾
    remove_tail, tokens = TryConsumeKeyword(KW_REMOVE_TAIL, tokens)
    if remove_tail:
      expr = SubListExpr(expr, None, 1)
      continue
    
    # Found neither 的老 or 有几个坑 after the expression.
    break

  return expr, tokens

def TryParseTermExpr(tokens):
  factor, tokens = TryParseAtomicExpr(tokens)
  if not factor:
    return None, tokens

  factors = [factor]  # All factors of the term.
  operators = []  # Operators between the factors. The len of this is len(factors) - 1.

  while True:
    pre_operator_tokens = tokens
    operator, tokens = TryConsumeKeyword(KW_TIMES, tokens)
    if not operator:
      operator, tokens = TryConsumeKeyword(KW_DIVIDE_BY, tokens)
    if not operator:
      operator, tokens = TryConsumeKeyword(KW_INTEGER_DIVIDE_BY, tokens)
    if not operator:
      operator, tokens = TryConsumeKeyword(KW_MODULO, tokens)
    if not operator:
      break

    factor, tokens = TryParseAtomicExpr(tokens)
    if factor:
      operators.append(operator)
      factors.append(factor)
    else:
      # We have a trailing operator without a factor to follow it.
      tokens = pre_operator_tokens
      break

  assert len(factors) == len(operators) + 1
  expr = factors[0]
  for i, operator in enumerate(operators):
    expr = ArithmeticExpr(expr, operator, factors[i + 1])
  return expr, tokens

def TryParseArithmeticExpr(tokens):
  term, tokens = TryParseTermExpr(tokens)
  if not term:
    return None, tokens

  terms = [term]  # All terms of the expression.
  operators = []  # Operators between the terms. The len of this is len(terms) - 1.

  while True:
    pre_operator_tokens = tokens
    operator, tokens = TryConsumeKeyword(KW_PLUS, tokens)
    if not operator:
      operator, tokens = TryConsumeKeyword(KW_MINUS, tokens)
    if not operator:
      break

    term, tokens = TryParseTermExpr(tokens)
    if term:
      operators.append(operator)
      terms.append(term)
    else:
      # We have a trailing operator without a term to follow it.
      tokens = pre_operator_tokens
      break

  assert len(terms) == len(operators) + 1
  expr = terms[0]
  for i, operator in enumerate(operators):
    expr = ArithmeticExpr(expr, operator, terms[i + 1])
  return expr, tokens

def ParseArithmeticExpr(tokens):
  expr, tokens = TryParseArithmeticExpr(tokens)
  assert expr, '期望 ArithmeticExpr。落空了：%s' % (tokens[:5],)
  return expr, tokens

def TryParseCompOrArithExpr(tokens):
  arith, tokens = TryParseArithmeticExpr(tokens)
  if not arith:
    return None, tokens
  post_arith_tokens = tokens

  cmp, tokens = TryConsumeKeyword(KW_COMPARE, tokens)
  if cmp:
    arith2, tokens = ParseArithmeticExpr(tokens)
    relation, tokens = TryConsumeKeyword(KW_GREATER, tokens)
    if not relation:
      relation, tokens = ConsumeKeyword(KW_LESS, tokens)
    return ComparisonExpr(arith, relation, arith2), tokens

  cmp, tokens = TryConsumeKeyword(KW_COMPARE_WITH, tokens)
  if cmp:
    arith2, tokens = TryParseArithmeticExpr(tokens)
    if not arith2:
      return arith, post_arith_tokens
    relation, tokens = TryConsumeKeyword(KW_EQUAL, tokens)
    if not relation:
      relation, tokens = TryConsumeKeyword(KW_NOT_EQUAL, tokens)
      if not relation:
        return arith, post_arith_tokens
    return ComparisonExpr(arith, relation, arith2), tokens

  cmp, tokens = TryConsumeKeyword(KW_IS_NONE, tokens)
  if cmp:
    return ComparisonExpr(arith, Keyword(KW_IS_NONE), None), tokens

  return arith, tokens

def TryParseTupleExpr(tokens):
  orig_tokens = tokens
  expr, tokens = TryParseCompOrArithExpr(tokens)
  if not expr:
    return None, orig_tokens

  # Do we see 抱团?
  tuple, tokens = TryConsumeKeyword(KW_TUPLE, tokens)
  if tuple:
    return TupleExpr((expr,)), tokens

  # Do we see 跟？
  and_, tokens = TryConsumeKeyword(KW_COMPARE_WITH, tokens)
  if and_:
    rest_of_tuple, tokens = TryParseTupleExpr(tokens)
    if rest_of_tuple:
      return TupleExpr((expr,) + rest_of_tuple.tuple), tokens

  return None, orig_tokens

def TryParseNonConcatExpr(tokens):
  tuple, tokens = TryParseTupleExpr(tokens)
  if tuple:
    return tuple, tokens
  return TryParseCompOrArithExpr(tokens)

def TryParseExpr(tokens):
  nc_expr, tokens = TryParseNonConcatExpr(tokens)
  if not nc_expr:
    return None, tokens

  nc_exprs = [nc_expr]
  while True:
    pre_operator_tokens = tokens
    concat, tokens = TryConsumeKeyword(KW_CONCAT, tokens)
    if not concat:
      break

    nc_expr, tokens = TryParseNonConcatExpr(tokens)
    if nc_expr:
      nc_exprs.append(nc_expr)
    else:
      # We have a trailing concat operator without an expression to follow it.
      tokens = pre_operator_tokens
      break

  if len(nc_exprs) == 1:
    return nc_exprs[0], tokens

  return ConcatExpr(nc_exprs), tokens

def ParseExpr(tokens):
  expr, tokens = TryParseExpr(tokens)
  assert expr, '指望一个表达式，但是啥也没有；%s' % tokens[:5]
  return expr, tokens

def ParseExprFromStr(str):
  return ParseExpr(list(Tokenize(str)))

def TryParseExprFromStr(str):
  return TryParseExpr(list(Tokenize(str)))

def TryParseFuncDef(tokens, is_method=False):
  orig_tokens = tokens
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if not id:
    return None, tokens

  open_paren, tokens = TryConsumeKeyword(KW_OPEN_PAREN, tokens)
  params = [IdentifierToken(ID_SELF)] if is_method else []
  if open_paren:
    while True:
      param, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
      params.append(param)
      close_paren, tokens = TryConsumeKeyword(KW_CLOSE_PAREN, tokens)
      if close_paren:
        break
      _, tokens = ConsumeKeyword(KW_COMMA, tokens)
      
    func_def, tokens = ConsumeToken(
        Keyword(KW_DEF), tokens)
    stmts, tokens = ParseStmts(tokens)
    _, tokens = ConsumeKeyword(KW_END, tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_FUNC_DEF, (id, params, stmts)), tokens

  # not open_paren
  func_def, tokens = TryConsumeKeyword(KW_DEF, tokens)
  if func_def:
    stmts, tokens = ParseStmts(tokens)
    _, tokens = ConsumeKeyword(KW_END, tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_FUNC_DEF, (id, params, stmts)), tokens

  return None, orig_tokens

def ParseMethodDefs(tokens):
  methods = []
  while True:
    method, tokens = TryParseFuncDef(tokens, is_method=True)
    if method:
      methods.append(method)
    else:
      return methods, tokens

def TryParseStmt(tokens):
  """Returns (statement, remainding_tokens)."""

  orig_tokens = tokens

  # Parse 翠花，上
  imp, tokens = TryConsumeKeyword(KW_IMPORT, tokens)
  if imp:
    module, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_IMPORT, module), tokens

  # Parse 开整：
  begin, tokens = TryConsumeKeyword(KW_BEGIN, tokens)
  if begin:
    stmts, tokens = ParseStmts(tokens)
    if not stmts:
      stmts = []
    _, tokens = ConsumeKeyword(KW_END, tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_COMPOUND, stmts), tokens

  # Parse 保准
  assert_, tokens = TryConsumeKeyword(KW_ASSERT, tokens)
  if assert_:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_ASSERT, expr), tokens

  # Parse 辟谣
  assert_, tokens = TryConsumeKeyword(KW_ASSERT_FALSE, tokens)
  if assert_:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_ASSERT_FALSE, expr), tokens

  # Parse 整叉劈了
  raise_, tokens = TryConsumeKeyword(KW_RAISE, tokens)
  if raise_:
    print(tokens)
    expr, tokens = ParseExpr(tokens)
    print(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_RAISE, expr), tokens

  # Parse 削：
  set_none, tokens = TryConsumeKeyword(KW_SET_NONE, tokens)
  if set_none:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_SET_NONE, expr), tokens

  # Parse 炮决：
  del_, tokens = TryConsumeKeyword(KW_DEL, tokens)
  if del_:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_DEL, expr), tokens

  # Parse 唠唠：
  say, tokens = TryConsumeKeyword(KW_SAY, tokens)
  if say:
    colon, tokens = ConsumeKeyword(KW_COLON, tokens)
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_SAY, expr), tokens

  # Parse 整
  call_expr, tokens = TryParseCallExpr(tokens)
  if call_expr:
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_CALL, call_expr), tokens

  # Parse 滚犊子吧
  ret, tokens = TryConsumeKeyword(KW_RETURN, tokens)
  if ret:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_RETURN, expr), tokens

  # Parse 接着磨叽
  cont, tokens = TryConsumeKeyword(KW_CONTINUE, tokens)
  if cont:
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_CONTINUE, None), tokens

  # Parse 尥蹶子
  break_, tokens = TryConsumeKeyword(KW_BREAK, tokens)
  if break_:
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_BREAK, None), tokens

  # Parse 寻思
  check, tokens = TryConsumeKeyword(KW_CHECK, tokens)
  if check:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeKeyword(KW_THEN, tokens)
    then_stmt, tokens = ParseStmt(tokens)
    # Parse the optional else-branch.
    kw_else, tokens = TryConsumeKeyword(KW_ELSE, tokens)
    if kw_else:
      else_stmt, tokens = ParseStmt(tokens)
    else:
      else_stmt = None
    return Statement(STMT_CONDITIONAL, (expr, then_stmt, else_stmt)), tokens

  func_def, tokens = TryParseFuncDef(tokens)
  if func_def:
    return func_def, tokens

  # Parse an identifier name.
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)

  if id:
    # Code below is for statements that start with an identifier.

    # Parse 是活雷锋
    is_var, tokens = TryConsumeKeyword(KW_IS_VAR, tokens)
    if is_var:
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_VAR_DECL, id), tokens

    # Parse 都是活雷锋
    is_list, tokens = TryConsumeKeyword(KW_IS_LIST, tokens)
    if is_list:
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_LIST_VAR_DECL, id), tokens

    # Parse 阶级
    class_, tokens = TryConsumeKeyword(KW_CLASS, tokens)
    if class_:
      _, tokens = ConsumeKeyword(KW_DERIVED, tokens)
      subclass, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
      _, tokens = ConsumeKeyword(KW_CLASS, tokens)
      _, tokens = ConsumeKeyword(KW_DEF, tokens)
      methods, tokens = ParseMethodDefs(tokens)
      _, tokens = ConsumeKeyword(KW_END, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_CLASS_DEF, (subclass, id, methods)), tokens

  expr1, tokens = TryParseExpr(orig_tokens)
  if expr1:
    # Code below is fof statements that start with an expression.
  
    # Parse 从...到...磨叽
    from_, tokens = TryConsumeKeyword(KW_FROM, tokens)
    if from_:
      from_expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_TO, tokens)
      to_expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_LOOP, tokens)
      stmts, tokens = ParseStmts(tokens)
      _, tokens = ConsumeKeyword(KW_END_LOOP, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_LOOP, (expr1, from_expr, to_expr, stmts)), tokens

    # Parse 在...磨叽
    in_, tokens = TryConsumeKeyword(KW_IN, tokens)
    if in_:
      range_expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_LOOP, tokens)
      stmts, tokens = ParseStmts(tokens)
      _, tokens = ConsumeKeyword(KW_END_LOOP, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_RANGE_LOOP, (expr1, range_expr, stmts)), tokens

    # Parse 从一而终磨叽 or the '1 Infinite Loop' 彩蛋
    infinite_loop, tokens = TryConsumeKeyword(KW_1_INFINITE_LOOP, tokens)
    if not infinite_loop:
      infinite_loop, tokens = TryConsumeKeyword(KW_1_INFINITE_LOOP_EGG, tokens)
    if infinite_loop:
      stmts, tokens = ParseStmts(tokens)
      _, tokens = ConsumeKeyword(KW_END_LOOP, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_INFINITE_LOOP, (expr1, stmts)), tokens

    # Parse 装
    become, tokens = TryConsumeKeyword(KW_BECOME, tokens)
    if become:
      expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_ASSIGN, (expr1, expr)), tokens

    # Parse 来了个
    append, tokens = TryConsumeKeyword(KW_APPEND, tokens)
    if append:
      expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_APPEND, (expr1, expr)), tokens

    # Parse 来了群
    extend, tokens = TryConsumeKeyword(KW_EXTEND, tokens)
    if extend:
      expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_EXTEND, (expr1, expr)), tokens

    # Parse 走走
    inc, tokens = TryConsumeKeyword(KW_INC, tokens)
    if inc:
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return (Statement(STMT_INC_BY,
                        (expr1, IntegerLiteralExpr(1))),
              tokens)

    # Parse 走X步
    inc, tokens = TryConsumeKeyword(KW_INC_BY, tokens)
    if inc:
      expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_STEP, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_INC_BY, (expr1, expr)), tokens

    # Parse 稍稍
    dec, tokens = TryConsumeKeyword(KW_DEC, tokens)
    if dec:
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return (Statement(STMT_DEC_BY,
                        (expr1, IntegerLiteralExpr(1))),
              tokens)

    # Parse 稍X步
    dec, tokens = TryConsumeKeyword(KW_DEC_BY, tokens)
    if dec:
      expr, tokens = ParseExpr(tokens)
      _, tokens = ConsumeKeyword(KW_STEP, tokens)
      _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
      return Statement(STMT_DEC_BY, (expr1, expr)), tokens

    # Treat the expression as a statement.
    _, tokens = ConsumeKeyword(KW_PERIOD, tokens)
    return Statement(STMT_EXPR, expr1), tokens

  return None, orig_tokens

def ParseStmt(tokens):
  stmt, tokens = TryParseStmt(tokens)
  assert stmt, '期望语句，落空了：%s' % (tokens[:5],)
  return stmt, tokens

def ParseStmtFromStr(tokens):
  return ParseStmt(list(Tokenize(tokens)))

def ParseStmts(tokens):
  """Returns (statement list, remaining tokens)."""

  stmts = []
  while True:
    stmt, tokens = TryParseStmt(tokens)
    if not stmt:
      return stmts, tokens
    stmts.append(stmt)

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
  
def TranslateTokensToPython(tokens):
  statements, tokens = ParseStmts(tokens)
  assert not tokens, ('多余符号：%s' % (tokens,))
  py_code = []
  for s in statements:
    py_code.append(TranslateStatementToPython(s))
  return '\n'.join(py_code)

def ParseToAst(code):
  tokens = list(Tokenize(code))
  statements, tokens = ParseStmts(tokens)
  assert not tokens, ('多余符号：%s' % (tokens,))
  return statements

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

def TranslateDongbeiToPython(code):
  tokens = list(Tokenize(code))
  return TranslateTokensToPython(tokens)

def Run(code, xudao=False):
  py_code = TranslateDongbeiToPython(code)
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
    sys.exit(__doc__)

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
    Run(src_file.read(), xudao=xudao)

if __name__ == '__main__':
  main()

