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
KW_BEGIN = u'开整了：'
KW_CALL = u'整'
KW_CLOSE_PAREN = u'）'
KW_CLOSE_PAREN_NARROW = ')'
KW_CLOSE_QUOTE = u'”'
KW_COLON = u'：'
KW_COMPARE = u'比'
KW_CONCAT = u'、'
KW_DEC = u'退退'
KW_DEC_BY = u'退'
KW_DIVIDE_BY = u'除以'
KW_END = u'整完了'
KW_END_LOOP = u'磨叽完了'
KW_FROM = u'从'
KW_FUNC_DEF = u'咋整：'
KW_INC = u'走走'
KW_INC_BY = u'走'
KW_IS_VAR = u'是活雷锋'
KW_LOOP = u'磨叽：'
KW_MINUS = u'减'
KW_OPEN_PAREN = u'（'
KW_OPEN_PAREN_NARROW = '('
KW_OPEN_QUOTE = u'“'
KW_PERIOD = u'。'
KW_PLUS = u'加'
KW_RETURN = u'滚犊子吧'
KW_SAY = u'唠唠'
KW_STEP = u'步'
KW_TIMES = u'乘'
KW_TO = u'到'

KEYWORDS = (
    KW_BANG,
    KW_BECOME,
    KW_BEGIN,
    KW_CLOSE_PAREN,
    KW_CLOSE_PAREN_NARROW,
    KW_CLOSE_QUOTE,
    KW_COLON,
    KW_COMPARE,
    KW_CONCAT,
    KW_DEC,
    KW_DEC_BY,
    KW_DIVIDE_BY,
    KW_END,   # must match 整完了 before matching 整
    KW_CALL,  # 整
    KW_END_LOOP,
    KW_FROM,
    KW_FUNC_DEF,
    KW_INC,
    KW_INC_BY,
    KW_IS_VAR,
    KW_LOOP,
    KW_MINUS,
    KW_OPEN_PAREN,
    KW_OPEN_PAREN_NARROW,
    KW_OPEN_QUOTE,
    KW_PERIOD,
    KW_PLUS,
    KW_RETURN,
    KW_SAY,
    KW_STEP,
    KW_TIMES,
    KW_TO,
    )

# Maps a keyword to its normalized form.
KEYWORD_TO_NORMALIZED_KEYWORD = {
    KW_BANG: KW_PERIOD,
    KW_OPEN_PAREN_NARROW: KW_OPEN_PAREN,
    KW_CLOSE_PAREN_NARROW: KW_CLOSE_PAREN,
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
  def __init__(self, tokens):
    self.tokens = tokens

  def __str__(self):
    tokens_str = ', '.join(str(token) for token in self.tokens)
    return u'EXPR [%s]' % (tokens_str,)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return (type(other) == Expr and
            self.tokens == other.tokens)

  def __ne__(self, other):
    return not (self == other)

class NewExpr:
  def __init__(self):
    pass

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    return type(self) == type(other) and self.Equals(other)

  def Equals(self, other):
    """Returns true if self and other (which is guaranteed to have the same type) are equal."""
    raise Exception('A subclass of NewExpr must implement Equals().')

  def __ne__(self, other):
    return not (self == other)

class ArithmeticExpr(NewExpr):
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

class AtomicExpr(NewExpr):
  def __init__(self, token):
    self.token = token

  def __str__(self):
    return 'ATOMIC_EXPR<%s>' % (self.token,)

  def Equals(self, other):
    return self.token == other.token

class ParenExpr(NewExpr):
  def __init__(self, expr):
    self.expr = expr

  def __str__(self):
    return 'PAREN_EXPR<%s>' % (self.expr,)

  def Equals(self, other):
    return self.expr == other.expr

class ComparisonExpr(NewExpr):
  def __init__(self, op1, relation, op2):
    self.op1 = op1
    self.relation = relation
    self.op2 = op2

  def __str__(self):
    return u'COMPARISON_EXPR(%s, %s, %s)' % (
        self.op1, self.relation, self.op2)

  def Equals(other):
    return (self.op1 == other.op1 and
            self.relation == other.relation and
            self.op2 == other.op2)

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


def TryParseKeyword(keyword, code):
  """Returns (parsed keyword string, remaining code)."""
  orig_code = code
  for char in keyword:
    code = code.lstrip()
    if not code.startswith(char):
      return None, orig_code
    code = code[1:]
  return keyword, code

def BasicTokenize(code):
  # Skip spaces at the beginning.
  while True:
    old_len = len(code)
    code = code.lstrip()
    if code.startswith('#'):  # comment
      code = re.sub(r'^.*', '', code)  # Ignore the comment line.
    if len(code) == old_len:
      break
    
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
    u'两': 2,
    u'三': 3,
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

def ParseExprToken(tokens, allow_close_paren):
  # TODO: make this return a token list instead of one token.
  """Returns (token, remaining tokens)."""

  orig_tokens = tokens

  # Do we see an integer literal?
  integer, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if integer is not None:
    return integer, tokens

  # Do we see a variable?
  var, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if var is not None:
    return var, tokens

  # Do we see a string literal?
  open_quote, tokens = TryConsumeToken(
      Keyword(KW_OPEN_QUOTE), tokens)
  if open_quote:
    str_token, tokens = TryConsumeTokenType(TK_STRING_LITERAL, tokens)
    _, tokens = ConsumeToken(Keyword(KW_CLOSE_QUOTE), tokens)
    return str_token, tokens

  # Do we see a function call?
  call, tokens = TryConsumeToken(Keyword(KW_CALL), tokens)
  if call:
    return call, tokens
    
  # Do we see an operator or a parenthesis?
  token = tokens[0]
  if token in (Keyword(KW_PLUS),
               Keyword(KW_MINUS),
               Keyword(KW_TIMES),
               Keyword(KW_DIVIDE_BY),
               Keyword(KW_CONCAT),
               Keyword(KW_OPEN_PAREN),
  ):
    return token, tokens[1:]
  if allow_close_paren and token == Keyword(KW_CLOSE_PAREN):
    return token, tokens[1:]

  return None, orig_tokens

# Expression grammer:
#
#   Expr ::= ComparisonExpr | ArithmeticExpr
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
#   AtomicExpr ::= LiteralExpr | ParenExpr | CallExpr
#   ParenExpr ::= （ Expr ）
#   CallExpr ::= 整 Identifier |
#                整 Identifier（ExprList）
#   ExprList ::= Expr |
#                Expr，ExprList

def NewParseExpr(tokens):
  """Returns (expr, remaining tokens)."""

  # Do we see an integer literal?
  num, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if num:
    return AtomicExpr(num), tokens

  # Do we see an identifier?
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if id:
    return AtomicExpr(id), tokens

  # Do we see a parenthesis?
  open_paren, tokens = TryConsumeToken(Keyword(KW_OPEN_PAREN), tokens)
  if open_paren:
    expr, tokens = NewParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_CLOSE_PAREN), tokens)
    return ParenExpr(expr), tokens

  return None, tokens

