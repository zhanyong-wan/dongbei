#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

"""dongbei语言执行器

用法：
    dongbei.py 源程序文件名...XS
"""

import io
import re
import sys

KW_BANG = u'！'
KW_BECOME = u'装'
KW_BEGIN = u'开整：'
KW_CALL = u'整'
KW_CHECK = u'瞅瞅：'
KW_CLOSE_PAREN = u'）'
KW_CLOSE_PAREN_NARROW = ')'
KW_CLOSE_QUOTE = u'”'
KW_COLON = u'：'
KW_COMMA = u'，'
KW_COMMA_NARROW = ','
KW_COMPARE = u'比'
KW_COMPARE_WITH = u'跟'
KW_CONCAT = u'、'
KW_DEC = u'退退'
KW_DEC_BY = u'退'
KW_DIVIDE_BY = u'除以'
KW_ELSE = u'要不行咧就'
KW_END = u'整完了'
KW_END_LOOP = u'磨叽完了'
KW_EQUAL = u'一样一样的'
KW_FROM = u'从'
KW_FUNC_DEF = u'咋整：'
KW_GREATER = u'大'
KW_INC = u'走走'
KW_INC_BY = u'走'
KW_IS_VAR = u'是活雷锋'
KW_LESS = u'小'
KW_LOOP = u'磨叽：'
KW_MINUS = u'减'
KW_NOT_EQUAL = u'不是一样一样的'
KW_OPEN_PAREN = u'（'
KW_OPEN_PAREN_NARROW = '('
KW_OPEN_QUOTE = u'“'
KW_PERIOD = u'。'
KW_PLUS = u'加'
KW_RETURN = u'滚犊子吧'
KW_SAY = u'唠唠'
KW_STEP = u'步'
KW_THEN = u'吗？要行咧就'
KW_TIMES = u'乘'
KW_TO = u'到'

KEYWORDS = (
    KW_BANG,
    KW_BECOME,
    KW_BEGIN,
    KW_CHECK,
    KW_CLOSE_PAREN,
    KW_CLOSE_PAREN_NARROW,
    KW_CLOSE_QUOTE,
    KW_COLON,
    KW_COMMA,
    KW_COMMA_NARROW,
    KW_COMPARE,
    KW_COMPARE_WITH,
    KW_CONCAT,
    KW_DEC,
    KW_DEC_BY,
    KW_DIVIDE_BY,
    KW_ELSE,
    KW_END,   # must match 整完了 before matching 整
    KW_CALL,  # 整
    KW_END_LOOP,
    KW_EQUAL,
    KW_FROM,
    KW_FUNC_DEF,
    KW_GREATER,
    KW_INC,
    KW_INC_BY,
    KW_IS_VAR,
    KW_LESS,
    KW_LOOP,
    KW_MINUS,
    KW_NOT_EQUAL,
    KW_OPEN_PAREN,
    KW_OPEN_PAREN_NARROW,
    KW_OPEN_QUOTE,
    KW_PERIOD,
    KW_PLUS,
    KW_RETURN,
    KW_SAY,
    KW_STEP,
    KW_THEN,
    KW_TIMES,
    KW_TO,
    )

# Maps a keyword to its normalized form.
KEYWORD_TO_NORMALIZED_KEYWORD = {
    KW_BANG: KW_PERIOD,
    KW_OPEN_PAREN_NARROW: KW_OPEN_PAREN,
    KW_CLOSE_PAREN_NARROW: KW_CLOSE_PAREN,
    KW_COMMA_NARROW: KW_COMMA,
    }

# Types of tokens.
TK_KEYWORD = 'KEYWORD'
TK_IDENTIFIER = 'IDENTIFIER'
TK_STRING_LITERAL = 'STRING'
TK_INTEGER_LITERAL = 'INTEGER'
TK_CHAR = 'CHAR'

# Statements.
STMT_SAY = 'SAY'
STMT_VAR_DECL = 'VAR_DECL'
STMT_ASSIGN = 'ASSIGN'
STMT_INC_BY = 'INC_BY'
STMT_DEC_BY = 'DEC_BY'
STMT_LOOP = 'LOOP'
STMT_FUNC_DEF = 'FUNC_DEF'
STMT_CALL = 'CALL'
STMT_COMPOUND = 'COMPOUND'
STMT_CONDITIONAL = 'CONDITIONAL'
STMT_RETURN = 'RETURN'

