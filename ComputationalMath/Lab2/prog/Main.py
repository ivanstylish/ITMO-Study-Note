import math

import matplotlib.pyplot as plt
import numpy as np

from Equation import equations
from SystemEquation import system_equations
from Solvers.BisectionSolver import BisectionSolver
from Solvers.ChordSolver import ChordSolver
from Solvers.NewtonSolver import NewtonSolver
from Solvers.NewtonSystemSolver import NewtonSystemSolver
from Solvers.SecantSolver import SecantSolver
from Solvers.SimpleIterationSolver import SimpleIterationSolver
from Solvers.SimpleIterationSystemSolver import SimpleIterationSystemSolver

solvers_eq = {
    1: (BisectionSolver(), "Метод половинного деления"),
    2: (ChordSolver(),     "Метод хорд"),
    3: (NewtonSolver(),    "Метод Ньютона"),
    4: (SecantSolver(),    "Метод секущих"),
    5: (SimpleIterationSolver(), "Метод простой итерации")
}

solvers_sys = {
    6: (NewtonSystemSolver(),       "Метод Ньютона для решения систем"),
    7: (SimpleIterationSystemSolver(), "Метод простой итерации для решения систем")
}


def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("\033[31mОшибка: введите число.\033[0m")


def get_int(prompt, allowed=None):
    while True:
        try:
            val = int(input(prompt))
            if allowed is None or val in allowed:
                return val
            print(f"\033[33mДопустимые значения: {allowed}\033[0m")
        except ValueError:
            print("\033[31mОшибка: введите целое число.\033[0m")


def input_file_or_keyboard():
    print("Ввод данных: 1 — клавиатура, 2 — файл")
    way = get_int("Выбор: ", [1, 2])

    if way == 1:
        a = get_float("a = ")
        while True:
            b = get_float("b = ")
            if b <= a:
                print("\033[31mОшибка: b должно быть строго больше a\033[0m")
            else:
                break
        eps = get_float("ε = ")
        return a, b, eps

    while True:
        filename = input("Введите имя файла: ").strip()
        if not filename.lower().endswith('.txt'):
            print("Ожидается файл с расширением .txt")
            continue
        try:
            with open(filename, "r", encoding="utf-8") as f:
                line = f.readline().strip()
                parts = line.split()
                if len(parts) != 3:
                    raise ValueError
                a, b, eps = map(float, parts)
                if b <= a:
                    raise ValueError("b должно быть больше a")
            print(f"Прочитано: a={a}, b={b}, ε={eps}")
            return a, b, eps
        except Exception as e:
            print("\033[31mНе удалось прочитать файл input.txt или неверный формат.\033[0m")
            print("Переход на ручной ввод...")
            return input_file_or_keyboard()


def plot_function(eq, a, b):
    x = np.linspace(a - 0.5, b + 0.5, 400)
    y = [eq.f(xi) for xi in x]
    plt.figure(figsize=(9, 6))
    plt.plot(x, y, label=eq.name)
    plt.axhline(0, color='red', linewidth=0.8, linestyle='--')
    plt.axvline(a, color='gray', linestyle=':', alpha=0.6)
    plt.axvline(b, color='gray', linestyle=':', alpha=0.6)
    plt.grid(True, alpha=0.4)
    plt.title("График функции")
    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.legend()
    plt.show()


def plot_system():
    x = np.linspace(-2, 4, 300)
    y1 = [1.5 - math.sin(xi - 1) for xi in x]
    y = np.linspace(-2, 4, 300)
    x2 = [1 + math.sin(yi + 1) for yi in y]

    plt.figure(figsize=(9, 6))
    plt.plot(x, y1, label="y = 1.5 − sin(x−1)")
    plt.plot(x2, y, label="x = 1 + sin(y+1)")
    plt.grid(True, alpha=0.4)
    plt.title("Графическое представление системы")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.axis("equal")
    plt.show()


