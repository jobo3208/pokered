#!/usr/bin/env python3

"""Recompute the main save data checksum"""

import sys


hl = 0xa598
bc = 0x0f8b
a = 1
d = 0

offset = 0x8000


if __name__ == '__main__':
    save_file = sys.argv[1]

    with open(save_file, 'rb') as f:
        sav = bytearray(f.read())

    while a > 0:
        a = sav[hl - offset]
        hl += 1
        a = a + d
        d = a
        bc -= 1
        a = bc & 0xff00
        a = a | (bc & 0xff)

    a = d
    a = (a & 0x00ff) ^ 0xff
    print("hl:", hex(hl))
    print("a:", hex(a))
    sav[hl - offset] = a

    with open(save_file, 'wb') as f:
        f.write(sav)

    print("wrote new checksum to", save_file)