class Token:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return u'%s <%s>' % (self.kind, self.value)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return (isinstance(other, Token) and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

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

  def ToPython(self):
    """Translates this expression to Python."""
    raise Exception('%s must implement ToPython().' % (type(self),))

def _dongbei_str(value):
  """Converts a value to its dongbei string."""
  if value is None:
    return '啥也不是'
  if type(value) == bool:
    return '对' if value else '错'
  return str(value)

class ConcatExpr(Expr):
  def __init__(self, exprs):
    self.exprs = exprs

  def __str__(self):
    return 'CONCAT_EXPR<%s>' % (self.exprs,)

  def Equals(self, other):
    return self.exprs == other.exprs

  def ToPython(self):
    return ' + '.join('_dongbei_str(%s)' % (
        expr.ToPython(),) for expr in self.exprs)

ARITHMETIC_OPERATION_TO_PYTHON = {
    u'加': '+',
    u'减': '-',
    u'乘': '*',
    u'除以': '/',
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

  def ToPython(self):
    if self.token.kind == TK_INTEGER_LITERAL:
      return str(self.token.value)
    if self.token.kind == TK_STRING_LITERAL:
      return 'u"%s"' % (self.token.value,)
    raise Exception('Unexpected token kind %s' % (self.token.kind,))

class VariableExpr(Expr):
  def __init__(self, var):
    self.var = var

  def __str__(self):
    return 'VARIABLE_EXPR<%s>' % (self.var,)

  def Equals(self, other):
    return self.var == other.var

  def ToPython(self):
    return GetPythonVarName(self.var.value)

class ParenExpr(Expr):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return 'PAREN_EXPR<%s>' % (self.expr,)

  def Equals(self, other):
    return self.expr == other.expr

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

  def ToPython(self):
    return '%s(%s)' % (
        GetPythonVarName(self.func.value),
        ', '.join(arg.ToPython() for arg in self.args))

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
    return u'COMPARISON_EXPR(%s, %s, %s)' % (
        self.op1, self.relation, self.op2)

  def Equals(self, other):
    return (self.op1 == other.op1 and
            self.relation == other.relation and
            self.op2 == other.op2)

  def ToPython(self):
    return '%s %s %s' % (self.op1.ToPython(),
                         COMPARISON_KEYWORD_TO_PYTHON[self.relation.value],
                         self.op2.ToPython())

class Statement:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    value_str = str(self.value)
    return u'%s <%s>' % (self.kind, value_str)

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
  m = re.match(u'^(【(.*?)】)', code)
  if m:
    id = re.sub(r'\s+', '', m.group(2))  # Ignore whitespace.
    yield Token(TK_IDENTIFIER, id)
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
    u'零': 0,
    u'一': 1,
    u'二': 2,
    u'俩': 2,
    u'两': 2,
    u'三': 3,
    u'仨': 3,
    u'四': 4,
    u'五': 5,
    u'六': 6,
    u'七': 7,
    u'八': 8,
    u'九': 9,
    u'十': 10,
    }

def ParseInteger(str):
  m = re.match(r'^([0-9]+)(.*)', str)
  if m:
    return (int(m.group(1)), m.group(2))
  for chinese_digit, value in CHINESE_DIGITS.items():
    if str.startswith(chinese_digit):
      return (value, str[len(chinese_digit):])
  return (None, str)

    
def ParseChars(chars):
  integer, rest = ParseInteger(chars)
  if integer is not None:
    yield Token(TK_INTEGER_LITERAL, integer)
  if rest:
    yield Token(TK_IDENTIFIER, rest)

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
        for tk in ParseChars(chars):
          yield tk
      yield token
      chars = ''
  for tk in ParseChars(chars):
    yield tk
    
vars = {}  # Maps Chinese identifier to generated identifier.
def GetPythonVarName(var):
  if var in vars:
    return vars[var]

  generated_var = '_db_var%d' % (len(vars),)
  vars[var] = generated_var
  return generated_var

def TryConsumeTokenType(tk_type, tokens):
  if not tokens:
    return (None, tokens)
  if tokens[0].kind == tk_type:
    return (tokens[0], tokens[1:])
  return (None, tokens)

def ConsumeTokenType(tk_type, tokens):
  tk, tokens = TryConsumeTokenType(tk_type, tokens)
  if tk is None:
    sys.exit(u'期望 %s，实际是 %s' % (tk_type, tokens[0]))
  return tk, tokens
    
def TryConsumeToken(token, tokens):
  if not tokens:
    return (None, tokens)
  if token != tokens[0]:
    return (None, tokens)
  return (token, tokens[1:])

def ConsumeToken(token, tokens):
  if not tokens:
    sys.exit(u'语句结束太早。')
  if token != tokens[0]:
    sys.exit(u'期望符号 %s，实际却是 %s。' %
             (token, tokens[0]))
  return token, tokens[1:]

# Expression grammar:
#
#   Expr ::= NonConcatExpr |
#            Expr、NonConcatExpr
#   NonConcatExpr ::= ComparisonExpr | ArithmeticExpr
#   ComparisonExpr ::= ArithmeticExpr 比 ArithmeticExpr 大 |
#                      ArithmeticExpr 比 ArithmeticExpr 小 |
#                      ArithmeticExpr 跟 ArithmeticExpr 一样一样的 |
#                      ArithmeticExpr 跟 ArithmeticExpr 不是一样一样的
#   ArithmeticExpr ::= TermExpr |
#                      ArithmeticExpr 加 TermExpr |
#                      ArithmeticExpr 减 TermExpr
#   TermExpr ::= AtomicExpr |
#                TermExpr 乘 AtomicExpr |
#                TermExpr 除以 AtomicExpr
#   AtomicExpr ::= LiteralExpr | VariableExpr | ParenExpr | CallExpr
#   ParenExpr ::= （ Expr ）
#   CallExpr ::= 整 Identifier |
#                整 Identifier（ExprList）
#   ExprList ::= Expr |
#                Expr，ExprList

def ParseCallExpr(tokens):
  """Returns (call_expr, remaining tokens)."""
  call, tokens = TryConsumeToken(Keyword(KW_CALL), tokens)
  if not call:
    return None, tokens

  func, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
  open_paren, tokens = TryConsumeToken(Keyword(KW_OPEN_PAREN), tokens)
  args = []
  if open_paren:
    while True:
      expr, tokens = ParseExpr(tokens)
      args.append(expr)
      close_paren, tokens = TryConsumeToken(
          Keyword(KW_CLOSE_PAREN), tokens)
      if close_paren:
        break
      _, tokens = ConsumeToken(Keyword(KW_COMMA), tokens)
  return CallExpr(func, args), tokens
 
def ParseAtomicExpr(tokens):
  """Returns (expr, remaining tokens)."""

  # Do we see an integer literal?
  num, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if num:
    return LiteralExpr(num), tokens

  # Do we see a string literal?
  open_quote, tokens = TryConsumeToken(Keyword(KW_OPEN_QUOTE), tokens)
  if open_quote:
    str, tokens = ConsumeTokenType(TK_STRING_LITERAL, tokens)
    _, tokens = ConsumeToken(Keyword(KW_CLOSE_QUOTE), tokens)
    return LiteralExpr(str), tokens

  # Do we see an identifier?
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if id:
    return VariableExpr(id), tokens

  # Do we see a parenthesis?
  open_paren, tokens = TryConsumeToken(Keyword(KW_OPEN_PAREN), tokens)
  if open_paren:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_CLOSE_PAREN), tokens)
    return ParenExpr(expr), tokens

  # Do we see a function call?
  call_expr, tokens = ParseCallExpr(tokens)
  if call_expr:
    return call_expr, tokens
      
  return None, tokens

