#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import re
import sys

KW_INC = u'走走'
KW_INC_BY = u'走'
KW_BECOME = u'装'
KW_BEGIN = u'开整了：'
KW_CALL = u'整'
KW_CLOSE_PAREN = u'）'
KW_CLOSE_QUOTE = u'”'
KW_COLON = u'：'
KW_CONCAT = u'还有'
KW_DEC = u'退退'
KW_DEC_BY = u'退'
KW_DIVIDE_BY = u'除以'
KW_END = u'整完了'
KW_END_LOOP = u'磨叽完了'
KW_FROM = u'从'
KW_FUNC_DEF = u'咋整：'
KW_IS_VAR = u'是活雷锋'
KW_LOOP = u'磨叽：'
KW_MINUS = u'减'
KW_OPEN_PAREN = u'（'
KW_OPEN_QUOTE = u'“'
KW_PERIOD = u'。'
KW_PLUS = u'加'
KW_SAY = u'唠唠'
KW_STEP = u'步'
KW_TIMES = u'乘'
KW_TO = u'到'

KEYWORDS = (
    KW_BECOME,
    KW_BEGIN,
    KW_CLOSE_PAREN,
    KW_CLOSE_QUOTE,
    KW_COLON,
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
    KW_OPEN_QUOTE,
    KW_PERIOD,
    KW_PLUS,
    KW_SAY,
    KW_STEP,
    KW_TIMES,
    KW_TO,
    )

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

class Token:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return self.__unicode__()

  def __unicode__(self):
    # return u'%s <%s>' % (self.kind, repr(self.value))
    return u'%s <%s>' % (self.kind, self.value)

  def __repr__(self):
    return self.__unicode__().encode('utf-8')

  def __eq__(self, other):
    return (isinstance(other, Token) and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

class Expression:
  def __init__(self, tokens):
    self.tokens = tokens

  def __str__(self):
    return self.__unicode__()

  def __unicode__(self):
    # return u'EXPRESSION %s' % (repr(self.tokens),)
    return u'EXPRESSION %s' % (self.tokens,)

  def __repr__(self):
    return self.__unicode__().encode('utf-8')

  def __eq__(self, other):
    return (isinstance(other, Expression) and
            self.tokens == other.tokens)

  def __ne__(self, other):
    return not (self == other)

class Statement:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return self.__unicode__()

  def __unicode__(self):
    # return u'%s <%s>' % (self.kind, repr(self.value))
    
    value_unicode = str(self.value).decode('utf-8')  # unicode(self.value)
    return u'%s <%s>' % (self.kind, value_unicode)

  def __repr__(self):
    return self.__unicode__().encode('utf-8')

  def __eq__(self, other):
    return (isinstance(other, Statement) and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

def TokenizeStringLiteralAndRest(code):
  close_quote_pos = code.find(KW_CLOSE_QUOTE)
  if close_quote_pos < 0:
    yield Token(TK_STRING_LITERAL, code)
    return

  yield Token(TK_STRING_LITERAL, code[:close_quote_pos])
  yield Token(TK_KEYWORD, KW_CLOSE_QUOTE)
  for tk in BasicTokenize(code[close_quote_pos + len(KW_CLOSE_QUOTE):]):
    yield tk


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
    id = m.group(2).strip()
    yield Token(TK_IDENTIFIER, id)
    for tk in BasicTokenize(code[len(m.group(1)):]):
      yield tk
    return
    
  # Try to parse a keyword at the beginning of the code.
  for keyword in KEYWORDS:
    if code.startswith(keyword):
      last_token = Token(TK_KEYWORD, keyword)
      yield last_token
      remaining_code = code[len(keyword):]
      if last_token == Token(TK_KEYWORD, KW_OPEN_QUOTE):
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

def ParseExpressionToken(tokens):
  """Returns (token, remaining tokens)."""

  orig_tokens = tokens
  
  integer, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if integer is not None:
    return integer, tokens

  var, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if var is not None:
    return var, tokens

  open_quote, tokens = TryConsumeToken(
      Token(TK_KEYWORD, KW_OPEN_QUOTE), tokens)
  if open_quote:
    str_token, tokens = TryConsumeTokenType(TK_STRING_LITERAL, tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_CLOSE_QUOTE), tokens)
    return str_token, tokens

  token = tokens[0]
  if token in (Token(TK_KEYWORD, KW_PLUS),
               Token(TK_KEYWORD, KW_MINUS),
               Token(TK_KEYWORD, KW_TIMES),
               Token(TK_KEYWORD, KW_DIVIDE_BY),
               Token(TK_KEYWORD, KW_CONCAT)):
    return token, tokens[1:]

  return None, orig_tokens

def ParseExpression(tokens):
  """Return (expr, remaining tokens)."""

  expr_tokens = []
  while True:
    token, tokens = ParseExpressionToken(tokens)
    if token:
      expr_tokens.append(token)
    else:
      break
  return Expression(expr_tokens), tokens

def TranslateToOneStatement(tokens):
  """Returns (statement, remainding_tokens, error)."""

  orig_tokens = tokens
  say, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_SAY), tokens)
  if say:
    colon, tokens = ConsumeToken(Token(TK_KEYWORD, KW_COLON), tokens)
    expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_SAY, expr), tokens)

  call, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_CALL), tokens)
  if call:
    func, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    open_paren, tokens = TryConsumeToken(
        Token(TK_KEYWORD, KW_OPEN_PAREN), tokens)
    if open_paren:
      arg, tokens = ParseExpression(tokens)
      _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_CLOSE_PAREN), tokens)
      args = [arg]
    else:
      args = []
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_CALL, (func, args)), tokens)

  id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if not id:
    # sys.exit(u'语句必须以“唠唠”或者标识符开始。实际是%s' % (tokens[0],))
    return (None, orig_tokens)

  is_var, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_IS_VAR), tokens)
  if is_var:
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_VAR_DECL, id), tokens)

  become, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_BECOME), tokens)
  if become:
    expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_ASSIGN, (id, expr)), tokens)

  inc, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_INC), tokens)
  if inc:
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY,
                      (id, Expression([Token(TK_INTEGER_LITERAL, 1)]))),
            tokens)

  inc, tokens = TryConsumeToken(
      Token(TK_KEYWORD, KW_INC_BY), tokens)
  if inc:
    expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_STEP), tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_INC_BY, (id, expr)), tokens)

  dec, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_DEC), tokens)
  if dec:
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY,
                      (id, Expression([Token(TK_INTEGER_LITERAL, 1)]))),
            tokens)

  dec, tokens = TryConsumeToken(
      Token(TK_KEYWORD, KW_DEC_BY), tokens)
  if dec:
    expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_STEP), tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_DEC_BY, (id, expr)), tokens)

  from_, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_FROM), tokens)
  if from_:
    from_expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_TO), tokens)
    to_expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_LOOP), tokens)
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_END_LOOP), tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_LOOP, (id, from_expr, to_expr, stmts)), tokens)

  open_paren, tokens = TryConsumeToken(
      Token(TK_KEYWORD, KW_OPEN_PAREN), tokens)
  if open_paren:
    param, tokens = ConsumeTokenType(TK_IDENTIFIER, tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_CLOSE_PAREN), tokens)
    func_def, tokens = ConsumeToken(
        Token(TK_KEYWORD, KW_FUNC_DEF), tokens)
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_END), tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, [param], stmts)), tokens)

  func_def, tokens = TryConsumeToken(
      Token(TK_KEYWORD, KW_FUNC_DEF), tokens)
  if func_def:
    stmts, tokens = TranslateToStatements(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_END), tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    return (Statement(STMT_FUNC_DEF, (id, [], stmts)), tokens)

  # sys.exit(u'名字过后应该是“是活雷锋”、“装”、“走走”、“走”、' +
  #          u'“退退”、“退”，或者“从”。实际是%s'
  #          % (tokens[0],))
  return (None, orig_tokens)

