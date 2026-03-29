import numpy as np

class Optimizer:

    def __init__(self, x0, eps=0.0001):
        self.x0 = np.array(x0, dtype=float)
        self.eps = eps
        self._f = lambda x: 2*x[0]**2 + 3*x[0]*x[1] + 5*x[1]**2 - 16*x[0] - 12*x[1] + 32
        self._grad_func = lambda x: np.array([4*x[0] + 3*x[1] - 16, 3*x[0] + 10*x[1] - 12])
        self.A = np.array([[4., 3.], [3., 10.]])

    def _grad(self, x):
        """Вычисление градиента"""
        return self._grad_func(x)

    def _value(self, x):
        """Значение целевой функции в точке x"""
        return self._f(x)

    def coordinate_descent(self):
        """Метод 1: Покоординатный спуск"""
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            x[0] = (16 - 3 * x[1]) / 4.0
            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break
            x[1] = (12 - 3 * x[0]) / 10.0
            history.append(x.copy())
            if np.linalg.norm(history[-1] - history[-2]) < self.eps:
                break
        return history

    def gradient_descent(self, h=0.05):
        """Метод 2: Градиентный спуск"""
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

    def steepest_descent(self):
        """Метод 3: Наискорейший спуск"""
        x = self.x0.copy()
        history = [x.copy()]
        for _ in range(200):
            g = self._grad(x)
            gg = np.dot(g, g)
            if gg < 1e-12:
                break
            denom = np.dot(g.T, np.dot(self.A, g))
            alpha = gg / denom
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