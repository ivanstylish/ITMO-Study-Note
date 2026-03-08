from Solvers.Solver import Solver

class NewtonSolver(Solver):
    def __init__(self):
        super().__init__("Метод Ньютона")

    def solve(self, eq, a, b, eps):
        if eq.df is None:
            return None, "Нет производной", []

        def ddf(x):
            return -14.4 * x + 2.54
        if eq.f(a) * ddf(a) > 0:
            x = a
        else:
            x = b
        iteration_count = 0
        table = []
        while True:
            iteration_count += 1
            fx = eq.f(x)
            dfx = eq.df(x)
            newX = x - fx/dfx
            gap = abs(newX - x)
            table.append([iteration_count, round(x, 3), round(fx, 3), round(dfx, 3), round(newX, 3), round(gap, 3)])
            if gap < eps:
                return newX, iteration_count, table
            x = newX
