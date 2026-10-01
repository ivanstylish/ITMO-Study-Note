from pathlib import Path
import sys, struct, json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lab2_variant15 as model
OUT = ROOT / 'Calculation_data' / 'WinMark'
SEED = (ROOT / '_audit/formula_seed36.mrk').read_bytes()

def cstring(text):
    b = text.encode('ascii')
    return (bytes([len(b)]) if len(b) < 255 else b'\xff' + struct.pack('<H', len(b))) + b

def weighted(states, weight):
    terms = []
    for k, state in enumerate(states):
        w = weight(state)
        if w:
            terms.append((f'{w:g}*' if w != 1 else '') + f'p{k}')
    return '+'.join(terms) or '0'

def formulas(system, lam, states):
    f = []
    def add(name, expr):
        f.append((name, expr))
    for i, r in enumerate(model.WEIGHTS, 1):
        add(f'A{i}', f'{lam*r*10:.12g}')
        add(f'U{i}', weighted(states, lambda s: int(s[i-1] > 0)))
    add('A', 'A1+A2+A3')
    add('U', 'U1+U2+U3')
    if system == 1:
        add('L', weighted(states, lambda s: s[3]))
        add('R', 'p10')
        add('D', '(p7+2*p8+3*p9)/0.3')
        for i in range(1, 4):
            add(f'L{i}', 'L/3')
            add(f'N{i}', f'U{i}+L{i}')
            add(f'X{i}', f'0.1*U{i}')
            add(f'W{i}', f'{lam:.12g}*D/(3*X{i})')
            add(f'T{i}', f'W{i}+10')
        add('N', 'N1+N2+N3')
        add('X', 'X1+X2+X3')
        add('W', 'D/(1-R)')
        add('T', 'W+10')
    else:
        for i in range(1, 4):
            add(f'L{i}', weighted(states, lambda s: max(s[i-1]-1, 0) if i < 3 else 0))
            add(f'N{i}', f'U{i}+L{i}')
            cap = [3, 2, 1][i-1]
            add(f'R{i}', weighted(states, lambda s: int(s[i-1] == cap) if i < 3 else int(s[2] > 0)))
            add(f'X{i}', f'{lam*model.WEIGHTS[i-1]:.12g}*(1-R{i})')
            num = weighted(states, lambda s: s[i-1] if i < 3 and s[i-1] < cap else 0)
            add(f'W{i}', f'10*({num})/(1-R{i})' if i < 3 else '0')
            add(f'T{i}', f'W{i}+10')
        for name in ['L', 'N', 'X']:
            add(name, '+'.join(f'{name}{i}' for i in range(1, 4)))
        add('R', '0.7*R1+0.2*R2+0.1*R3')
        add('W', '(X1*W1+X2*W2+X3*W3)/X')
        add('T', 'W+10')
    return f

def build(system, lam, filename):
    r = [None, model.system1, model.system2][system](lam)
    q = r['q']; n = len(q)
    f = formulas(system, lam, r['states'])
    header = bytearray(SEED[:53])
    header[:2] = struct.pack('<H', len(f))
    header[51:53] = struct.pack('<H', n)
    data = header + q.astype('<f4').tobytes()
    data += struct.pack('<i', -1) * (n*n) + struct.pack('<f', 1) * (n*n)
    data += bytes(n*4) + SEED[15749:15765]
    for name, expr in f:
        data += cstring(expr+'#') + cstring(name) + bytes(4)
    data += SEED[-84:]
    (OUT / filename).write_bytes(data)
    (OUT / filename.replace('.mrk', '_formulas.tsv')).write_text(
        'name\tformula\n'+'\n'.join(name+'\t'+expr for name,expr in f)+'\n', encoding='utf-8')

if __name__ == '__main__':
    for system in [1, 2]:
        build(system, .5, f'system{system}_complete.mrk')
        for step in range(1, 11):
            build(system, step/10, f'system{system}_lambda{step:02}.mrk')
    print('Created native projects with full generators and state-based formulas.')
