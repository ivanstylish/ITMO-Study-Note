import numpy as np


class SimpleIterationSystemSolver:
    def __init__(self):
        self.name = "Метод простой итерации для решения систем"

    def solve(self, sys_eq, x0, y0, eps):
        if sys_eq.phi_sys is None:
            return None, 0, [["\033[33mОшибка: не задана функция phi_sys\033[0m"]]

        p = np.array([x0, y0], dtype=float)
        iter_count = 0
        table = []

        while True:
            iter_count += 1
            p_new = np.array(sys_eq.phi_sys(p), dtype=float)

            diffs = np.abs(p_new - p)
            max_d = np.max(diffs)

            table.append([iter_count, round(p[0], 3), round(p[1], 3),
                          round(p_new[0], 3), round(p_new[1], 3), round(max_d, 3)])

            if max_d < eps:
                return p_new, iter_count, table

            p = p_new