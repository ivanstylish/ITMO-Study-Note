from Solvers.Solver import Solver

class ChordSolver(Solver):
    def __init__(self):
        super().__init__("Метод хорд")

    def solve(self, eq, a, b, eps):
        ok, msg = self.verify(eq, a, b)
        if not ok:
            return None, msg, []

        iteration_count = 0
        table = []
        prev_x = None

        while abs(b - a) > eps:
            iteration_count += 1
            fa = eq.f(a)
            fb = eq.f(b)
            if fb - fa == 0:
                return None, "Деление на ноль", table

            x = a - fa * (b - a) / (fb - fa)
            fx = eq.f(x)

            if prev_x is not None:
                gap = abs(x - prev_x)
            else:
                gap = abs(b - a)

            table.append([iteration_count, round(a, 3), round(b, 3), round(x, 3),
                          round(fa, 3), round(fb, 3), round(fx, 3), round(gap, 3)])

            if abs(fx) < eps:
                return x, iteration_count, table

            if fa * fx < 0:
                b = x
            else:
                a = x
        return x, iteration_count
