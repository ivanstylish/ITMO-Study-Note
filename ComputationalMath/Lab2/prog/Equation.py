import math

import numpy as np


class Equation:
    def __init__(self, name, f, df=None, phi=None, dphi=None):
        self.name = name
        self.f = f
        self.df = df
        self.phi = phi
        self.dphi = dphi


def f1(x):
    return -2.4 * x ** 3 + 1.27 * x ** 2 + 8.63 * x + 2.31

def df1(x):
    return -7.2 * x ** 2 + 2.54 * x + 8.63

def phi1(x):
    max_abs_df = max(abs(df1(y)) for y in np.linspace(-5, 5, 200))
    lam = -1.0 / max_abs_df if max_abs_df > 0 else -0.1
    return x + lam * f1(x)

def dphi1(x):
    max_abs_df = max(abs(df1(y)) for y in np.linspace(-5, 5, 200))
    lam = -1.0 / max_abs_df if max_abs_df > 0 else -0.1
    return 1 + lam * df1(x)

def f2(x):
    return math.sin(x - 2) + 4.58 * math.sin(x - 3)

def df2(x):
    return math.cos(x - 2) + 4.58 * math.cos(x - 3)

def phi2(x):
    return -math.sin(x - 2) - 4.58 * math.sin(x - 3)

def dphi2(x):
    return -math.cos(x - 2) - 4.58 * math.cos(x - 3)

def f3(x):
    return x - math.sin(x) - 0.1

def df3(x):
    return 1 - math.cos(x)

def phi3(x):
    return math.sin(x) + 0.1

def dphi3(x):
    return math.cos(x)

eq1 = Equation("-2.4x^3 + 1.27x^2 + 8.63x + 2.31", f1, df1, phi1, dphi1)
eq2 = Equation("sin(x - 2) + 4.58 * sin(x - 3)", f2, df2, phi2, dphi2)
eq3 = Equation("x - sin(x) = 0.1", f3, df3, phi3, dphi3)

equations = [eq1, eq2, eq3]
