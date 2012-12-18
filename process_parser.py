import sys
import re
import os
from collections import defaultdict
from random import randrange

import Image


if __name__ == '__main__':
  filename, = sys.argv[1:]
  print 'Parsing...',
  sys.stdout.flush()
  with open(filename) as fin:
    fin = iter(fin)
    while True:
      line = next(fin)
      if line == "Here are the programs:\n":
        break

    receives_from = defaultdict(list)
    transform = {}

    while True:
      line = next(fin)
      m = re.match('Process (\d+):$', line)
      if m is None:
        assert line.startswith('Run 7 iterations.')
        break
      process_id = int(m.group(1))
      while True:
        line = next(fin)
        if line == '\n':
          break
        m = re.match(r'  send Value to process (\d+),$', line)
        if m is not None:
          receiver_id = int(m.group(1))
          receives_from[receiver_id].append(process_id)
          continue
        m = re.match(r'  Value <- (-?\d+ \* |)\w / 64(| \+ \d+| -\d+)\.', line)
        if m is not None:
          if m.group(1):
            a = int(m.group(1).replace('*', ''))
          else:
            a = 1
          if m.group(2):
            b = int(m.group(2))
          else:
            b = 1
          transform[process_id] = a, b
          continue
        assert (
            re.match(r'  .* <- receive\(4\),$', line) or
            re.match(r'  \w <- .*[.,]$', line) or
            re.match(r'  Value <- (-?\d+ \* |)(\w) / 64(| \+ \d+| -\d+)\.', line)
          ), repr(line)

  print 'done'
  print 'Checking...',
  sys.stdout.flush()
  assert all(len(q) == 4 for q in receives_from.values())
  assert set(receives_from) == set(transform) == set(range(1 << 20))
  print 'done'

  if not os.path.exists('fractal'):
    os.mkdir('fractal')

  screen = [randrange(256) for _ in range(1 << 20)]
  for stage in range(8):
    print 'Stage', stage
    screen2 = []
    for i in range(1 << 20):
      s = sum(screen[q] for q in receives_from[i])
      s = (s + 2) // 4
      a, b = transform[i]
      s = a * s // 64 + b
      if s < 0:
        s = 0
      if s > 255:
        s = 255
      screen2.append(s)
    screen = screen2
    hz = Image.fromstring('L', (1024, 1024), ''.join(map(chr, screen)))
    hz.save('fractal/stage{}.png'.format(stage))
