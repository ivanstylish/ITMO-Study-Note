from pathlib import Path
import sys, struct, json
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import lab2_variant15 as model
OUT = ROOT/'Calculation_data/WinMark'

def read_project(path):
    data=path.read_bytes()
    count=struct.unpack_from('<H',data,0)[0]
    n=struct.unpack_from('<H',data,51)[0]
    q=np.frombuffer(data,dtype='<f4',count=n*n,offset=53).reshape(n,n).astype(float)
    pi=np.frombuffer(data,dtype='<f4',count=n,offset=53+n*n*12).astype(float)
    offset=53+n*n*12+n*4+16
    def string():
        nonlocal offset
        length=data[offset];offset+=1
        if length==255:
            length=struct.unpack_from('<H',data,offset)[0];offset+=2
        value=data[offset:offset+length].decode('ascii');offset+=length
        return value
    formulas={}
    for _ in range(count):
        expr=string();name=string();value=struct.unpack_from('<f',data,offset)[0];offset+=4
        formulas[name]={'formula':expr.rstrip('#'),'value':value}
    return q,pi,formulas

def expected(system,lam):
    r=[None,model.system1,model.system2][system](lam)
    e={'A':lam*10,'U':sum(r['busy']),'L':r['L'],'N':r['N'],
       'R':r['loss'],'X':r['X'],'W':r['W'],'T':r['T']}
    for i in range(3):
        j=i+1;e[f'A{j}']=lam*model.WEIGHTS[i]*10;e[f'U{j}']=r['busy'][i]
        if system==1:
            e[f'L{j}']=r['L']/3;e[f'X{j}']=r['busy'][i]/10
            e[f'W{j}']=lam*r['wait_num']/(3*e[f'X{j}'])
        else:
            e[f'L{j}']=r['queues'][i];e[f'R{j}']=r['loss_i'][i]
            e[f'X{j}']=r['x_i'][i];e[f'W{j}']=r['wait_i'][i]
        e[f'N{j}']=r['busy'][i]+e[f'L{j}'];e[f'T{j}']=e[f'W{j}']+10
    if system==1:e['D']=r['wait_num']
    return r,e

checks=[]
for system in (1,2):
    for step in range(0,11):
        lam=.5 if step==0 else step/10
        tag='complete' if step==0 else f'lambda{step:02}'
        name=f'system{system}_{tag}'
        path=OUT/f'system{system}.mrk' if step==0 else OUT/'Variation'/f'{name}.mrk'
        if not path.exists():raise FileNotFoundError(path)
        assert path.with_suffix('.html').exists()
        q,pi,f=read_project(path);r,e=expected(system,lam)
        qerror=float(abs(q-r['q']).max());perror=float(abs(pi-r['pi']).max())
        errors={k:abs(f[k]['value']-v) for k,v in e.items()}
        assert qerror<1e-7,(name,qerror)
        assert perror<2e-6,(name,perror)
        assert abs(pi.sum()-1)<2e-6,(name,pi.sum())
        assert max(errors.values())<.001,(name,errors)
        checks.append({'model':name,'lambda':lam,'q_max_error':qerror,
          'pi_max_error':perror,'balance_residual':float(abs(pi@q).max()),
          'metrics_max_error':max(errors.values()),
          'metrics':{k:v['value'] for k,v in f.items()},'metrics_errors':errors})
result={'source':'Actual WinMark saved projects after calculation; HTML exported by WinMark',
        'models_checked':len(checks),'checks':checks}
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified',len(checks),'native WinMark computations')
print('max pi error',max(c['pi_max_error'] for c in checks))
print('max metric error',max(c['metrics_max_error'] for c in checks))
for c in checks:
    if 'complete' in c['model']:print(c['model'],{k:c['metrics'][k] for k in ['L','N','R','X','W','T']})
