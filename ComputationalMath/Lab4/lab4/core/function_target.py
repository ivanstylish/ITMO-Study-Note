import numpy as np

class TargetFunction:
    """Определяет исходную функцию варианта 15"""
    @staticmethod
    def calculate(x):
        return (4 * x) / (x**4 + 15)

    @classmethod
    def generate_data(cls, x_start, x_end, h):
        x_vals = np.arange(x_start, x_end + h/2, h)
        y_vals = cls.calculate(x_vals)
        return x_vals, y_vals