def TranslateToStatements(tokens):
  """Returns (statement list, remaining tokens)."""

  stmts = []
  while True:
    stmt, tokens = TranslateToOneStatement(tokens)
    if not stmt:
      return stmts, tokens
    stmts.append(stmt)

def TranslateExpressionTokensToPython(tokens):
  """Returns the Python code for the given dongbei expression."""

  python_code = ''
  for token in tokens:
    if token.kind == TK_INTEGER_LITERAL:
      python_code += '%s' % (token.value,)
    elif token.kind == TK_IDENTIFIER:
      python_code += GetPythonVarName(token.value)
    elif token.kind == TK_STRING_LITERAL:
      python_code += 'u"%s"' % (token.value,)
    elif token == Token(TK_KEYWORD, KW_PLUS):
      python_code += '+'
    elif token == Token(TK_KEYWORD, KW_MINUS):
      python_code += '-'
    elif token == Token(TK_KEYWORD, KW_TIMES):
      python_code += '*'
    elif token == Token(TK_KEYWORD, KW_DIVIDE_BY):
      python_code += '/'
    elif token == Token(TK_KEYWORD, KW_CONCAT):
      python_code += ') + unicode('
    else:
      sys.exit(u'我不懂 %s 表达式。' % (token,))
  return python_code

def TranslateExpressionToPython(expr):
  python_code = TranslateExpressionTokensToPython(expr.tokens)
  if Token(TK_KEYWORD, KW_CONCAT) not in expr.tokens:
    return python_code
  return 'unicode(%s)' % (python_code,)

def TranslateStatementToPython(stmt, indent = ''):
  if stmt.kind == STMT_VAR_DECL:
    var_token = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = None' % (var,)
  if stmt.kind == STMT_ASSIGN:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s = %s' % (var, TranslateExpressionToPython(expr))
  if stmt.kind == STMT_SAY:
    expr = stmt.value
    return indent + '_db_append_output("%%s\\n" %% (%s,))' % (
        TranslateExpressionToPython(expr),)
  if stmt.kind == STMT_INC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s += %s' % (var, TranslateExpressionToPython(expr))
  if stmt.kind == STMT_DEC_BY:
    var_token, expr = stmt.value
    var = GetPythonVarName(var_token.value)
    return indent + '%s -= %s' % (var, TranslateExpressionToPython(expr))
  if stmt.kind == STMT_LOOP:
    var_token, from_val, to_val, stmts = stmt.value
    var = GetPythonVarName(var_token.value)
    loop = indent + 'for %s in range(%s, %s + 1):' % (
        var, TranslateExpressionToPython(from_val),
        TranslateExpressionToPython(to_val))
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
    args_code = map(TranslateExpressionToPython, args)
    code = indent + '%s(%s)' % (func_name, ', '.join(args_code))
    return code
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
  print '%s' % (py_code,)
  global _db_output
  _db_output = ''
  exec(py_code)
  print('%s' % (_db_output,))
  return _db_output


if __name__ == '__main__':
  with io.open(sys.argv[1], 'r', encoding='utf-8') as src_file:
    Run(src_file.read())
