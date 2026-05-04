import ODEEquation
from color import Color

class TablePrinter:

    _W = 62

    @classmethod
    def print(cls, solver_name: str, eq: ODEEquation,
              x0: float, y0: float, xs: list, ys: list) -> float:
        sep = "─" * cls._W
        print(f"\n{Color.header(sep)}")
        print(Color.header(f"  Метод: {solver_name}"))
        print(Color.header(sep))
        print(f"  {'i':>4}  {'x_i':>8}  {'y_i':>13}  {'y_exact':>13}  {'|err|':>11}")
        print(Color.header(sep))

        max_err = 0.0
        for i, (x, y) in enumerate(zip(xs, ys)):
            try:
                ye = eq.exact_safe(x, x0, y0)
                err = abs(ye - y)
                max_err = max(max_err, err)
                print(f"  {i:>4}  {x:>8.4f}  {y:>13.6f}  {ye:>13.6f}  {err:>11.2e}")
            except ValueError as e:
                print(Color.error(
                    f"  {i:>4}  {x:>8.4f}  {y:>13.6f}  {'N/A':>13}  {'N/A':>11}"
                ))
                Color.print_warn(str(e))

        print(Color.header(sep))
        print(Color.ok(f"  Максимальная погрешность: {max_err:.2e}"))
        return max_err