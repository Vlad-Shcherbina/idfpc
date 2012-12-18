from pprint import pprint
from collections import Counter
import os

import Image
import ImageDraw

from draw_lines import trace_lines, known_pages, pic, get_abc, render_page


CHAR_SIZE = 12


def extract_chars(trace):
  trace = iter(trace)
  prev_x = -100
  prev_y = -100

  chars = [[]]

  for x, y, _, _, clr in trace:
    vx = x - prev_x
    vy = y - prev_y
    if abs(vx) < CHAR_SIZE and abs(vy) < CHAR_SIZE:
      chars[-1].append((vx, vy, 1 if clr else 0))
    else:
      if chars[-1]:
        chars.append([])

    prev_x = x
    prev_y = y

  if chars[-1] == []:
    chars.pop()

  return [tuple(char) for char in chars if len(char) > 1]


def char_base(char):
  min_x = 0
  min_y = 0
  x = 0
  y = 0
  for dx, dy, _ in char:
    x += dx
    y += dy
    min_x = min(min_x, x)
    min_y = min(min_y, y)
  return min_x, min_y


def draw_char(draw, x, y, char):
  for dx, dy, clr in char:
    if clr != 0:
      draw.line((x, y, x+dx, y+dy), fill=1)
    x += dx
    y += dy


def trace_back(x, y, vx, vy, clr):
  x0 = x - vx
  y0 = y - vy

  if x0 < 0 or x0 >= pic.size[0]:
    return None
  if y0 < 0 or y0 >= pic.size[1]:
    return None

  a, b, c = get_abc(x0, y0)
  return x0, y0, vx^a, vy^b, clr^c
  #pass


def char_applies(x0, y0, char):
  x = x0
  y = y0
  prev_dx = prev_dy = None
  for dx, dy, clr in char:
    if x < 0 or y < 0 or x >= pic.size[0] or y >= pic.size[1]:
      return None

    if prev_dx is not None:
      a, b, c = get_abc(x, y)
      if dx ^ prev_dx != a or dy ^ prev_dy != b:
        return None

    x += dx
    y += dy

    prev_dx = dx
    prev_dy = dy

  vx, vy, clr = char[0]
  a, b, c = get_abc(x0, y0)
  return (x0, y0, vx^a, vy^b, 0)


if __name__ == '__main__':
  chars = []
  for addr in known_pages:
    chars += extract_chars(trace_lines(*addr))

  freqs = Counter(chars)

  img = Image.new('1', (300, 300))
  draw = ImageDraw.Draw(img)

  x = 15
  y = 15
  for char, _ in freqs.most_common(49):
    draw_char(draw, x, y, char)
    x += 30
    if x + 15 > img.size[0]:
      x = 15
      y += 30

  img.save('chars.png')

  generated_by = {}
  for char, _ in freqs.most_common(10):
    for x in range(pic.size[0]):
      for y in range(pic.size[1]):
        q = char_applies(x, y, char)
        if q:
          if q not in generated_by:
            for q1 in trace_lines(*q):
              generated_by[q1] = q

  if not os.path.exists('page_candidates'):
    os.mkdir('page_candidates')

  for i, q in enumerate(set(generated_by.values())):
    while True:
      q2 = trace_back(*q)
      if q2 is None:
        break
      q = q2

    print 'rendering', i
    render_page(*q).save('page_candidates/page{:03}.png'.format(i))
