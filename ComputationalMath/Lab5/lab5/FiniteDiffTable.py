class FiniteDiffTable:

    def __init__(self, data):
        if not data.is_uniform:
            raise ValueError(
                "Таблица конечных разностей требует равномерного шага."
            )
        self._data = data
        self.table = self._build(data.y)

    @staticmethod
    def _build(y):
        table = [list(y)]
        while len(table[-1]) > 1:
            prev = table[-1]
            table.append([prev[i + 1] - prev[i] for i in range(len(prev) - 1)])
        return table

    def get(self, order, index):
        if order >= len(self.table) or index >= len(self.table[order]):
            raise IndexError(
                f"Δ^{order}y[{index}] выходит за границы таблицы."
            )
        return self.table[order][index]

    def print(self):
        x, n = self._data.x, self._data.n
        col = 11
        header = f"{'x':>8} {'y':>10}"
        for k in range(1, n):
            header += f"  {('Δ^' + str(k) + 'y'):>{col}}"
        print(header)
        print("─" * len(header))
        for i in range(n):
            row = f"{x[i]:8.4f} {self.table[0][i]:10.4f}"
            for k in range(1, n):
                if i < len(self.table[k]):
                    row += f"  {self.table[k][i]:>{col}.4f}"
                else:
                    row += f"  {'':>{col}}"
            print(row)
