import ODEEquation
from methods.ODEsolver import ODESolver


class EulerMethod(ODESolver):
    """
    y_{i+1} = y_i + h · f(x_i, y_i)
    """

    name = "Эйлера"
    order = 1

    def solve(self, eq: ODEEquation, x0: float, y0: float,
              xn: float, h: float, **_) -> tuple:
        xs, ys = [x0], [y0]
        x, y = x0, y0
        while x + h <= xn + 1e-12:
            y = y + h * eq.f_safe(x, y)
            x = self._next_x(x, h)
            self._guard(y, x, self.name)
            xs.append(x)
            ys.append(y)
        return xs, ys