from Solvers.Solver import Solver


class SecantSolver(Solver):
    def __init__(self):
        super().__init__("Метод секущих")

    def solve(self, eq, a, b, eps):
        ok, msg = self.verify(eq, a, b)
        if not ok:
            return None, msg, []

        if eq.f(a) * eq.f(b) > 0:
            return None, "f(a) и f(b) одного знака -> корня гарантированно нет", []

        x_prev = a
        x_curr = b
        iteration_count = 0
        table = []

        MAX_X = 1e6
        MAX_ITER = 100

        while iteration_count < MAX_ITER:
            iteration_count += 1
            fx_prev = eq.f(x_prev)
            fx_curr = eq.f(x_curr)

            if abs(fx_curr) < eps:
                return x_curr, iteration_count, table

            denom = fx_curr - fx_prev
            if abs(denom) < 1e-12:
                return None, "Знаменатель близок к нулю (параллельная секущая)", table

            x_next = x_curr - fx_curr * (x_curr - x_prev) / denom

            if abs(x_next) > MAX_X:
                return None, f"Итерация ушла за пределы разумных значений (|x| > {MAX_X})", table

            gap = abs(x_next - x_curr)

            table.append([iteration_count, round(x_prev, 3), round(x_curr, 3),
                          round(x_next, 3), round(eq.f(x_next), 3), round(gap, 3)])

            if gap < eps:
                return x_next, iteration_count, table

            x_prev = x_curr
            x_curr = x_next

        return None, "Превышено максимальное число итераций", table