while True:
    print("\n" + "="*70)
    print("Лабораторная работа 2. Численное решение нелинейных уравнений и систем")
    print("Вариант 15")
    print("="*70)
    print("  1  —  Решение нелинейного уравнения")
    print("  2  —  Решение системы нелинейных уравнений")
    print("  0  —  Выход")
    print("-"*70)

    mode = get_int("Выберите режим: ", [0,1,2])

    if mode == 0:
        print("\nВы действительно хотите выйти из программы?")
        print("  1 — Да, выйти")
        print("  2 — Нет, остаться")

        confirm = get_int("Ваш выбор: ", [1, 2])

        if confirm == 1:
            print("\nПрограмма завершена.")
            print(" /\_/\ ")
            break
        else:
            print("Возвращаемся в главное меню...\n")
            continue

    if mode == 1:
        print("\nДоступные уравнения:")
        for i, eq in enumerate(equations, 1):
            print(f"  {i} - {eq.name}")

        eq_choice = get_int("Выберите уравнение (1-3): ", [1,2,3])
        selected_eq = equations[eq_choice - 1]
        print("\033[33mДоступные методы:\033[0m")
        for k, (_, name) in solvers_eq.items():
            print(f"  {k:2d}  —  {name}")

        m = get_int("Выберите метод: ", list(solvers_eq.keys()))
        solver, method_name = solvers_eq[m]

        print(f"\nВыбран метод: {method_name}")
        a, b, eps = input_file_or_keyboard()

        ok, msg = solver.verify(eq, a, b)
        if not ok:
            print(f"\033[31m\nОшибка:{msg}\033[0m")
            print("Вернитесь и выберите другой интервал.\n")
            continue

        if m == 5:
            x_vals = np.linspace(a, b, 200)
            max_der = max(abs(eq.dphi(xv)) for xv in x_vals)
            print(f"max |φ'(x)| на [{a:.4f}, {b:.4f}] ≈ {max_der:.4f}")
            if max_der >= 1:
                print("Условие сходимости НЕ выполнено (|φ'| >= 1)")
                print("Метод может не сойтись. Продолжить? (1 — да, 0 — нет)")
                if get_int("-> ", [0,1]) == 0:
                    continue

        print("\nПостроение графика...")
        plot_function(eq, a, b)

        root, n_iter, table = solver.solve(eq, a, b, eps)

        if root is None:
            print("Не удалось найти корень.")
            continue

        print("\n" + "═"*70)
        print(f"Результат метода {method_name}")
        print(f"Корень:          x = {root:.6f}")
        print(f"Значение функции: f(x) = {eq.f(root):.2e}")
        print(f"Количество итераций: {n_iter}")
        print("═"*70)

        if table:
            print("\nТаблица итерационного процесса:")
            if m == 1:
                print(" № |    a    |    b    |    x    |  f(a)  |  f(b)  |  f(x)  | |x_{k+1}-x_{k}|")
                print("-"*78)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:7.3f} | {row[2]:7.3f} | {row[3]:7.3f} | "
                          f"{row[4]:6.3f} | {row[5]:6.3f} | {row[6]:6.3f} | {row[7]:5.3f}")

            elif m == 2:
                print(" № |    a    |    b    |    x    |  f(a)  |  f(b)  |  f(x)  | |b-a|")
                print("-"*78)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:7.3f} | {row[2]:7.3f} | {row[3]:7.3f} | "
                          f"{row[4]:6.3f} | {row[5]:6.3f} | {row[6]:6.3f} | {row[7]:5.3f}")

            elif m == 3:
                print(" № |   x_k   |  f(x_k) | f'(x_k) | x_{k+1} | |x_{k+1}-x_{k}|  ")
                print("-"*60)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:8.4f} | {row[2]:8.3e} | {row[3]:8.3e} | "
                          f"{row[4]:8.3f} | {row[5]:6.3e}")

            elif m == 4:
                print(" № |    x_{k-1}    |    x_k    |    x_{k+1}    |  f(x_{k+1})  |  |x_{k+1}-x_{k}|  |")
                print("-"*78)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:7.3f} | {row[2]:7.3f} | {row[3]:7.3f} | "
                          f"{row[4]:6.3f} | {row[5]:6.3f} |")

            elif m == 5:
                print(" № |   x_k   |  x_{k+1} |   f(x_{k+1})   |  |x_{k+1}-x_{k}|  ")
                print("-"*55)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:8.3f} | {row[2]:8.3f} | {row[3]:9.3e} | {row[4]:7.3e}")

        print("\n")

    elif mode == 2:
        print("\nДоступные системы уравнений:")
        for i, sys_eq in enumerate(system_equations, 1):
            print(f"  {i} - {sys_eq.name}")

        sys_choice = get_int("Выберите систему (1-3): ", [1,2,3])
        selected_sys = system_equations[sys_choice - 1]
        print(sys_eq.name)
        print("\033[33m\nДоступные методы:\033[0m")
        for k, (_, name) in solvers_sys.items():
            print(f"  {k:2d}  —  {name}")

        m = get_int("Выберите метод: ", list(solvers_sys.keys()))
        solver, method_name = solvers_sys[m]

        print(f"\nВыбран метод: {method_name}")

        x0 = get_float("x₀ = ")
        y0 = get_float("y₀ = ")
        eps = get_float("ε = ")

        print("\nПостроение графика...")
        plot_system()

        sol, n_iter, table = solver.solve(sys_eq, x0, y0, eps)

        if sol is None:
            print("Не удалось найти решение системы.")
            if table and table[0][0].startswith("Ошибка"):
                print("Сообщение:", table[0][0])
            continue

        x, y = sol
        print("\n" + "═"*70)
        print(f"Результат метода {method_name}")
        print(f"  x = {x:.6f}")
        print(f"  y = {y:.6f}")
        print(f"Количество итераций: {n_iter}")
        print("═"*70)

        f1, f2 = sys_eq.f_sys(sol)
        print(f"Проверка остатков:")
        print(f"  f₁ = {f1:12.3e}")
        print(f"  f₂ = {f2:12.3e}")

        if table:
            print("\nТаблица итераций:")
            if m == 6:
                print(" № |    x     |    y     |    f1     |    f2     |  max|Δ|  ")
                print("-"*70)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:9.5f} | {row[2]:9.5f} | {row[3]:10.3e} | {row[4]:10.3e} | {row[5]:8.3e}")
            else:
                print(" № |    x     |    y     |   x_new   |   y_new   |  max|Δ|  ")
                print("-"*70)
                for row in table:
                    print(f"{row[0]:2} | {row[1]:9.5f} | {row[2]:9.5f} | {row[3]:9.5f} | {row[4]:9.5f} | {row[5]:8.3e}")

        print("\n")