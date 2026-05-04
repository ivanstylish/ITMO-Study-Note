from ODEEquation import ODEEquation
from methods.ODEsolver import ODESolver


class RungeKutta4(ODESolver):
    """
        k1 = h·f(x_i,       y_i)
        k2 = h·f(x_i + h/2, y_i + k1/2)
        k3 = h·f(x_i + h/2, y_i + k2/2)
        k4 = h·f(x_i + h,   y_i + k3)
        y_{i+1} = y_i + (k1 + 2k2 + 2k3 + k4) / 6
    """

    name  = "Рунге-Кутта 4"
    order = 4

    def solve(self, eq: ODEEquation, x0: float, y0: float,
              xn: float, h: float, **_) -> tuple:
        xs, ys = [x0], [y0]
        x, y = x0, y0
        while x + h <= xn + 1e-12:
            k1 = h * eq.f_safe(x,       y)
            k2 = h * eq.f_safe(x + h/2, y + k1/2)
            k3 = h * eq.f_safe(x + h/2, y + k2/2)
            k4 = h * eq.f_safe(x + h,   y + k3)
            y  = y + (k1 + 2*k2 + 2*k3 + k4) / 6
            x  = self._next_x(x, h)
            self._guard(y, x, self.name)
            xs.append(x)
            ys.append(y)
        return xs, ys