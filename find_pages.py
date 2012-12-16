from pprint import pprint
from collections import Counter

import Image
import ImageDraw

from draw_lines import trace_lines, known_pages


CHAR_SIZE = 12


def extract_chars(trace):
  trace = iter(trace)
  prev_x = -100
  prev_y = -100

  chars = [[]]

  for x, y, clr in trace:
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


if __name__ == '__main__':
  chars = []
  for addr in known_pages:
    chars += extract_chars(trace_lines(*addr))

  freqs = Counter(chars)
  pprint(freqs.most_common(30))


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
