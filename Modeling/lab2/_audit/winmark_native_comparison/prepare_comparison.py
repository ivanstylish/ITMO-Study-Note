from pathlib import Path
import struct
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Calculation_data/WinMark/NativeComparison'
OUT.mkdir(exist_ok=True)
def string(s):
    b=s.encode('ascii')
    return (bytes([len(b)]) if len(b)<255 else b'\xff'+struct.pack('<H',len(b)))+b
def read(n):
    b=(ROOT/f'Calculation_data/WinMark/system{n}.mrk').read_bytes()
    size=struct.unpack_from('<H',b,51)[0]
    q=np.frombuffer(b,dtype='<f4',count=size*size,offset=53).reshape(size,size).copy()
    return b,q
b1,q1=read(1);_,q2=read(2)
n1,n2=len(q1),len(q2);n=n1*n2
# Independent product chain preserves both original models as its marginals.
q=np.kron(q1,np.eye(n2,dtype=np.float32))+np.kron(np.eye(n1,dtype=np.float32),q2)
ids=np.full((n,n),-1,dtype='<i4');coefs=np.ones((n,n),dtype='<f4')
for a in range(n1):
 for b in range(n2):
  k=a*n2+b
  for c in range(n1):
   if c!=a and q1[a,c]>0 and c>a:
    ids[k,c*n2+b]=0;coefs[k,c*n2+b]=q1[a,c]/.5
  for c in range(n2):
   if c!=b and q2[b,c]>0 and c>b:
    ids[k,a*n2+c]=0;coefs[k,a*n2+c]=q2[b,c]/.5
def weighted(which):
 terms=[]
 for a in range(n1):
  for b in range(n2):
   weight=max(a-7,0) if which==1 else max(b//9-1,0)+max((b%9)//3-1,0)
   if weight:terms.append((f'{weight}*' if weight!=1 else '')+f'p{a*n2+b}')
 return '+'.join(terms)
formulas=[('LQ1',weighted(1)),('LQ2',weighted(2))]
header=bytearray(b1[:49]);header[:2]=struct.pack('<H',2)
# One named element, followed by its value, variation start and increment.
data=header+struct.pack('<H',1)+string('lambda')+struct.pack('<fff',.5,.5,0)+struct.pack('<H',n)
data+=q.astype('<f4').tobytes()+ids.tobytes()+coefs.tobytes()+bytes(n*4)
data+=b1[53+n1*n1*12+n1*4:53+n1*n1*12+n1*4+16]
for name,expr in formulas:data+=string(expr+'#')+string(name)+bytes(4)
data+=b1[-84:]
assert n==396 and np.max(abs(q.sum(axis=1)))<2e-7
assert np.count_nonzero(ids==0)==1365
assert len(formulas)==2 and all(len(expr)<65535 for _,expr in formulas)
(OUT/'comparison_input_v3.mrk').write_bytes(data)
(OUT/'formulas.tsv').write_text('name\tformula\n'+'\n'.join(k+'\t'+v for k,v in formulas)+'\n',encoding='utf-8')
print('Native comparison input created:',n,'joint states; original matrices unchanged')
