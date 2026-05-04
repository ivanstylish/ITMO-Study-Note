from ODEEquation import ODEEquation
from methods.ODEsolver import ODESolver
from methods.RungeKutta4 import RungeKutta4


class AdamsMethod(ODESolver):
    """
    Предиктор (явная схема 4-го порядка):
        y*_{i+1} = y_i + h/24·(55f_i - 59f_{i-1} + 37f_{i-2} - 9f_{i-3})

    Корректор (неявная схема 4-го порядка, итерационно):
        y_{i+1} = y_i + h/24·(9f(x_{i+1}, y*) + 19f_i - 5f_{i-1} + f_{i-2})
    """

    name      = "Адамса"
    order     = 4
    _MIN_STEP = 4
    _MAX_ITER = 50

    def solve(self, eq: ODEEquation, x0: float, y0: float,
              xn: float, h: float, eps: float = 1e-8, **_) -> tuple:

        n_steps = round((xn - x0) / h)
        if n_steps < self._MIN_STEP:
            raise ValueError(
                f"Метод Адамса требует ≥ {self._MIN_STEP} шагов. "
                f"При h={h} на [{x0}, {xn}] шагов: {n_steps}. "
                f"Уменьшите h."
            )

        # Стартовые значения (RK4)
        rk4 = RungeKutta4()
        xs, ys = rk4.solve(eq, x0, y0, self._next_x(x0, 3 * h), h)
        fs = [eq.f_safe(xs[i], ys[i]) for i in range(len(xs))]

        x = xs[-1]
        while x + h <= xn + 1e-12:
            fi, fi1, fi2, fi3 = fs[-1], fs[-2], fs[-3], fs[-4]

            # Предиктор
            y_pred = ys[-1] + h / 24 * (55*fi - 59*fi1 + 37*fi2 - 9*fi3)
            x_new  = self._next_x(x, h)
            self._guard(y_pred, x_new, f"{self.name}(предиктор)")

            # Корректор (итерации до сходимости)
            y_corr    = y_pred
            converged = False
            for _ in range(self._MAX_ITER):
                y_prev = y_corr
                f_new  = eq.f_safe(x_new, y_prev)
                y_corr = ys[-1] + h / 24 * (9*f_new + 19*fi - 5*fi1 + fi2)
                self._guard(y_corr, x_new, f"{self.name}(корректор)")
                if abs(y_corr - y_prev) < eps:
                    converged = True
                    break

            if not converged:
                raise ValueError(
                    f"Корректор Адамса не сошёлся за {self._MAX_ITER} итераций "
                    f"в точке x={x_new:.6f}. Попробуйте уменьшить h."
                )

            xs.append(x_new)
            ys.append(y_corr)
            fs.append(eq.f_safe(x_new, y_corr))
            x = x_new

        return xs, ys