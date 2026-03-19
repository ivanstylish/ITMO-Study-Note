import math


class Functions:

    @staticmethod
    def polynomial_v15(x: float) -> float:
        return 5 * x ** 3 - 2 * x ** 2 + 3 * x - 15

    @staticmethod
    def cos_x(x: float) -> float:
        return math.cos(x)

    @staticmethod
    def ln_x(x: float) -> float:
        if x <= 0:
            raise ValueError("ln(x) не определён при x ≤ 0")
        return math.log(x)

    @staticmethod
    def x_sq_minus_4(x: float) -> float:
        return x ** 2 - 4

    @staticmethod
    def sin_over_x(x: float) -> float:
        if x == 0:
            return 1.0
        return math.sin(x) / x

    @staticmethod
    def inv_sqrt_1_minus_x2(x: float) -> float:
        val = 1 - x ** 2
        if val <= 0:
            raise ValueError("Разрыв: 1 − x^2 ≤ 0")
        return 1.0 / math.sqrt(val)

    @staticmethod
    def inv_x(x: float) -> float:
        if x == 0:
            raise ValueError("Разрыв в точке x = 0")
        return 1.0 / x

    @staticmethod
    def inv_x_square(x: float) -> float:
        if x == 0:
            raise ValueError("Разрыв в точке x = 0")
        return 1.0 / x ** 2

    @staticmethod
    def _zero_in(a: float, b: float) -> bool:
        """0 находится внутри или на границе [a, b]"""
        return a <= 0 <= b

    @staticmethod
    def _zero_left(a: float, b: float) -> bool:
        return a <= 0 < b

    @staticmethod
    def _endpoints_pm1(a: float, b: float) -> bool:
        return (abs(a) >= 1 or abs(b) >= 1) and not (a > 1 or b < -1)


    @classmethod
    def _make_registry(cls) -> dict:
        def no_disc(a, b):  return False

        def proper(a, b):   return None

        return {
            "5x^3 - 2x^2 + 3x - 15": {
                "func": cls.polynomial_v15,
                "discontinuity": no_disc,
                "convergent": proper,
            },
            "cos(x)": {
                "func": cls.cos_x,
                "discontinuity": no_disc,
                "convergent": proper,
            },
            "ln(x)": {
                "func": cls.ln_x,
                "discontinuity": cls._zero_left,
                "convergent": lambda a, b: True if cls._zero_left(a, b) else None,
            },
            "x^2 - 4": {
                "func": cls.x_sq_minus_4,
                "discontinuity": no_disc,
                "convergent": proper,
            },
            "sin(x)/x": {
                "func": cls.sin_over_x,
                "discontinuity": no_disc,
                "convergent": proper,
            },
            "1/sqrt(1-x^2)": {
                "func": cls.inv_sqrt_1_minus_x2,
                "discontinuity": cls._endpoints_pm1,
                "convergent": lambda a, b: True if cls._endpoints_pm1(a, b) else None,
            },
            "1/x": {
                "func": cls.inv_x,
                "discontinuity": cls._zero_in,
                "convergent": lambda a, b: (
                    False if cls._zero_in(a, b)
                    else None
                ),
            },
            "1/x^2": {
                "func": cls.inv_x_square,
                "discontinuity": cls._zero_in,
                "convergent": lambda a, b: (
                    False if cls._zero_in(a, b)
                    else None
                ),
            },
        }

    REGISTRY: dict = {}


Functions.REGISTRY = Functions._make_registry()