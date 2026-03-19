class FuncType:
    pass


class Methods:

    @staticmethod
    def integrate_rectangle_left(func: FuncType, a: float, b: float, n: int) -> float:
        h = (b - a) / n
        return h * sum(func(a + i * h) for i in range(n))

    @staticmethod
    def integrate_rectangle_right(func: FuncType, a: float, b: float, n: int) -> float:
        h = (b - a) / n
        return h * sum(func(a + (i + 1) * h) for i in range(n))

    @staticmethod
    def integrate_rectangle_middle(func: FuncType, a: float, b: float, n: int) -> float:
        h = (b - a) / n
        return h * sum(func(a + (i + 0.5) * h) for i in range(n))

    @staticmethod
    def integrate_trapezoid(func: FuncType, a: float, b: float, n: int) -> float:
        h = (b - a) / n
        result = (func(a) + func(b)) / 2.0
        result += sum(func(a + i * h) for i in range(1, n))
        return h * result

    @staticmethod
    def integrate_simpson(func: FuncType, a: float, b: float, n: int) -> float:
        if n % 2 != 0:
            n += 1
        h = (b - a) / n
        result = func(a) + func(b)
        result += 4 * sum(func(a + i * h) for i in range(1, n, 2))
        result += 2 * sum(func(a + i * h) for i in range(2, n - 1, 2))
        return h / 3.0 * result


    REGISTRY: dict = {
        "левые": {
            "func": integrate_rectangle_left.__func__,
            "order": 1,
        },
        "правые": {
            "func": integrate_rectangle_right.__func__,
            "order": 1,
        },
        "средние": {
            "func": integrate_rectangle_middle.__func__,
            "order": 2,
        },
        "Метод трапеций": {
            "func": integrate_trapezoid.__func__,
            "order": 2,
        },
        "Метод Симпсона ": {
            "func": integrate_simpson.__func__,
            "order": 4,
        },
    }