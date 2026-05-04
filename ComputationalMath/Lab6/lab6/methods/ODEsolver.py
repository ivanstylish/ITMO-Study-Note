import math
import ODEEquation


class ODESolver:

    name: str = "ODESolver"
    order: int = 0

    def solve(self, eq: ODEEquation, x0: float, y0: float,
              xn: float, h: float, **kwargs) -> tuple:
        raise NotImplementedError

    @staticmethod
    def _next_x(x: float, h: float) -> float:
        return round(x + h, 12)

    @staticmethod
    def _guard(y: float, x: float, who: str) -> None:
        if not math.isfinite(y):
            raise ValueError(
                f"[{who}] Решение расходится в x={x:.6f}: y={y}"
            )