import math
import numpy as np


class SystemEquation:
    def __init__(self, name, f_sys, jac=None, phi_sys=None):
        self.name = name
        self.f_sys = f_sys
        self.jac = jac
        self.phi_sys = phi_sys


def sys_f(p):
    x, y = p
    return [math.sin(x - 1) + y - 1.5, x - math.sin(y + 1) - 1]


def sys_phi(p):
    x, y = p
    return [1 + math.sin(y + 1), 1.5 - math.sin(x - 1)]


def sys_jac(p):
    x, y = p
    return np.array([
        [math.cos(x - 1), 1],
        [1, -math.cos(y + 1)]
    ])


sys_eq = SystemEquation("sin(x-1) + y = 1.5; x - sin(y+1) = 1", sys_f, sys_jac, sys_phi)

system_equations = [sys_eq]
