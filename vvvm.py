import re
import struct
import sys
from timeit import default_timer

MEMORY_SIZE = 13371111


def decode_instr(instr):
  """ Return pair (opcode, d_ip) """
  opcode = instr >> 16
  d_ip = (instr + 32768) % 65536 - 32768
  return opcode, d_ip


class VM(object):
  def __init__(self, memory, ip):
    self.memory = memory[:]
    self.ip = ip

  def step(self):
    instr = self.memory[self.ip]
    opcode, d_ip = decode_instr(instr)
    if 1 <= opcode <= 8:
      op1 = self.memory[self.ip + self.memory[self.ip + 2]]
      op2 = self.memory[self.ip + 3]
      if opcode == 1:
        result = op1 + op2
      elif opcode == 2:
        result = op1 - op2
      elif opcode == 3:
        result = op1 * op2
      elif opcode == 4:
        result = op1 // op2
      elif opcode == 5:
        result = op1 & op2
      elif opcode == 6:
        result = op1 | op2
      elif opcode == 7:
        result = op1 << op2
      elif opcode == 8:
        result = op1 >> op2
      else:
        assert False
      result = ((result + 0x80000000) & 0xFFFFFFFF) - 0x80000000
      self.memory[self.ip + self.memory[self.ip + 1]] = result
    elif opcode == 9:
      self.memory[self.ip + self.memory[self.ip + 1]] = ~self.memory[self.ip + 2]
    elif opcode == 10:
      if self.memory[self.ip + 2] < self.memory[self.ip + 3]:
        self.ip += self.memory[self.ip + 1] - d_ip
    elif opcode == 11:
      sys.stdout.write(chr(self.memory[self.ip + 1]))
    else:
      assert False, 'unrecognized opcode {} at {}'.format(opcode, self.ip)

    self.ip += d_ip


if __name__ == '__main__':
  with open('pic.bmp', 'rb') as fin:
    data = fin.read()

  data_start = data.find('###')
  data_segment = data[data_start:]

  assert len(data_segment) % 4 == 0
  data_segment = [
      struct.unpack('<i', data_segment[i:i+4])[0]
      for i in range(0, len(data_segment), 4)]

  print len(data_segment)

  memory = [0] * MEMORY_SIZE
  memory[:len(data_segment)] = data_segment

  start = default_timer()
  n = 0

  vm = VM(memory, 36)
  try:
    while True:
      vm.step()
      n += 1
      if n % 100000000 == 0:
        sys.stdout.flush()
        print>>sys.stderr, n / (default_timer() - start), 'steps per second'
  finally:
    sys.stdout.flush()
    print>>sys.stderr, 'it took', default_timer() - start, 's'


