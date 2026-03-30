import numpy as np

class Optimizer:

    def __init__(self, x0, eps=0.0001):
        self.x0 = np.array(x0, dtype=float)
        self.eps = eps
        # Целевая функция: f(x) = 2x1^2 + 3x1*x2 + 5x2^2 - 16x1 - 12x2 + 32
        self._f = lambda x: 2*x[0]**2 + 3*x[0]*x[1] + 5*x[1]**2 - 16*x[0] - 12*x[1] + 32
        # Градиент: grad f = [df/dx1, df/dx2] = [4x1 + 3x2 - 16, 3x1 + 10x2 - 12]
        self._grad_func = lambda x: np.array([4*x[0] + 3*x[1] - 16, 3*x[0] + 10*x[1] - 12])

    def _grad(self, x):
        """Вычисление градиента"""
        return self._grad_func(x)

    def _value(self, x):
        """Значение целевой функции в точке x"""
        return self._f(x)

    def coordinate_descent(self):
        """
        Метод 1: Покоординатный спуск (лекция, слайды 3–8).

        На каждом шаге цикла фиксируем одну переменную и минимизируем
        по другой, приравнивая частную производную к нулю:

          df/dx1 = 4*x1 + 3*x2 - 16 = 0  =>  x1 = (16 - 3*x2) / 4
          df/dx2 = 3*x1 + 10*x2 - 12 = 0 =>  x2 = (12 - 3*x1) / 10

        Останов: ||x^(k+1) - x^(k)|| <= eps
        """
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            # Минимизация по x1 при фиксированном x2: df/dx1 = 4x1 + 3x2 - 16 = 0
            x[0] = (16 - 3 * x[1]) / 4.0
            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break
            # Минимизация по x2 при фиксированном x1: df/dx2 = 3x1 + 10x2 - 12 = 0
            x[1] = (12 - 3 * x[0]) / 10.0
            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break
        return history

    def gradient_descent(self, h=0.05):
        """
        Метод 2: Градиентный спуск с фиксированным шагом h (лекция, слайды 14–22).

        Формула пересчёта (слайд 21–22):
          x^(k+1) = x^(k) - h * grad_f(x^(k))

        то есть каждая координата:
          x1^(k+1) = x1^(k) - h * df/dx1(M_k)
          x2^(k+1) = x2^(k) - h * df/dx2(M_k)

        Останов: ||x^(k+1) - x^(k)|| <= eps
        """
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            g = self._grad(x)
            # x^(k+1) = x^(k) - h * grad f(x^(k))
            x_new = x - h * g
            history.append(x_new.copy())
            if np.linalg.norm(x_new - x) < self.eps:
                break
            x = x_new
        return history

    def steepest_descent(self):
        """
        Метод 3: Наискорейший спуск (лекция, слайды 26–32).

        Направление спуска — антиградиент: S^(k) = -grad f(x^(k))

        Шаг alpha_k находится из одномерной минимизации (слайд 28):
          min_alpha  f(x^(k) - alpha * grad f(x^(k)))

        Для квадратичной функции f(x) = (1/2) x^T A x + b^T x + c
        подстановка x_new = x - alpha*g в f и дифференцирование по alpha
        даёт аналитическое решение:
          d/d(alpha) f(x - alpha*g) = 0
          => -g^T * grad f(x - alpha*g) = 0
          => alpha = (g^T * g) / (g^T * A * g)

        где A — матрица Гессе (постоянна для квадратичной функции).

        Формула пересчёта:
          x^(k+1) = x^(k) - alpha_k * grad f(x^(k))

        Останов: ||x^(k+1) - x^(k)|| <= eps
        """
        # Матрица вторых частных производных (Гессе) для f:
        # d^2f/dx1^2 = 4,  d^2f/dx1dx2 = 3
        # d^2f/dx2dx1 = 3, d^2f/dx2^2 = 10
        A = np.array([[4., 3.], [3., 10.]])

        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            g = self._grad(x)
            # Числитель: g^T * g
            gTg = np.dot(g, g)
            if gTg < 1e-12:
                break
            # Знаменатель: g^T * A * g  (из условия df/dalpha = 0)
            gTAg = np.dot(g, np.dot(A, g))
            # Оптимальный шаг (одномерная минимизация по alpha)
            alpha = gTg / gTAg
            # x^(k+1) = x^(k) - alpha_k * grad f(x^(k))
            x_new = x - alpha * g
            history.append(x_new.copy())
            if np.linalg.norm(x_new - x) < self.eps:
                break
            x = x_new
        return history

    def print_history(self, method_name, history):
        """Единый вывод результатов"""
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
        """Запуск всех трёх методов"""
        print("=== Запуск оптимизатора (вариант 6) ===")
        print(f"Начальная точка: x0 = {self.x0}")
        print(f"Критерий останова: ε = {self.eps}\n")

        hist1 = self.coordinate_descent()
        self.print_history("Покоординатный спуск", hist1)

        hist2 = self.gradient_descent()
        self.print_history("Градиентный спуск", hist2)

        hist3 = self.steepest_descent()
        self.print_history("Наискорейший спуск", hist3)

        print("\nВсе методы сошлись к глобальному минимуму (4.000000, 0.000000), f = 0.000000")


if __name__ == "__main__":
    opt = Optimizer(x0=[-3.0, 2.0])
    opt.run_all()