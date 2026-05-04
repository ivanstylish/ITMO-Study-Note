import math
from typing import Dict
from ODEEquation import ODEEquation


class EquationBank:

    def __init__(self):
        self._eqs: Dict[int, ODEEquation] = {}

    def add(self, number: int, eq: ODEEquation) -> None:
        self._eqs[number] = eq

    def get(self, number: int) -> ODEEquation:
        if number not in self._eqs:
            raise KeyError(f"Уравнение {number} не найдено в каталоге")
        return self._eqs[number]

    def all_items(self) -> list:
        return sorted(self._eqs.items())

    def count(self) -> int:
        return len(self._eqs)


def build_equation_bank() -> EquationBank:
    bank = EquationBank()

    # 1. Уравнение Бернулли: y' = y + (1+x)y^2
    #    v = 1/y → v' + v = -(1+x) → v = -x + Ce^{-x}
    #    y(1) = -1  →  C = 0  →  y = -1/x
    bank.add(1, ODEEquation(
        label="y' = y + (1+x)·y^2",
        f=lambda x, y: y + (1 + x) * y ** 2,
        exact=lambda x, x0, y0: -1.0 / x,
        exact_info="y = -1/x  (при y(1) = -1)",
        default_x0=1.0,
        default_y0=-1.0,
        default_xn=1.5,
    ))

    # 2. y' = x + y
    #    y = Ce^x - x - 1;  C = (y0 + x0 + 1)·e^{-x0}
    bank.add(2, ODEEquation(
        label="y' = x + y",
        f=lambda x, y: x + y,
        exact=lambda x, x0, y0: (y0 + x0 + 1) * math.exp(x - x0) - x - 1,
        exact_info="y = (y0+x0+1)·e^{x-x0} - x - 1",
        default_x0=0.0,
        default_y0=1.0,
        default_xn=1.0,
    ))

    # 3. y' = x^2 - y
    #    y = x^2-2x+2 + Ce^{-x};  C = (y0 - x0^2+2x0-2)·e^{x0}
    bank.add(3, ODEEquation(
        label="y' = x^2 - y",
        f=lambda x, y: x ** 2 - y,
        exact=lambda x, x0, y0: (
                x ** 2 - 2 * x + 2
                + (y0 - x0 ** 2 + 2 * x0 - 2) * math.exp(-(x - x0))
        ),
        exact_info="y = x^2-2x+2 + (y0-x0^2+2x0-2)·e^{-(x-x0)}",
        default_x0=0.0,
        default_y0=1.0,
        default_xn=2.0,
    ))

    return bank