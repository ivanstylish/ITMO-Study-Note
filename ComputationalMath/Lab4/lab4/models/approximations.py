import numpy as np
from core.least_squares import LeastSquaresMethod


class BaseApproximation:
    def __init__(self, name):
        self.name = name
        self.coeffs = []
        self.S = 0
        self.sigma = 0
        self.r_squared = 0

    def fit(self, x, y):
        raise NotImplementedError

    def predict(self, x):
        raise NotImplementedError

    def r_squared_message(self):
        r2 = self.r_squared
        if r2 >= 0.95:
            return f"R^2 = {r2:.5f} — высокая точность аппроксимации"
        elif r2 >= 0.75:
            return f"R^2 = {r2:.5f} — удовлетворительная точность аппроксимации"
        elif r2 >= 0.50:
            return f"R^2 = {r2:.5f} — слабая точность аппроксимации"
        else:
            return f"R^2 = {r2:.5f} — недостаточная точность аппроксимации"


class LinearApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Линейная функция")

    def fit(self, x, y):
        self.coeffs = LeastSquaresMethod.solve_polynomial(x, y, 1)
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)
        self.pearson_r = np.corrcoef(x, y)[0, 1]

    def predict(self, x):
        return self.coeffs[0] + self.coeffs[1] * x

    def formula(self):
        return f"f(x) = a + b * xi"

    def print_coeffs(self):
        a, b = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}]"


class QuadraticApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Полиноминальная 2-й степени функция")

    def fit(self, x, y):
        self.coeffs = LeastSquaresMethod.solve_polynomial(x, y, 2)
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)

    def predict(self, x):
        return self.coeffs[0] + self.coeffs[1] * x + self.coeffs[2] * x ** 2

    def formula(self):
        return f"f(x) = a + b * xi + c * xi ** 2"

    def print_coeffs(self):
        a, b, c = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}, {round(c, 4)}]"


class CubicApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Полиноминальная 3-й степени функция")

    def fit(self, x, y):
        self.coeffs = LeastSquaresMethod.solve_polynomial(x, y, 3)
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)

    def predict(self, x):
        return self.coeffs[0] + self.coeffs[1] * x + self.coeffs[2] * x ** 2 + self.coeffs[3] * x ** 3

    def formula(self):
        return f"f(x) = a + b * xi + c * xi ** 2 + d * xi ** 3"

    def print_coeffs(self):
        a, b, c, d = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}, {round(c, 4)}, {round(d, 4)}]"


class ExponentialApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Экспоненциальная функция")
        self.valid = True

    def fit(self, x, y):
        if np.any(y <= 0):
            self.valid = False
            self.S = float('inf')
            self.sigma = float('inf')
            self.r_squared = -float('inf')
            return
        ln_y = np.log(y)
        coeffs_lin = LeastSquaresMethod.solve_polynomial(x, ln_y, 1)
        self.b_coeff = coeffs_lin[1]
        self.a_coeff = np.exp(coeffs_lin[0])
        self.coeffs = [self.a_coeff, self.b_coeff]
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)

    def predict(self, x):
        return self.a_coeff * np.exp(self.b_coeff * x)

    def formula(self):
        return "f(x) = a * exp(b * xi)"

    def print_coeffs(self):
        a, b = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}]"


class LogarithmicApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Логарифмическая функция")
        self.valid = True

    def fit(self, x, y):
        if np.any(x <= 0):
            self.valid = False
            self.S = float('inf')
            self.sigma = float('inf')
            self.r_squared = -float('inf')
            return
        ln_x = np.log(x)
        coeffs_lin = LeastSquaresMethod.solve_polynomial(ln_x, y, 1)
        self.a_coeff = coeffs_lin[0]
        self.b_coeff = coeffs_lin[1]
        self.coeffs = [self.a_coeff, self.b_coeff]
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)

    def predict(self, x):
        return self.a_coeff + self.b_coeff * np.log(x)

    def formula(self):
        return "f(x) = a + b * log(xi)"

    def print_coeffs(self):
        a, b = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}]"


class PowerApproximation(BaseApproximation):
    def __init__(self):
        super().__init__("Степенная функция")
        self.valid = True

    def fit(self, x, y):
        if np.any(x <= 0) or np.any(y <= 0):
            self.valid = False
            self.S = float('inf')
            self.sigma = float('inf')
            self.r_squared = -float('inf')
            return
        ln_x = np.log(x)
        ln_y = np.log(y)
        coeffs_lin = LeastSquaresMethod.solve_polynomial(ln_x, ln_y, 1)
        self.b_coeff = coeffs_lin[1]
        self.a_coeff = np.exp(coeffs_lin[0])
        self.coeffs = [self.a_coeff, self.b_coeff]
        y_pred = self.predict(x)
        self.S, self.sigma, self.r_squared = LeastSquaresMethod.calculate_metrics(y, y_pred)

    def predict(self, x):
        return self.a_coeff * (x ** self.b_coeff)

    def formula(self):
        return "f(x) = a * xi ** b"

    def print_coeffs(self):
        a, b = self.coeffs
        return f"[{round(a, 4)}, {round(b, 4)}]"