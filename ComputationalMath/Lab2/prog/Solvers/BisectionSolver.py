from Solvers.Solver import Solver


class BisectionSolver(Solver):
    def __init__(self):
        super().__init__("Метод половинного деления  ")

    def solve(self, eq, a, b, eps):
        ok, msg = self.verify(eq, a, b)
        if not ok:
            return None, msg, []

        iteration_count = 0
        table = []

        while abs(b - a) > eps or abs(eq.f((a + b) / 2)) > eps:
            x = (a + b) / 2
            iteration_count += 1
            fx = eq.f(x)

            table.append([iteration_count, round(a, 3), round(b, 3), round(x, 3),
                          round(eq.f(a), 3), round(eq.f(b), 3), round(fx, 3), round(abs(b - a), 3)])

            if abs(fx) < eps:
                return x, iteration_count, table

            if eq.f(a) * fx < 0:
                b = x
            else:
                a = x

        x = (a + b) / 2
        return x, iteration_count, table
