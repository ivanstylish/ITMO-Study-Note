import math
import os

from InterpolationData import InterpolationData
from Color import Color


class Data:
    """Фабричные методы: возвращают InterpolationData из разных источников."""

    TEST_FILES = {
        "test1.txt": (
            "# Таблица 1.5 (вариант 15)\n"
            "2.10 3.7587\n2.15 4.1861\n2.20 4.9218\n"
            "2.25 5.3487\n2.30 5.9275\n2.35 6.4193\n2.40 7.0839\n"
        ),
        "test2.txt": (
            "# sin(x)\n"
            "0.0 0.0000\n0.5 0.4794\n1.0 0.8415\n"
            "1.5 0.9975\n2.0 0.9093\n2.5 0.5985\n3.0 0.1411\n"
        ),
        "test3.txt": (
            "# exp(x)/10\n"
            "1.0 0.2718\n1.2 0.3320\n1.4 0.4055\n"
            "1.6 0.4953\n1.8 0.6050\n2.0 0.7389\n"
        ),
    }

    BUILTIN_FUNCTIONS = {
        "1": ("sin(x)",        lambda v: math.sin(v)),
        "2": ("cos(x)",        lambda v: math.cos(v)),
        "3": ("exp(x)",        lambda v: math.exp(v)),
        "4": ("ln(x)  (x>0)", lambda v: math.log(v) if v > 0 else None),
        "5": ("x^3 - 2x + 1", lambda v: v ** 3 - 2 * v + 1),
    }

    @classmethod
    def from_keyboard(cls):
        n = cls._ask_int("Введите количество узлов (не менее 3): ", min_val=3)
        print(Color.cyan(f"Введите {n} пар (x y) по одной на строке:"))
        x, y = [], []
        i = 0
        while i < n:
            raw = input(f"  [{i + 1}] x y: ").split()
            if len(raw) != 2:
                print(Color.yellow("  Нужно два числа через пробел."))
                continue
            try:
                xi, yi = float(raw[0]), float(raw[1])
            except ValueError:
                print(Color.red("  Ошибка: введите два числа."))
                continue
            if xi in x:
                print(Color.yellow(f"  Узел x={xi} уже добавлен, введите другой."))
                continue
            x.append(xi)
            y.append(yi)
            i += 1
        return InterpolationData(x, y)

    @classmethod
    def from_file(cls):
        cls._ensure_test_files()
        print(Color.cyan("Тестовые файлы: " + ", ".join(cls.TEST_FILES)))
        while True:
            fname = input("Введите имя файла: ").strip()
            if not fname:
                print(Color.yellow("  Имя файла не может быть пустым."))
                continue
            if not os.path.exists(fname):
                print(Color.red(f"  Файл '{fname}' не найден."))
                continue
            x, y, errors = [], [], []
            try:
                with open(fname, encoding="utf-8") as f:
                    for lineno, line in enumerate(f, 1):
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split()
                        if len(parts) != 2:
                            errors.append(f"Строка {lineno}: ожидалось 2 числа")
                            continue
                        try:
                            xi, yi = float(parts[0]), float(parts[1])
                            if xi in x:
                                errors.append(f"Строка {lineno}: дубль x={xi}")
                            else:
                                x.append(xi)
                                y.append(yi)
                        except ValueError:
                            errors.append(f"Строка {lineno}: не распознаны числа")
            except OSError as e:
                print(Color.red(f"  Ошибка чтения файла: {e}"))
                continue
            for err in errors:
                print(Color.yellow(f"  Предупреждение: {err}"))
            try:
                data = InterpolationData(x, y)
                print(Color.green(f"  Загружено {data.n} узлов из '{fname}'."))
                return data
            except ValueError as e:
                print(Color.red(f"  Ошибка данных: {e}. Выберите другой файл."))

    @classmethod
    def from_function(cls):
        print(Color.cyan("Доступные функции:"))
        for k, (name, _) in cls.BUILTIN_FUNCTIONS.items():
            print(f"  {k}: {name}")
        while True:
            choice = input("Номер функции: ").strip()
            if choice not in cls.BUILTIN_FUNCTIONS:
                print(Color.yellow("  Нет такого номера, попробуйте ещё раз."))
                continue
            fname, func = cls.BUILTIN_FUNCTIONS[choice]
            break
        while True:
            try:
                a = float(input("Левая граница: "))
                b = float(input("Правая граница: "))
                if a >= b:
                    print(Color.yellow("  Левая граница должна быть меньше правой."))
                    continue
                break
            except ValueError:
                print(Color.red("  Ошибка: введите число."))
        n = cls._ask_int("Количество точек (не менее 3): ", min_val=3)
        xs = [a + i * (b - a) / (n - 1) for i in range(n)]
        pairs = []
        for xi in xs:
            val = func(xi)
            if val is not None and not math.isnan(val):
                pairs.append((xi, val))
            else:
                print(Color.yellow(f"  Пропуск: функция не определена в x={xi:.4f}"))
        if len(pairs) < 3:
            print(Color.red("  Слишком мало корректных точек. Выберите другой интервал."))
            return cls.from_function()
        x_out = [p[0] for p in pairs]
        y_out = [p[1] for p in pairs]
        print(Color.green(f"\n  Сгенерировано {len(x_out)} точек функции {fname}:"))
        for xi, yi in zip(x_out, y_out):
            print(f"    x={xi:.4f}  y={yi:.4f}")
        return InterpolationData(x_out, y_out)

    @staticmethod
    def demo_var15():
        x = [2.10, 2.15, 2.20, 2.25, 2.30, 2.35, 2.40]
        y = [3.7587, 4.1861, 4.9218, 5.3487, 5.9275, 6.4193, 7.0839]
        print(Color.green("\n  [Демо] Таблица 1.5, вариант 15 загружена."))
        return InterpolationData(x, y)

    # ── вспомогательные ──────────────────────────────────────────

    @classmethod
    def _ensure_test_files(cls):
        for fname, content in cls.TEST_FILES.items():
            if not os.path.exists(fname):
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)

    @staticmethod
    def _ask_int(prompt, min_val=1):
        while True:
            try:
                v = int(input(prompt))
                if v < min_val:
                    print(Color.yellow(f"  Введите число >= {min_val}."))
                    continue
                return v
            except ValueError:
                print(Color.red("  Ошибка: введите целое число."))