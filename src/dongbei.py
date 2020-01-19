#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def Run(code):
  lines = code.split()
  output = ''
  value = None
  for line in lines:
    if re.match(u'.*是活雷锋。$', line):
      value = None
      continue

    m = re.match(u'.*装(.*)。$', line)
    if m:
      value = m.group(1)
      continue

    m = re.match(u'唠：“(.*?)”', line)
    if m:
      output += m.group(1) + '\n'
      continue

  if value is not None:
    output += str(value)
  return output