def ParseExprFromStr(str):
  return NewParseExpr(list(Tokenize(str)))

def ParseExpr(tokens):
  """Returns (expr, remaining tokens)."""

  expr_tokens = []
  paren_level = 0  # How many level are we in parentheses?
  while True:
    token, tokens = ParseExprToken(
        tokens, allow_close_paren = paren_level > 0)
    if token:
      expr_tokens.append(token)
      if token == Keyword(KW_OPEN_PAREN):
        paren_level += 1
      elif token == Keyword(KW_CLOSE_PAREN):
        paren_level -= 1
    else:
      break
  return Expr(expr_tokens), tokens

def TranslateToOneStatement(tokens):
  """Returns (statement, remainding_tokens, error)."""

  orig_tokens = tokens
  say, tokens = TryConsumeToken(Keyword(KW_SAY), tokens)
  if say:
    colon, tokens = ConsumeToken(Keyword(KW_COLON), tokens)
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_SAY, expr), tokens)

  call, tokens = TryConsumeToken(Keyword(KW_CALL), tokens)
  if call:
    func, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    open_paren, tokens = TryConsumeToken(
        Keyword(KW_OPEN_PAREN), tokens)
    if open_paren:
      arg, tokens = ParseExpr(tokens)
      _, tokens = ConsumeToken(Keyword(KW_CLOSE_PAREN), tokens)
      args = [arg]
    else:
      args = []
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_CALL, (func, args)), tokens)

  ret, tokens = TryConsumeToken(Keyword(KW_RETURN), tokens)
  if ret:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_RETURN, expr), tokens)
    
  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if not id:
    # sys.exit(u'语句必须以“唠唠”或者标识符开始。实际是%s' % (tokens[0],))
    return (None, orig_tokens)

  is_var, tokens = TryConsumeToken(Keyword(KW_IS_VAR), tokens)
  if is_var:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_VAR_DECL, id), tokens)

  become, tokens = TryConsumeToken(Keyword(KW_BECOME), tokens)
  if become:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_ASSIGN, (id, expr)), tokens)

  inc, tokens = TryConsumeToken(Keyword(KW_INC), tokens)
  if inc:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY,
                      (id, Expr([Token(TK_INTEGER_LITERAL, 1)]))),
            tokens)

  inc, tokens = TryConsumeToken(
      Keyword(KW_INC_BY), tokens)
  if inc:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_STEP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY, (id, expr)), tokens)

  dec, tokens = TryConsumeToken(Keyword(KW_DEC), tokens)
  if dec:
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY,
                      (id, Expr([Token(TK_INTEGER_LITERAL, 1)]))),
            tokens)

  dec, tokens = TryConsumeToken(
      Keyword(KW_DEC_BY), tokens)
  if dec:
    expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_STEP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY, (id, expr)), tokens)

  from_, tokens = TryConsumeToken(Keyword(KW_FROM), tokens)
  if from_:
    from_expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_TO), tokens)
    to_expr, tokens = ParseExpr(tokens)
    _, tokens = ConsumeToken(Keyword(KW_LOOP), tokens)
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END_LOOP), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_LOOP, (id, from_expr, to_expr, stmts)), tokens)

  open_paren, tokens = TryConsumeToken(
      Keyword(KW_OPEN_PAREN), tokens)
  if open_paren:
    param, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    _, tokens = ConsumeToken(Keyword(KW_CLOSE_PAREN), tokens)
    func_def, tokens = ConsumeToken(
        Keyword(KW_FUNC_DEF), tokens)
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, [param], stmts)), tokens)

  func_def, tokens = TryConsumeToken(
      Keyword(KW_FUNC_DEF), tokens)
  if func_def:
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Keyword(KW_END), tokens)
    _, tokens = ConsumeToken(Keyword(KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, [], stmts)), tokens)

  return (None, orig_tokens)

