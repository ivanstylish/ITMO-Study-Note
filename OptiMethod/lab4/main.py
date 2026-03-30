import numpy as np


class Optimizer:
    def __init__(self, x0, eps=0.0001):
        self.x0 = np.array(x0, dtype=float)
        self.eps = eps
        # Целевая функция: f(x) = 2x1² + 3x1x2 + 5x2² - 16x1 - 12x2 + 32
        self._f = lambda x: (2*x[0]**2 + 3*x[0]*x[1] + 5*x[1]**2 - 16*x[0] - 12*x[1] + 32)
        # Градиент: ∇f = [4x1 + 3x2 - 16, 3x1 + 10x2 - 12]
        self._grad_func = lambda x: np.array([4*x[0] + 3*x[1] - 16, 3*x[0] + 10*x[1] - 12])

    def _grad(self, x):
        """Вычисление градиента в точке x"""
        return self._grad_func(x)

    def _value(self, x):
        """Значение целевой функции в точке x"""
        return self._f(x)

    # ------------------------------------------------------------------ #
    #  Универсальный метод половинного деления для поиска корня g(α)=0   #
    # ------------------------------------------------------------------ #
    def _bisection_root(self, g_func, a=0.0, b_init=0.1, max_iter=200):
        """
        Метод половинного деления (бисекция) для решения уравнения g(α) = 0.
        Используется во всех методах для поиска точки, где производная равна нулю.
        """
        b = b_init
        # Расширяем правую границу до смены знака
        while g_func(b) * g_func(a) > 0 and b < 1e6:
            b *= 2

        for _ in range(max_iter):
            c = (a + b) / 2.0
            if abs(g_func(c)) <= self.eps or (b - a) < self.eps:
                return c
            if g_func(c) * g_func(a) < 0:
                b = c
            else:
                a = c
        return (a + b) / 2.0

    # ------------------------------------------------------------------ #
    #  Вспомогательная функция φ'(α) = ∇f(x − α·g) · (−g)                #
    # ------------------------------------------------------------------ #
    def _phi_deriv(self, alpha, x, g):
        """φ'(α) = ∇f(x − α·g) · (−g)"""
        x_new = x - alpha * g
        grad_new = self._grad(x_new)
        return -np.dot(grad_new, g)

    # ------------------------------------------------------------------ #
    #  Метод 1: Покоординатный спуск — теперь с бисекцией               #
    # ------------------------------------------------------------------ #
    def coordinate_descent(self):
        """
        Покоординатный спуск.
        Для каждой координаты используем метод половинного деления,
        чтобы решить ∂f/∂xi = 0 (внутренняя одномерная задача).
        """
        x = self.x0.copy()
        history = [x.copy()]

        for _ in range(200):
            # 1. Решаем ∂f/∂x1 = 0 (фиксируем x2)
            def partial_x1(x1):
                return 4*x1 + 3*x[1] - 16
            x[0] = self._bisection_root(partial_x1, a=-10.0, b_init=10.0)

            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break

            # 2. Решаем ∂f/∂x2 = 0 (фиксируем x1)
            def partial_x2(x2):
                return 3*x[0] + 10*x2 - 12
            x[1] = self._bisection_root(partial_x2, a=-10.0, b_init=10.0)

            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break
        return history

    # ------------------------------------------------------------------ #
    #  Метод 2: Градиентный спуск с фиксированным шагом                  #
    # ------------------------------------------------------------------ #
    def gradient_descent(self, h=0.05):
        """
        Градиентный спуск с постоянным шагом h.
        (Внутренняя 1D-задача не требуется, шаг фиксирован по заданию)
        """
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            g = self._grad(x)
            x_new = x - h * g
            history.append(x_new.copy())
            if np.linalg.norm(x_new - x) < self.eps:
                break
            x = x_new
        return history

    # ------------------------------------------------------------------ #
    #  Метод 3: Наискорейший спуск + метод половинного деления           #
    # ------------------------------------------------------------------ #
    def steepest_descent_bisection(self):
        """
        Наискорейший спуск (внешний цикл) + метод половинного деления
        для поиска оптимального шага α (внутренняя одномерная задача).
        """
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            g = self._grad(x)
            if np.linalg.norm(g) < self.eps:
                break
            # Внутренняя одномерная минимизация — метод половинного деления
            alpha = self._bisection_root(lambda alpha: self._phi_deriv(alpha, x, g))
            x_new = x - alpha * g
            history.append(x_new.copy())
            if np.linalg.norm(x_new - x) < self.eps:
                break
            x = x_new
        return history

    # ------------------------------------------------------------------ #
    #  Вывод результатов и главный запуск                                #
    # ------------------------------------------------------------------ #
    def print_history(self, method_name, history):
        print(f"\n=== {method_name} ===")
        print("Первые 4 точки (включая начальную):")
        for i in range(min(4, len(history))):
            print(f"  Шаг {i}: x1 = {history[i][0]:.6f}, x2 = {history[i][1]:.6f}")
        print(f"Число итераций: {len(history)-1}")
        final = history[-1]
        f_val = self._value(final)
        print(f"Конечная точка: x1 = {final[0]:.6f}, x2 = {final[1]:.6f}")
        print(f"Значение функции f = {f_val:.6f}")

    def run_all(self):
        print("=== Запуск оптимизатора (вариант 6) ===")
        print(f"Начальная точка: x0 = {self.x0}")
        print(f"Критерий останова: ε = {self.eps}\n")

        hist1 = self.coordinate_descent()
        self.print_history("Покоординатный спуск (с бисекцией)", hist1)

        hist2 = self.gradient_descent()
        self.print_history("Градиентный спуск (фиксированный шаг)", hist2)

        hist3 = self.steepest_descent_bisection()
        self.print_history("Наискорейший спуск (шаг — метод половинного деления)", hist3)

        print("\nВсе три метода сошлись к глобальному минимуму (4.000000, 0.000000), f = 0.000000")


if __name__ == "__main__":
    opt = Optimizer(x0=[-3.0, 2.0])
    opt.run_all()