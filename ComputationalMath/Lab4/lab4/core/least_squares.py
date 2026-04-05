import numpy as np


class LeastSquaresMethod:
    """Реализация метода наименьших квадратов"""

    @staticmethod
    def solve_polynomial(x, y, degree):
        coeffs = np.polyfit(x, y, degree)
        return coeffs[::-1]  # Возвращаем от a0 до aN

    @staticmethod
    def calculate_metrics(y_true, y_pred):
        n = len(y_true)
        # Мера отклонения S
        S = np.sum((y_pred - y_true) ** 2)
        # Среднеквадратичное отклонение sigma
        sigma = np.sqrt(S / n)
        # Коэффициент детерминации R^2
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        return S, sigma, r_squared