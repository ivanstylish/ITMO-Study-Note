# =====================================================================
#  1. InterpolationData — хранение и валидация таблицы узлов
# =====================================================================

class InterpolationData:
    """Хранит отсортированную таблицу (x, y) и проверяет её корректность."""

    MIN_NODES = 3

    def __init__(self, x, y):
        if len(x) != len(y):
            raise ValueError("Длины x и y должны совпадать.")
        if len(x) < self.MIN_NODES:
            raise ValueError(
                f"Нужно не менее {self.MIN_NODES} узлов, получено {len(x)}."
            )
        pairs = sorted(zip(x, y), key=lambda p: p[0])
        self.x = [p[0] for p in pairs]
        self.y = [p[1] for p in pairs]
        self._check_unique()

    def _check_unique(self):
        for i in range(len(self.x) - 1):
            if abs(self.x[i + 1] - self.x[i]) < 1e-15:
                raise ValueError(f"Дублирующийся узел x = {self.x[i]}.")

    @property
    def n(self):
        return len(self.x)

    @property
    def h(self):
        """Шаг первого интервала (для равномерных сеток)."""
        return self.x[1] - self.x[0]

    @property
    def is_uniform(self):
        h0 = self.h
        return all(
            abs((self.x[i + 1] - self.x[i]) - h0) < 1e-9
            for i in range(self.n - 1)
        )

