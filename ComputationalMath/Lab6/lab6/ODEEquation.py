import math
class ODEEquation:
    def __init__(self, label: str, f, exact, exact_info: str,
                 default_x0: float, default_y0: float, default_xn: float):
        self.label = label
        self.f = f
        self.exact = exact
        self.exact_info = exact_info
        self.default_x0 = default_x0
        self.default_y0 = default_y0
        self.default_xn = default_xn

    def f_safe(self, x: float, y: float) -> float:
        try:
            val = self.f(x, y)
            if not math.isfinite(val):
                raise ValueError(
                    f"f({x:.4f}, {y:.4f}) = {val}  (не конечное число)"
                )
            return val
        except ZeroDivisionError:
            raise ValueError(f"Деление на ноль в f({x:.4f}, {y:.4f})")
        except OverflowError:
            raise ValueError(f"Переполнение в f({x:.4f}, {y:.4f})")

    def exact_safe(self, x: float, x0: float, y0: float) -> float:
        try:
            val = self.exact(x, x0, y0)
            if not math.isfinite(val):
                raise ValueError(
                    f"Точное решение в x={x:.4f} не конечно: {val}"
                )
            return val
        except (ZeroDivisionError, OverflowError) as e:
            raise ValueError(
                f"Ошибка точного решения в x={x:.4f}: {e}"
            )


