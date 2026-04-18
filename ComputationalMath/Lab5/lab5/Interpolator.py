# =====================================================================
#  3. Interpolator — все методы интерполяции
# =====================================================================
from FiniteDiffTable import FiniteDiffTable
from Color import Color


class Interpolator:
    """Вычисляет значение функции в точке xp по данным InterpolationData."""

    METHODS_VAR15 = [
        ("lagrange",       "Лагранж"),
        ("newton_divided", "Ньютон (разд. разн.)"),
        ("newton_forward", "Ньютон вперёд (кон. разн.)"),
    ]

    def __init__(self, data):
        self._d = data
        self._fdt = None  # создаётся лениво

    def _get_fdt(self):
        if self._fdt is None:
            self._fdt = FiniteDiffTable(self._d)
        return self._fdt

    # ── 3.1 Лагранж ──────────────────────────────────────────────
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

    # ── 3.2 Ньютон с разделёнными разностями ─────────────────────
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

    # ── 3.3 Ньютон вперёд ────────────────────────────────────────
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

    # ── 3.4 Ньютон назад ─────────────────────────────────────────
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

    # ── 3.5 Гаусс вперёд ─────────────────────────────────────────
    def gauss_forward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        tbl = fdt.table
        m = min(range(n), key=lambda i: abs(x[i] - xp))
        t = (xp - x[m]) / h
        result = self._d.y[m]
        if m < len(tbl[1]):
            result += t * tbl[1][m]
        if 0 <= m - 1 < len(tbl[2]):
            result += t * (t - 1) / 2 * tbl[2][m - 1]
        if 0 <= m - 1 < len(tbl[3]):
            result += (t + 1) * t * (t - 1) / 6 * tbl[3][m - 1]
        if 0 <= m - 2 < len(tbl[4]):
            result += (t + 2) * (t + 1) * t * (t - 1) / 24 * tbl[4][m - 2]
        if 0 <= m - 2 < len(tbl[5]):
            result += (t + 2) * (t + 1) * t * (t - 1) * (t - 2) / 120 * tbl[5][m - 2]
        return result

    # ── 3.6 Гаусс назад ──────────────────────────────────────────
    def gauss_backward(self, xp):
        if not self._d.is_uniform:
            raise ValueError("Требуется равномерный шаг.")
        fdt = self._get_fdt()
        x, h, n = self._d.x, self._d.h, self._d.n
        tbl = fdt.table
        m = min(range(n), key=lambda i: abs(x[i] - xp))
        t = (xp - x[m]) / h
        result = self._d.y[m]
        if 0 <= m - 1 < len(tbl[1]):
            result += t * tbl[1][m - 1]
        if 0 <= m - 1 < len(tbl[2]):
            result += t * (t + 1) / 2 * tbl[2][m - 1]
        if 0 <= m - 1 < len(tbl[3]):
            result += (t + 1) * t * (t - 1) / 6 * tbl[3][m - 1]
        if 0 <= m - 2 < len(tbl[4]):
            result += (t + 1) * t * (t - 1) * (t - 2) / 24 * tbl[4][m - 2]
        return result

    # ── общий расчёт и вывод ──────────────────────────────────────
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
                # числовой результат — зелёный
                print(f"  {label:<34}: {Color.green(f'{val:.6f}')}")
            else:
                # «Недоступно: ...» — жёлтый (предупреждение, не крэш)
                print(f"  {label:<34}: {Color.yellow(val)}")