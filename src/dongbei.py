#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

def Run(code):
  if code:
    if re.match(u'.*是活雷锋。', code):
      return ''
    return re.sub(u'唠：“(.*?)”', r'\1', code)
  return ''
