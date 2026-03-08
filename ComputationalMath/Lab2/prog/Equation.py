class Equation:
    def __init__(self, name, f, df=None, phi=None, dphi=None):
        self.name = name
        self.f = f
        self.df = df
        self.phi = phi
        self.dphi = dphi


def f(x):
    return -2.4 * x ** 3 + 1.27 * x ** 2 + 8.63 * x + 2.31

def df(x):
    return -7.2 * x ** 2 + 2.54 * x + 8.63

def phi(x):
    lam = -1 / 30.02
    return x + lam * f(x)


def dphi(x):
    lam = -1 / 30.02
    return 1 + lam * df(x)


eq = Equation("-2.4x^3 + 1.27x^2 + 8.63x + 2.31", f, df, phi, dphi)

