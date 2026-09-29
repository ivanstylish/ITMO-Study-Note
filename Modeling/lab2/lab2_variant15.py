from itertools import product
from pathlib import Path
import json
import numpy as np

B = 10.0
WEIGHTS = np.array([0.7, 0.2, 0.1])
CV = 1.6
ALPHA = (1 + np.sqrt((CV**2 - 1) / (CV**2 + 1))) / 2
RATES = np.array([2 * ALPHA / B, 2 * (1 - ALPHA) / B])


def stationary(q):
    """解 pi Q = 0，并用归一化方程替换最后一列"""
    a = q.T.copy()
    a[-1] = 1
    rhs = np.zeros(len(q))
    rhs[-1] = 1
    pi = np.linalg.solve(a, rhs)
    assert pi.min() > -1e-12
    assert np.max(np.abs(pi @ q)) < 1e-12
    assert abs(pi.sum() - 1) < 1e-12
    return pi


def system1(lam):
    # (busy1, busy2, busy3, queue); 有排队时三台必须全部忙碌
    states = [(*s, 0) for s in product(range(2), repeat=3)]
    states += [(1, 1, 1, k) for k in range(1, 4)]
    index = {s: i for i, s in enumerate(states)}
    q = np.zeros((11, 11))
    for k, s in enumerate(states):
        idle = [j for j in range(3) if s[j] == 0]
        if idle:
            for j in idle:
                t = list(s)
                t[j] = 1
                q[k, index[tuple(t)]] += lam * WEIGHTS[j] / WEIGHTS[idle].sum()
        elif s[3] < 3:
            q[k, index[(*s[:3], s[3] + 1)]] += lam
        for j in range(3):
            if s[j]:
                t = list(s)
                if s[3]:
                    t[3] -= 1
                else:
                    t[j] = 0
                q[k, index[tuple(t)]] += 1 / B
    np.fill_diagonal(q, -q.sum(axis=1))
    pi = stationary(q)
    busy = pi @ np.array([s[:3] for s in states])
    length = sum(p * s[3] for p, s in zip(pi, states))
    loss = pi[-1]
    throughput = busy.sum() / B
    # 到达所见状态加权；满员时拒绝的到达不纳入时间平均。
    wait_num = sum(p * (s[3] + 1) / (3 / B)
                   for p, s in zip(pi, states) if sum(s[:3]) == 3 and s[3] < 3)
    wait = wait_num / (1 - loss)
    assert abs(length - throughput * wait) < 1e-10
    assert abs(length + busy.sum() - throughput * (wait + B)) < 1e-10
    assert abs(throughput - lam * (1 - loss)) < 1e-10
    grouped = np.array([sum(p for p,s in zip(pi,states) if sum(s)==n) for n in range(7)])
    weights = [1.0]
    for n in range(1,7):
        weights.append(weights[-1] * lam * B / min(n,3))
    assert np.max(np.abs(grouped - np.array(weights)/sum(weights))) < 1e-10
    return dict(states=states, q=q, pi=pi, busy=busy, L=length,
                N=length + busy.sum(), loss=loss, X=throughput,
                W=wait, T=wait + B, wait_num=wait_num)


def system2(lam):
    # n1=0..3，n2=0..2，h=0（空闲）、1（快相）、2（慢相）
    states = list(product(range(4), range(3), range(3)))
    index = {s: i for i, s in enumerate(states)}
    q = np.zeros((36, 36))
    arrivals = lam * WEIGHTS
    for k, s in enumerate(states):
        for j, cap in enumerate([3, 2]):
            if s[j] < cap:
                t = list(s); t[j] += 1
                q[k, index[tuple(t)]] += arrivals[j]
            if s[j] > 0:
                t = list(s); t[j] -= 1
                q[k, index[tuple(t)]] += 1 / B
        if s[2] == 0:
            for h, prob in [(1, ALPHA), (2, 1 - ALPHA)]:
                q[k, index[(s[0], s[1], h)]] += arrivals[2] * prob
        else:
            q[k, index[(s[0], s[1], 0)]] += RATES[s[2] - 1]
    np.fill_diagonal(q, -q.sum(axis=1))
    pi = stationary(q)
    busy = pi @ np.array([[int(x > 0) for x in s] for s in states])
    queues = pi @ np.array([[max(s[0]-1, 0), max(s[1]-1, 0), 0] for s in states])
    loss_i = pi @ np.array([[s[0] == 3, s[1] == 2, s[2] > 0] for s in states])
    x_i = np.array([busy[0]/B, busy[1]/B,
                   sum(p * (RATES[s[2]-1] if s[2] else 0) for p,s in zip(pi,states))])
    wait_i = np.zeros(3)
    for j, cap in enumerate([3, 2]):
        wait_i[j] = sum(p * s[j] * B for p,s in zip(pi,states) if s[j] < cap) / (1-loss_i[j])
    assert np.max(np.abs(queues - x_i * wait_i)) < 1e-10
    assert np.max(np.abs(x_i - arrivals*(1-loss_i))) < 1e-10
    wait = x_i @ wait_i / x_i.sum()
    u = (arrivals[0]*B)**np.arange(4); u /= u.sum()
    v = (arrivals[1]*B)**np.arange(3); v /= v.sum()
    w = np.array([1, arrivals[2]*ALPHA/RATES[0], arrivals[2]*(1-ALPHA)/RATES[1]])
    w /= w.sum()
    assert np.max(np.abs(pi - np.kron(np.kron(u,v),w))) < 1e-10
    assert abs(queues.sum()+busy.sum()-x_i.sum()*(wait+B)) < 1e-10
    return dict(states=states, q=q, pi=pi, busy=busy, queues=queues,
                loss_i=loss_i, x_i=x_i, wait_i=wait_i, L=queues.sum(),
                N=queues.sum()+busy.sum(), loss=WEIGHTS @ loss_i,
                X=x_i.sum(), W=wait, T=wait+B)


def export(folder):
    folder = Path(folder)
    folder.mkdir(exist_ok=True)
    result = {}
    for name, solve in [('system1', system1), ('system2', system2)]:
        r = solve(0.5)
        np.savetxt(folder / (name+'_Q.csv'), r['q'], delimiter=',', fmt='%.12g')
        result[name] = {k: (v.tolist() if isinstance(v,np.ndarray) else v) for k,v in r.items()}
    result['sweep'] = [{'lambda': float(x), **{f'{name}_{key}': float(solve(x)[key])
        for name,solve in [('s1',system1),('s2',system2)] for key in ['L','loss','X','T']}}
        for x in np.arange(0.1, 1.01, 0.1)]
    (folder/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    return result


if __name__ == '__main__':
    data = export(Path(__file__).parent / 'Calculation_data')
    for name in ['system1','system2']:
        print(name, {k: round(data[name][k], 8) for k in ['L','loss','X','W','T']})