def TranslateToStatements(tokens):
  """Returns (statement list, remaining tokens)."""

  stmts = []
  while True:
    stmt, tokens = TranslateToOneStatement(tokens)
    if not stmt:
      return stmts, tokens
    stmts.append(stmt)

def TranslateExprTokensToPython(tokens):
  """Returns the Python code for the given dongbei expression."""

  python_code = ''
  while len(tokens) > 0:
    token = tokens[0]
    tokens = tokens[1:]

    if token.kind == TK_INTEGER_LITERAL:
      python_code += '%s' % (token.value,)
    elif token.kind == TK_IDENTIFIER:
      python_code += GetPythonVarName(token.value)
    elif token.kind == TK_STRING_LITERAL:
      python_code += 'u"%s"' % (token.value,)
    elif token == Keyword(KW_PLUS):
      python_code += '+'
    elif token == Keyword(KW_MINUS):
      python_code += '-'
    elif token == Keyword(KW_TIMES):
      python_code += '*'
    elif token == Keyword(KW_DIVIDE_BY):
      python_code += '/'
    elif token == Keyword(KW_CONCAT):
      python_code += ') + str('
    elif token == Keyword(KW_CALL):
      if len(tokens) == 0:
        sys.exit(u'“整”后面必须跟函数名。')
      func = tokens[0]
      python_code += GetPythonVarName(func.value)
      tokens = tokens[1:]
      if len(tokens) == 0 or tokens[0] != Keyword(KW_OPEN_PAREN):
        python_code += '()'
    elif token == Keyword(KW_OPEN_PAREN):
      python_code += '('
    elif token == Keyword(KW_CLOSE_PAREN):
      python_code += ')'
    else:
      sys.exit(u'我不懂 %s 表达式。' % (token,))

  return python_code

def TranslateExprToPython(expr):
  python_code = TranslateExprTokensToPython(expr.tokens)
  if Keyword(KW_CONCAT) not in expr.tokens:
    return python_code
  return 'str(%s)' % (python_code,)

def TranslateStatementToPython(stmt, indent = ''):
  if stmt.kind == STMT_VAR_DECL:
    var_token = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = None' % (var,)
  if stmt.kind == STMT_ASSIGN:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = %s' % (var, TranslateExprToPython(expr))
  if stmt.kind == STMT_SAY:
    expr = stmt.value
    return indent + '_db_append_output("%%s\\n" %% (%s,))' % (
        TranslateExprToPython(expr),)
  if stmt.kind == STMT_INC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s += %s' % (var, TranslateExprToPython(expr))
  if stmt.kind == STMT_DEC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s -= %s' % (var, TranslateExprToPython(expr))
  if stmt.kind == STMT_LOOP:
    var_token, from_val, to_val, stmts = stmt.value
    var = GetPythonVarName(var_token.value)
    loop = indent + 'for %s in range(%s, %s + 1):' % (
        var, TranslateExprToPython(from_val),
        TranslateExprToPython(to_val))
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
    func_token, args = stmt.value
    func_name = GetPythonVarName(func_token.value)
    args_code = map(TranslateExprToPython, args)
    code = indent + '%s(%s)' % (func_name, ', '.join(args_code))
    return code
  if stmt.kind == STMT_RETURN:
    expr = stmt.value
    expr_code = TranslateExprToPython(expr)
    return indent + 'return ' + expr_code
  sys.exit(u'我不懂 %s 语句。' % (stmt.kind))
  
def Translate(tokens):
  statements, tokens = TranslateToStatements(tokens)
  assert not tokens, ('多余符号：%s' % (tokens,))
  py_code = []
  for s in statements:
    py_code.append(TranslateStatementToPython(s))
  return '\n'.join(py_code)

def ParseToAst(code):
  tokens = list(Tokenize(code))
  statements, tokens = TranslateToStatements(tokens)
  assert not tokens, ('多余符号：%s' % (tokens,))
  return statements

_db_output = ''
def _db_append_output(s):
  global _db_output
  _db_output += s

def Run(code):
  tokens = list(Tokenize(code))
  py_code = Translate(tokens)
  print('Python 代码：')
  print('%s' % (py_code,))
  global _db_output
  _db_output = ''
  exec(py_code)
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
