import math
import numpy as np


class SystemEquation:
    def __init__(self, name, f_sys, jac=None, phi_sys=None):
        self.name = name
        self.f_sys = f_sys
        self.jac = jac
        self.phi_sys = phi_sys


def sys_f1(p):
    x, y = p
    return [math.sin(x - 1) + y - 1.5,
            x - math.sin(y + 1) - 1]

def sys_phi1(p):
    x, y = p
    return [1 + math.sin(y + 1),
            1.5 - math.sin(x - 1)]

def sys_jac1(p):
    x, y = p
    return np.array([
        [math.cos(x - 1), 1],
        [1, -math.cos(y + 1)]
    ])

def sys_f2(p):
    x, y = p
    return [x**2 + y**2 - 1,
            x - y - 0.5]

def sys_phi2(p):
    x, y = p
    return [math.sqrt(1 - y**2) if abs(y) <= 1 else x,
            x - 0.5]

def sys_jac2(p):
    x, y = p
    return np.array([
        [2*x, 2*y],
        [1, -1]
    ])

def sys_f3(p):
    x, y = p
    return [math.exp(x) + y - 2,
            x**2 + y**2 - 4]

def sys_phi3(p):
    x, y = p
    return [math.log(2 - y) if 2-y > 0 else x,
            math.sqrt(4 - x**2) if 4-x**2 >= 0 else y]

def sys_jac3(p):
    x, y = p
    return np.array([
        [math.exp(x), 1],
        [2*x, 2*y]
    ])

sys_eq1 = SystemEquation("sin(x-1) + y = 1.5\n      x - sin(y+1) = 1", sys_f1, sys_jac1, sys_phi1)
sys_eq2 = SystemEquation("x^2 + y^2 = 1\n      x - y = 0.5", sys_f2, sys_jac2, sys_phi2)
sys_eq3 = SystemEquation("e^x + y = 2\n      x^2 + y^2 = 4", sys_f3, sys_jac3, sys_phi3)
system_equations = [sys_eq1, sys_eq2, sys_eq3]
