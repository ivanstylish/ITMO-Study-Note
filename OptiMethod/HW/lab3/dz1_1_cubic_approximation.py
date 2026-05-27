#!/usr/bin/env python3

import numpy as np

def f(x):
    return np.tan(x) - 2.0 * np.sin(x)

def df(x):
    return 1.0 / (np.cos(x) ** 2) - 2.0 * np.cos(x)

def cubic_approximation(f, df, a, b, eps=1e-4, max_iter=200):
    x1, x2 = float(a), float(b)
    df1, df2 = df(x1), df(x2)
    if df1 * df2 >= 0:
        raise ValueError(
            "Condition f'(x1)*f'(x2)<0 not satisfied: "
            f"f'({x1})={df1}, f'({x2})={df2}"
        )
    history = []
    for k in range(1, max_iter + 1):
        h = x2 - x1
        if abs(h) < eps:
            x0 = (x1 + x2) / 2.0
            history.append(dict(iter=k, x1=x1, x2=x2, x0=x0,
                              f0=f(x0), df0=df(x0),
                              z=None, omega=None, mu=None, stop=True))
            return x0, f(x0), history
        y1, y2 = f(x1), f(x2)
        y11, y12 = df(x1), df(x2)
        # z = f'(x1) + f'(x2) - 3*(f(x2)-f(x1))/(x2-x1)
        z = y11 + y12 - 3.0 * (y2 - y1) / h
        # omega = sqrt(z^2 - f'(x1)*f'(x2))
        disc = max(z * z - y11 * y12, 0.0)
        omega = np.sqrt(disc)
        # mu = (omega + z - y1') / (2*omega - y1' + y2')
        denom = 2.0 * omega - y11 + y12
        if abs(denom) > 1e-15:
            mu = (omega + z - y11) / denom
        else:
            mu = 0.5
        mu = max(0.0, min(1.0, mu))
        x0 = x1 + mu * h
        f0, df0 = f(x0), df(x0)
        stop = abs(df0) < eps
        history.append(dict(iter=k, x1=x1, x2=x2, x0=x0,
                          f0=f0, df0=df0,
                          z=z, omega=omega, mu=mu, stop=stop))
        if stop:
            return x0, f0, history
        if df0 < 0:
            x1 = x0 # min on the left of X0 
        else:
            x2 = x0 # min on the right of x0 
    x0 = (x1 + x2) / 2.0
    return x0, f(x0), history


def print_table(history):
    sep = "-" * 90
    print(sep)
    print(f"{'k':>3} {'x1':>10} {'x2':>10} {'z':>10} {'omega':>10} "
          f"{'mu':>10} {'x0':>10} {'f(x0)':>10} {'df(x0)':>10} {'Stop':>5}")
    print(sep)
    for r in history:
        zs = f"{r['z']:>10.6f}" if r['z'] is not None else "       ---"
        ws = f"{r['omega']:>10.6f}" if r['omega'] is not None else "       ---"
        ms = f"{r['mu']:>10.6f}" if r['mu'] is not None else "       ---"
        ss = "Yes" if r['stop'] else "No"
        print(f"{r['iter']:>3} {r['x1']:>10.6f} {r['x2']:>10.6f} "
              f"{zs} {ws} {ms} {r['x0']:>10.6f} "
              f"{r['f0']:>10.6f} {r['df0']:>10.6f} {ss:>5}")
    print(sep)


if __name__ == "__main__":
    print("=" * 65)
    print("DZ 1.1 -- Cubic Approximation (Hermite polynomial)")
    print("f(x) = tg(x) - 2sin(x), [0, pi/4], eps = 0.0001")
    print("=" * 65)

    a, b = 0.0, np.pi / 4.0
    print(f"\n>> Unimodality check:")
    print(f"   f'({a:.6f}) = {df(a):.6f}")
    print(f"   f'({b:.6f}) = {df(b):.6f}")
    print(f"   Product = {df(a)*df(b):.6f} < 0  [OK]")

    x_opt, f_opt, hist = cubic_approximation(f, df, a, b, eps=1e-4)

    print(f"\n>> Iteration table:")
    print_table(hist)

    x_exact = np.arccos(2.0**(-1.0/3.0))
    print(f"\n{'='*65}")
    print("FINAL RESULTS")
    print(f"  x*       = {x_opt:.10f}")
    print(f"  f(x*)    = {f_opt:.10f}")
    print(f"  x*_exact = {x_exact:.10f}")
    print(f"  Error    = {abs(x_opt - x_exact):.2e}")
    print(f"  Iterations: {len(hist)}")
    print(f"{'='*65}")

    # Detailed manual calculation (first 3 iterations)
    print(f"\n{'='*65}")
    print("DETAILED MANUAL CALCULATION (3 iterations)")
    print(f"{'='*65}")
    for i, r in enumerate(hist[:3]):
        x1, x2 = r['x1'], r['x2']
        h = x2 - x1
        y1, y2 = f(x1), f(x2)
        y11, y12 = df(x1), df(x2)
        print(f"\n=== Iteration {i+1} ===")
        print(f"  x1 = {x1:.10f}, x2 = {x2:.10f}, h = {h:.10f}")
        print(f"  y1 = f(x1)  = {y1:.10f}")
        print(f"  y2 = f(x2)  = {y2:.10f}")
        print(f"  y1'= f'(x1) = {y11:.10f}")
        print(f"  y2'= f'(x2) = {y12:.10f}")
        print(f"  z = y1'+y2'-3(y2-y1)/h = {r['z']:.10f}")
        print(f"  w = sqrt(z^2 - y1'*y2') = {r['omega']:.10f}")
        print(f"  mu= (w+z-y1')/(2w-y1'+y2') = {r['mu']:.10f}")
        print(f"  x0 = x1 + mu*h = {r['x0']:.10f}")
        print(f"  f(x0) = {r['f0']:.10f}")
        print(f"  f'(x0)= {r['df0']:.10f}")
        status = "STOP (|f'|<eps)" if r['stop'] else "CONTINUE (|f'|>=eps)"
        print(f"  |f'(x0)| = {abs(r['df0']):.10f} -> {status}")
