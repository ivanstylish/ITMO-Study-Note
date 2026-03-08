import numpy as np
from Solvers.Solver import Solver

class SimpleIterationSolver(Solver):
    def __init__(self):
        super().__init__("Метод простой итерации")

    def solve(eq, a, b, eps):
        if eq.phi is None or eq.dphi is None:
            return None, "Нет phi", []
        x_vals = np.linspace(a, b, 100)
        max_dphi = max(abs(eq.dphi(xv)) for xv in x_vals)
        if max_dphi >= 1:
            return None, "Метод не сходится", []
        x = (a + b) / 2
        iter_count = 0
        table = []
        while True:
            iter_count += 1
            x_new = eq.phi(x)
            fx_new = eq.f(x_new)
            diff = abs(x_new - x)
            table.append([iter_count, round(x, 3), round(x_new, 3), round(fx_new, 3), round(diff, 3)])
            if diff < eps:
                return x_new, iter_count, table
            x = x_new