def ParseTermExpr(tokens):
  factor, tokens = ParseAtomicExpr(tokens)
  if not factor:
    return None, tokens

  factors = [factor]  # All factors of the term.
  operators = []  # Operators between the factors. The len of this is len(factors) - 1.

  while True:
    pre_operator_tokens = tokens
    operator, tokens = TryConsumeToken(Keyword(KW_TIMES), tokens)
    if not operator:
      operator, tokens = TryConsumeToken(Keyword(KW_DIVIDE_BY), tokens)
    if not operator:
      break

    factor, tokens = ParseAtomicExpr(tokens)
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

def ParseArithmeticExpr(tokens):
  term, tokens = ParseTermExpr(tokens)
  if not term:
    return None, tokens

  terms = [term]  # All terms of the expression.
  operators = []  # Operators between the terms. The len of this is len(terms) - 1.

  while True:
    pre_operator_tokens = tokens
    operator, tokens = TryConsumeToken(Keyword(KW_PLUS), tokens)
    if not operator:
      operator, tokens = TryConsumeToken(Keyword(KW_MINUS), tokens)
    if not operator:
      break

    term, tokens = ParseTermExpr(tokens)
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

def ParseNonConcatExpr(tokens):
  arith, tokens = ParseArithmeticExpr(tokens)
  if not arith:
    return None, tokens

  cmp, tokens = TryConsumeToken(Keyword(KW_COMPARE), tokens)
  if cmp:
    arith2, tokens = ParseArithmeticExpr(tokens)
    relation, tokens = TryConsumeToken(Keyword(KW_GREATER), tokens)
    if not relation:
      relation, tokens = ConsumeToken(Keyword(KW_LESS), tokens)
    return ComparisonExpr(arith, relation, arith2), tokens

  cmp, tokens = TryConsumeToken(Keyword(KW_COMPARE_WITH), tokens)
  if cmp:
    arith2, tokens = ParseArithmeticExpr(tokens)
    relation, tokens = TryConsumeToken(Keyword(KW_EQUAL), tokens)
    if not relation:
      relation, tokens = ConsumeToken(Keyword(KW_NOT_EQUAL), tokens)
    return ComparisonExpr(arith, relation, arith2), tokens

  return arith, tokens

