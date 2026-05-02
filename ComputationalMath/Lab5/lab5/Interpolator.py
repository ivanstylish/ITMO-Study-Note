from FiniteDiffTable import FiniteDiffTable
from Color import Color


class Interpolator:

    METHODS_VAR15 = [
        ("lagrange", "Лагранж"),
        ("newton_forward", "Ньютон вперёд (кон. разн.)"),
        ("newton_backward", "Ньютон назад (кон. разн.)"),
        ("gauss_forward", "Гаусс вперёд"),
        ("gauss_backward", "Гаусс назад"),
    ]

    def __init__(self, data):
        self._d = data
        self._fdt = None

    def _get_fdt(self):
        if self._fdt is None:
            self._fdt = FiniteDiffTable(self._d)
        return self._fdt

    def lagrange(self, xp):
        xi, yi, n = self._d.x, self._d.y, self._d.n
        total = 0.0
        for i in range(n):
            L = 1.0
            for j in range(n):
                if j != i:
                    denom = xi[i] - xi[j]
                    if abs(denom) < 1e-15:
                        raise ValueError(
                            f"Совпадающие узлы: x[{i}]=x[{j}]={xi[i]}"
                        )
                    L *= (xp - xi[j]) / denom
            total += L * yi[i]
        return total

    def newton_divided(self, xp):
        xi, yi, n = self._d.x, self._d.y, self._d.n
        dd = [list(yi)]
        for k in range(1, n):
            prev = dd[-1]
            row = []
            for i in range(n - k):
                denom = xi[i + k] - xi[i]
                if abs(denom) < 1e-15:
                    raise ValueError(
                        f"Совпадающие узлы xi[{i}] и xi[{i + k}]."
                    )
                row.append((prev[i + 1] - prev[i]) / denom)
            dd.append(row)
        result = dd[0][0]
        prod = 1.0
        for k in range(1, n):
            prod *= xp - xi[k - 1]
            result += dd[k][0] * prod
        return result

    def newton_forward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        t = (xp - x[0]) / h
        result = self._d.y[0]
        coeff = 1.0
        for k in range(1, n):
            coeff *= (t - (k - 1)) / k
            result += coeff * fdt.table[k][0]
        return result

    def newton_backward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        t = (xp - x[-1]) / h
        result = self._d.y[-1]
        coeff = 1.0
        for k in range(1, n):
            coeff *= (t + (k - 1)) / k
            result += coeff * fdt.table[k][n - k - 1]
        return result

    def gauss_forward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        tbl = fdt.table
        m = min(range(n), key=lambda i: abs(x[i] - xp))
        t = (xp - x[m]) / h
        result = self._d.y[m]

        coeff = 1.0
        for k in range(1, n):
            if k % 2 == 1:
                t_mult = t + (k - 1) // 2
                idx = m - (k - 1) // 2
            else:
                t_mult = t - k // 2
                idx = m - k // 2

            if 0 <= idx < len(tbl[k]):
                coeff *= t_mult / k
                result += coeff * tbl[k][idx]
            else:
                break
        return result

    def gauss_backward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        tbl = fdt.table
        m = min(range(n), key=lambda i: abs(x[i] - xp))
        t = (xp - x[m]) / h
        result = self._d.y[m]

        coeff = 1.0
        for k in range(1, n):
            if k % 2 == 1:
                t_mult = t - (k - 1) // 2
                idx = m - (k + 1) // 2
            else:
                t_mult = t + k // 2
                idx = m - k // 2

            if 0 <= idx < len(tbl[k]):
                coeff *= t_mult / k
                result += coeff * tbl[k][idx]
            else:
                break
        return result

    def compute_all(self, xp, methods=None):
        if methods is None:
            methods = self.METHODS_VAR15
        results = {}
        for key, label in methods:
            try:
                val = getattr(self, key)(xp)
                results[label] = val
            except Exception as e:
                results[label] = f"Недоступно: {e}"
        return results

    @staticmethod
    def print_results(xp, results):
        print(Color.cyan(f"\nРезультаты интерполяции для x = {xp}:"))
        print(Color.cyan("─" * 50))
        for label, val in results.items():
            if isinstance(val, float):
                print(f"  {label:<34}: {Color.green(f'{val:.6f}')}")
            else:
                print(f"  {label:<34}: {Color.yellow(val)}")