import ODEEquation
from methods.ODEsolver import ODESolver


class ErrorEstimator:

    @staticmethod
    def runge_estimate(solver: ODESolver, eq: ODEEquation,
                       x0: float, y0: float, xn: float,
                       h: float, eps: float) -> tuple:

        _, yh = solver.solve(eq, x0, y0, xn, h)
        _, yh2 = solver.solve(eq, x0, y0, xn, h / 2)
        p = solver.order
        R = abs(yh[-1] - yh2[-1]) / (2 ** p - 1)
        return R, R <= eps

    @staticmethod
    def max_norm_error(eq: ODEEquation, x0: float, y0: float,
                       xs: list, ys: list) -> float:
        return max(
            abs(eq.exact_safe(x, x0, y0) - y)
            for x, y in zip(xs, ys)
        )

    @staticmethod
    def pointwise_errors(eq: ODEEquation, x0: float, y0: float,
                         xs: list, ys: list) -> list:
        result = []
        for x, y in zip(xs, ys):
            try:
                result.append(abs(eq.exact_safe(x, x0, y0) - y))
            except ValueError:
                result.append(float("nan"))
        return result