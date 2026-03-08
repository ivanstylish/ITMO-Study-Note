class Solver:
    def __init__(self, name):
        self.name = name

    def verify(self, eq, a, b):
        if eq.f(a) * eq.f(b) >= 0:
            return False, "Нет корня или несколько на интервале"
        return True, ""

    def solve(self, eq, a, b, eps):
        pass
