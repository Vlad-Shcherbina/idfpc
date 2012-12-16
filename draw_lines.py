"""
  grep "###" pic.bmp --binary-files=text
produces
### These three # signs marked the beginning of data segment as well as first comment. Grep is your friend now.
### RGB triplets in this file do not really store colors.
### Each triplet of bytes correspoding to a pixel contains values A,B,C (in this order), each a signed 8-bit integer.
### Remember that BMP stores image upside-down, so first bytes of data segment are first triplets of last row of image.
### Let X=70 and Y=79 be coordinates of current pixel. Let VX=18 and VY=26 (signed 8-bit integers) be current vector. Let CLR=0.
### Loop: take values A,B,C from triplet corresponding to current pixel in this BMP.
### Xor VX with A, VY with B and CLR with C.
### If CLR is not 0 draw a line from (X,Y) to (X+VX,Y+VY).
### Add VX to X and VY to Y, repeat the loop until A=B=C=0.
### So first visited points should be (70,79), (70,87), (64,79), (64,87)...
### Codeword: play
"""

import Image
import ImageDraw


def signed_int8(x):
  return (x + 128) % 256 - 128


pic = Image.open('pic.bmp')
out = Image.new('L', pic.size)
draw = ImageDraw.Draw(out)


x, y = 70, 79
vx, vy = 18, 26
clr = 0

while True:
  out.putpixel((x, y), clr)
  c, b, a = map(signed_int8, pic.getpixel((x, y)))

  if a == b == c == 0:
    break

  vx ^= a
  vy ^= b
  clr ^= c

  if clr != 0:
    draw.line((x, y, x+vx, y+vy), fill=255)

  x += vx
  y += vy

out.save('lines.png')
