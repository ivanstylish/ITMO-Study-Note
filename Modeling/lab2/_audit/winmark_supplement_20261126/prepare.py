from pathlib import Path
from struct import pack
import numpy as np

work = Path(__file__).resolve().parent
root = work.parents[1]
base = root / 'Calculation_data/WinMark'
output = base / 'ReportSupplement'
output.mkdir(exist_ok=True)

def cstring(s):
    b = s.encode('ascii')
    size = bytes([len(b)]) if len(b) < 255 else b'\xff' + pack('<H', len(b))
    return size + b

def project(system, name, formulas):
    raw = (base / f'system{system}.mrk').read_bytes()
    n = 11 if system == 1 else 36
    q = np.frombuffer(raw, dtype='<f4', count=n*n, offset=53).reshape(n,n)
    links = np.full((n,n), -1, dtype='<i4')
    factors = np.ones((n,n), dtype='<f4')
    for i, j in zip(*np.nonzero(np.triu(q, 1))):
        links[i,j] = 0
        factors[i,j] = q[i,j] / .5
    assert (links == 0).sum() == (15 if system == 1 else 75)
    header = bytearray(raw[:49])
    header[:2] = pack('<H',len(formulas))
    header[29:33] = pack('<I',1)
    header[33:35] = pack('<H',1)
    header[35:37] = pack('<H',10)
    header[37:41] = pack('<I',1)
    offset = 53 + n*n*12
    native = header + pack('<H',1) + cstring('lambda') + pack('<fd',.1,.1) + pack('<H',n)
    native += q.tobytes() + links.tobytes() + factors.tobytes() + raw[offset:offset+n*4+16]
    native += pack('<fff',.1,.1,.1) + bytes((n+len(formulas))*10*4)
    for key, expr in formulas.items():
        native += cstring(expr+'#') + cstring(key) + bytes(4)
    native += raw[-84:]
    (work/f'{name}_input.mrk').write_bytes(native)

for system in (1,2):
    f = dict(line.split('\t',1) for line in (base/f'system{system}_formulas.tsv').read_text().splitlines()[1:])
    f.update(A1='7*lambda',A2='2*lambda',A3='lambda')
    if system == 1:
        for i in (1,2,3): f[f'W{i}']=f'lambda*D/(3*X{i})'
    else:
        for i,r in enumerate(('.7','.2','.1'),1): f[f'X{i}']=f'{r}*lambda*(1-R{i})'
    project(system,f'system{system}',f)

project(1,'comparison',{
    'rho1':'7*lambda','rho2':'2*lambda',
    'LQ1':'p8+2*p9+3*p10',
    'LQ2':'(rho1^2+2*rho1^3)/(1+rho1+rho1^2+rho1^3)+rho2^2/(1+rho2+rho2^2)',
    'Loss1':'p10',
    'Loss2':'0.7*rho1^3/(1+rho1+rho1^2+rho1^3)+0.2*rho2^2/(1+rho2+rho2^2)+0.1*lambda/(1+lambda)',
})