def ParseExpr(tokens):
  nc_expr, tokens = ParseNonConcatExpr(tokens)
  if not nc_expr:
    return None, tokens

  nc_exprs = [nc_expr]
  while True:
    pre_operator_tokens = tokens
    concat, tokens = TryConsumeToken(Keyword(KW_CONCAT), tokens)
    if not concat:
      break

    nc_expr, tokens = ParseNonConcatExpr(tokens)
    if nc_expr:
      nc_exprs.append(nc_expr)
    else:
      # We have a trailing concat operator without an expression to follow it.
      tokens = pre_operator_tokens
      break

  if len(nc_exprs) == 1:
    return nc_exprs[0], tokens

  return ConcatExpr(nc_exprs), tokens
  
def ParseExprFromStr(str):
  return ParseExpr(list(Tokenize(str)))

def ParseStmt(tokens):
  """Returns (statement, remainding_tokens)."""

  orig_tokens = tokens

  # Parse 开整：
  begin, tokens = TryConsumeToken(Keyword(KW_BEGIN), tokens)
  if begin:
    stmts, tokens = ParseStmts(tokens)
    if not stmts:
      stmts = []
    _, tokens = ConsumeToken(Keyword(KW_END), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return Statement(STMT_COMPOUND, stmts), tokens

  # Parse 唠唠：
  say, tokens = TryConsumeToken(Keyword(KW_SAY), tokens)
  if say:
    colon, tokens = ConsumeToken(Keyword(KW_COLON), tokens)
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_SAY, expr), tokens)

  # Parse 整
  call_expr, tokens = ParseCallExpr(tokens)
  if call_expr:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return Statement(STMT_CALL, call_expr), tokens

  # Parse 滚犊子吧
  ret, tokens = TryConsumeToken(Keyword(KW_RETURN), tokens)
  if ret:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_RETURN, expr), tokens)

  # Parse 瞅瞅
  check, tokens = TryConsumeToken(Keyword(KW_CHECK), tokens)
  if check:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_THEN), tokens)
    then_stmt, tokens = ParseStmt(tokens)
    # Parse the optional else-branch.
    kw_else, tokens = TryConsumeToken(Keyword(KW_ELSE), tokens)
    if kw_else:
      else_stmt, tokens = ParseStmt(tokens)
    else:
      else_stmt = None
    return Statement(STMT_CONDITIONAL, (expr, then_stmt, else_stmt)), tokens

  # Parse an identifier name.
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if not id:
    return (None, orig_tokens)

  # Code below is for statements that start with an identifier.

  # Parse 是活雷锋
  is_var, tokens = TryConsumeToken(Keyword(KW_IS_VAR), tokens)
  if is_var:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_VAR_DECL, id), tokens)

  # Parse 装
  become, tokens = TryConsumeToken(Keyword(KW_BECOME), tokens)
  if become:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_ASSIGN, (id, expr)), tokens)

  # Parse 走走
  inc, tokens = TryConsumeToken(Keyword(KW_INC), tokens)
  if inc:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY,
                      (id, LiteralExpr(Token(TK_INTEGER_LITERAL, 1)))),
            tokens)

  # Parse 走X步
  inc, tokens = TryConsumeToken(
      Keyword(KW_INC_BY), tokens)
  if inc:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_STEP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY, (id, expr)), tokens)

  # Parse 退退
  dec, tokens = TryConsumeToken(Keyword(KW_DEC), tokens)
  if dec:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY,
                      (id, LiteralExpr(Token(TK_INTEGER_LITERAL, 1)))),
            tokens)

  # Parse 退X步
  dec, tokens = TryConsumeToken(
      Keyword(KW_DEC_BY), tokens)
  if dec:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_STEP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY, (id, expr)), tokens)

  # Parse 磨叽
  from_, tokens = TryConsumeToken(Keyword(KW_FROM), tokens)
  if from_:
    from_expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_TO), tokens)
    to_expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_LOOP), tokens)
    stmts, tokens = ParseStmts(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END_LOOP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_LOOP, (id, from_expr, to_expr, stmts)), tokens)

  # Parse 咋整
  open_paren, tokens = TryConsumeToken(
      Keyword(KW_OPEN_PAREN), tokens)
  if open_paren:
    params = []
    while True:
      param, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
      params.append(param)
      close_paren, tokens = TryConsumeToken(Keyword(KW_CLOSE_PAREN), tokens)
      if close_paren:
        break
      _, tokens = ConsumeToken(Keyword(KW_COMMA), tokens)
        
    func_def, tokens = ConsumeToken(
        Keyword(KW_FUNC_DEF), tokens)
    stmts, tokens = ParseStmts(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, params, stmts)), tokens)

  func_def, tokens = TryConsumeToken(
      Keyword(KW_FUNC_DEF), tokens)
  if func_def:
    stmts, tokens = ParseStmts(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, [], stmts)), tokens)

  return (None, orig_tokens)

