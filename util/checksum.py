hl = 0xa598
bc = 0x0f8b
a = 0
d = 0

offset = 0x8000


with open('pokered.test.sav', 'rb') as f:
    sav = f.read()


while True:
    a = sav[hl - offset]
    hl += 1
    a = a + d
    d = a
    bc -= 1
    a = bc & 0xff00
    a = a | (bc & 0xff)
    if a == 0:
        print("hl:", hex(hl))
        a = d
        a = (a & 0x00ff) ^ 0xff
        print(hex(a))
        break
