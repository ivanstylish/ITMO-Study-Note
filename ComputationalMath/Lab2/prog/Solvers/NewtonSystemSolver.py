import numpy as np


class NewtonSystemSolver:
    def init(self):
        self.name = "Метод Ньютона для решения систем"

    def solve(self, sys_eq, x0, y0, eps):
        if sys_eq.f_sys is None or sys_eq.jac is None:
            return None, 0, [["\033[33mОшибка: не задана f_sys или jac\033[0m"]]
        p = np.array([x0, y0], dtype=float)
        iter_count = 0
        table = []
        while True:
            iter_count += 1
            F = np.array(sys_eq.f_sys(p))
            J = sys_eq.jac(p)
            try:
                delta = np.linalg.solve(J, -F)
            except np.linalg.LinAlgError:
                return None, iter_count, [["Якобиан вырожден"]]
            p_new = p + delta
            gap = np.abs(p_new - p)
            max_d = np.max(gap)
            table.append([iter_count, round(p[0], 3), round(p[1], 3),
                          round(p_new[0], 3), round(p_new[1], 3),
                          round(F[0], 3), round(F[1], 3), round(max_d, 3)])
            if max_d < eps:
                return p_new, iter_count, table
            p = p_new
