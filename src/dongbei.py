#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import re
import sys

KW_BECOME = u'装'
KW_BEGIN = u'开整了：'
KW_CLOSE_QUOTE = u'”'
KW_COLON = u'：'
KW_END = u'整完了。'
KW_FROM = u'从'
KW_IS_VAR = u'是活雷锋'
KW_LOOP = u'磨叽：'
KW_OPEN_QUOTE = u'“'
KW_PERIOD = u'。'
KW_SAY = u'唠'
KW_TO = u'到'

KEYWORDS = (
    KW_BECOME,
    KW_BEGIN,
    KW_CLOSE_QUOTE,
    KW_COLON,
    KW_END,
    KW_FROM,
    KW_IS_VAR,
    KW_LOOP,
    KW_OPEN_QUOTE,
    KW_PERIOD,
    KW_SAY,
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

class Token:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return self.__unicode()

  def __unicode__(self):
    return u'%s <%s>' % (self.kind, self.value)

  def __repr__(self):
    return self.__unicode__().encode('utf-8')

  def __eq__(self, other):
    return (other is not None and
            self.kind == other.kind and
            self.value == other.value)

  def __ne__(self, other):
    return not (self == other)

class Statement:
  def __init__(self, kind, value):
    self.kind = kind
    self.value = value

  def __str__(self):
    return self.__unicode()

  def __unicode__(self):
    return u'%s <%s>' % (self.kind, self.value)

  def __repr__(self):
    return self.__unicode__().encode('utf-8')

  def __eq__(self, other):
    return (other is not None and
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
  last_token = Token(TK_KEYWORD, KW_CLOSE_QUOTE)
  yield last_token
  for tk in BasicTokenize(code[close_quote_pos + len(KW_CLOSE_QUOTE):], last_token):
    yield tk


def BasicTokenize(code, last_token=None):
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

  # Try to parse a keyword at the beginning of the code.
  for keyword in KEYWORDS:
    if code.startswith(keyword):
      last_token = Token(TK_KEYWORD, keyword)
      yield last_token
      for tk in BasicTokenize(code[len(keyword):].lstrip(), last_token):
        yield tk
      return

  # The code doesn't start with a keyword.
  # Try to parse a string literal.
  if last_token == Token(TK_KEYWORD, KW_OPEN_QUOTE):
    for tk in TokenizeStringLiteralAndRest(code):
      yield tk
    return

  last_token = Token(TK_CHAR, code[0])
  yield last_token
  for tk in BasicTokenize(code[1:], last_token):
    yield tk
  

def ParseInteger(str):
  m = re.match(r'^([0-9]+)(.*)', str)
  if m:
    return (int(m.group(1)), m.group(2))
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
    sys.exit(u'期望 %s，实际不是。' % (tk_type,))
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

def ParseExpression(tokens):
  integer, tokens = TryConsumeTokenType(TK_INTEGER_LITERAL, tokens)
  if integer is not None:
    return integer, tokens
  var, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
  if var is not None:
    return var, tokens
  _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_OPEN_QUOTE), tokens)
  str_token, tokens = ConsumeTokenType(TK_STRING_LITERAL, tokens)
  _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_CLOSE_QUOTE), tokens)
  return str_token, tokens
  
  
def TranslateToAst(tokens, statements):
  if not tokens:
    return

  # print('1 %s' % (tokens,))
  say, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_SAY), tokens)
  if say:
    colon, tokens = ConsumeToken(Token(TK_KEYWORD, KW_COLON), tokens)
    # print('%s' % (tokens,))
    expr, tokens = ParseExpression(tokens)
    _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
    statements.append(Statement(STMT_SAY, expr))
  else:
    # print('2 %s' % (tokens,))
    id, tokens = TryConsumeTokenType(TK_IDENTIFIER, tokens)
    if not id:
      sys.exit(u'语句必须以“唠”或者标识符开始。')
    # print('3 %s' % (tokens,))
    python_id = GetPythonVarName(id.value)
    is_var, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_IS_VAR), tokens)
    # print('4 %s' % (tokens,))
    if is_var:
      _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
      # print('5 %s' % (tokens,))
      statements.append(Statement(STMT_VAR_DECL, python_id))
    else:
      become, tokens = TryConsumeToken(Token(TK_KEYWORD, KW_BECOME), tokens)
      if become:
        expr, tokens = ParseExpression(tokens)
        _, tokens = ConsumeToken(Token(TK_KEYWORD, KW_PERIOD), tokens)
        statements.append(Statement(STMT_ASSIGN, (python_id, expr)))
      else:
        sys.exit(u'名字过后应该是“是活雷锋”或者“装”。')

  TranslateToAst(tokens, statements)  

def TranslateExpression(expr):
  if expr.kind == TK_INTEGER_LITERAL:
    return '%s' % (expr.value,)
  if expr.kind == TK_IDENTIFIER:
    return GetPythonVarName(expr.value)
  if expr.kind == TK_STRING_LITERAL:
    return 'u"%s"' % (expr.value,)
  sys.exit(u'我不懂 %s 表达式。' % (expr,))

def TranslateStatement(stmt):
  if stmt.kind == STMT_VAR_DECL:
    return '%s = None' % (stmt.value,)
  if stmt.kind == STMT_ASSIGN:
    var, expr = stmt.value
    return '%s = %s' % (var, TranslateExpression(expr))
  if stmt.kind == STMT_SAY:
    expr = stmt.value
    return '_db_output += "%%s\\n" %% (%s,)' % (TranslateExpression(expr),)
  sys.exit(u'我不懂 %s 语句。' % (stmt.kind))
  
def Translate(tokens):
  statements = []
  TranslateToAst(tokens, statements)
  py_code = ['_db_output = ""']
  for s in statements:
    py_code.append(TranslateStatement(s))
  return '\n'.join(py_code)

def Run(code):
  tokens = list(Tokenize(code))
  py_code = Translate(tokens)
  # print '%s' % (py_code,)
  exec(py_code)
  print('%s' % (_db_output,))
  return _db_output


if __name__ == '__main__':
  with io.open(sys.argv[1], 'r', encoding='utf-8') as src_file:
    Run(src_file.read())