def ParseStmtFromStr(tokens):
  return ParseStmt(list(Tokenize(tokens)))

def ParseStmts(tokens):
  """Returns (statement list, remaining tokens)."""

  stmts = []
  while True:
    stmt, tokens = ParseStmt(tokens)
    if not stmt:
      return stmts, tokens
    stmts.append(stmt)

def TranslateStatementToPython(stmt, indent = ''):
  """Translates the statements to Python code, without trailing newline."""
  
  if stmt.kind == STMT_VAR_DECL:
    var_token = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = None' % (var,)

  if stmt.kind == STMT_ASSIGN:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = %s' % (var, expr.ToPython())

  if stmt.kind == STMT_SAY:
    expr = stmt.value
    return indent + '_db_append_output("%%s\\n" %% (_dongbei_str(%s),))' % (
        expr.ToPython(),)

  if stmt.kind == STMT_INC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s += %s' % (var, expr.ToPython())

  if stmt.kind == STMT_DEC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s -= %s' % (var, expr.ToPython())

  if stmt.kind == STMT_LOOP:
    var_token, from_val, to_val, stmts = stmt.value
    var = GetPythonVarName(var_token.value)
    loop = indent + 'for %s in range(%s, %s + 1):' % (
        var, from_val.ToPython(),
        to_val.ToPython())
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
    func_token = stmt.value.func
    args = stmt.value.args
    func_name = GetPythonVarName(func_token.value)
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
    
  sys.exit(u'我不懂 %s 语句咋执行。' % (stmt.kind))
  
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

_db_output = ''
def _db_append_output(s):
  global _db_output
  _db_output += s

def Run(code):
  tokens = list(Tokenize(code))
  py_code = TranslateTokensToPython(tokens)
  print('Python 代码：')
  print('%s' % (py_code,))
  global _db_output
  _db_output = ''
  # See https://stackoverflow.com/questions/871887/using-exec-with-recursive-functions
  # Use the same dictionary for local and global definitions.
  # Needed for defining recursive dongbei functions.
  exec(py_code, globals(), globals())
  print('运行结果：')
  print('%s' % (_db_output,))
  return _db_output


if __name__ == '__main__':
  if len(sys.argv) == 1:
    sys.exit(__doc__)

  for filepath in sys.argv[1:]:
    with io.open(filepath, 'r', encoding='utf-8') as src_file:
      print('执行 %s ...' % (filepath,))
      Run(src_file.read())
