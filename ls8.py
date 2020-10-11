#!/usr/bin/env python3

"""Main."""

import sys, os
from cpu import *

with open(os.path.join(sys.path[0], 'sctest.ls8'), 'r') as f:
  lines = f.readlines()
  load = []
  for item in lines:
    if item[0] == '1' or item[0] == '0':
      load.append("0b" + item[0:8])

cpu = CPU()

cpu.load(load)
print()
cpu.run()
print()