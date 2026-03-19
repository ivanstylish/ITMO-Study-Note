from typing import Optional
from Methods import FuncType, Methods


class Integrator:

    INITIAL_N: int = 4
    MAX_N: int = 1_000_000

    @classmethod
    def compute(
            cls,
            func_entry: dict,
            method_entry: dict,
            a: float,
            b: float,
            eps: float,
    ) -> tuple[float, int]:

        convergent: Optional[bool] = func_entry["convergent"](a, b)
        if convergent is False:
            raise ValueError("\033[33mИнтеграл не существует: интеграл расходится.\033[0m")
        if func_entry["discontinuity"](a, b) and convergent is None:
            raise ValueError("\033[33mИнтеграл не существует: функция имеет разрыв.\033[0m")

        func = func_entry["func"]
        method = method_entry["func"]
        p = method_entry["order"]
        denom = 2 ** p - 1

        n = cls.INITIAL_N
        i_n = cls._safe_call(method, func, a, b, n)

        while n <= cls.MAX_N:
            n2 = n * 2
            i_2n = cls._safe_call(method, func, a, b, n2)
            if abs(i_2n - i_n) / denom <= eps:
                return i_2n, n2
            i_n = i_2n
            n = n2

        raise RuntimeError(f"\033[31mНе удалось достичь точности {eps} при n = {cls.MAX_N}.\033[0m")

    @staticmethod
    def _safe_call(method, func: FuncType, a: float, b: float, n: int) -> float:
        try:
            return method(func, a, b, n)
        except (ValueError, ZeroDivisionError) as e:
            raise ValueError(f"\033[31mОшибка вычисления: {e}\033[0m") from e
