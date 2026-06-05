import random

def gen(n):
    while True:
        buf = list(range(1, n + 1))
        random.shuffle(buf)
        for v in buf:
            yield v

g = gen(233)

def ticket():
    print(f"1.  - {(str(g.__next__()).rjust(3), str(g.__next__()).rjust(3))} - / - ".replace("'", ""))

for _ in range(12):
    for _ in range(10):
        ticket()
    print()
