# src/confidence_intervals.py
import numpy as np
from scipy import stats


class ConfidenceIntervals:

    def __init__(self, confidence_level: float = 0.95):
        self.alpha = 1 - confidence_level
        self.z = stats.norm.ppf(1 - self.alpha / 2)

    def asymptotic_ci_mean(self, data: np.ndarray) -> tuple:
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        se = std / np.sqrt(len(data))
        lower = mean - self.z * se
        upper = mean + self.z * se
        return (lower, upper)

    def exact_normal_ci(self, data: np.ndarray) -> dict:
        n = len(data)
        mean = np.mean(data)
        var_unb = np.var(data, ddof=1)
        std_unb = np.sqrt(var_unb)
        se = std_unb / np.sqrt(n)

        t = stats.t.ppf(1 - self.alpha / 2, df=n - 1)
        ci_mu = (mean - t * se, mean + t * se)

        chi2_low = stats.chi2.ppf(self.alpha / 2, df=n - 1)
        chi2_high = stats.chi2.ppf(1 - self.alpha / 2, df=n - 1)
        ci_sigma2 = ((n - 1) * var_unb / chi2_high, (n - 1) * var_unb / chi2_low)

        return {'mu': ci_mu, 'sigma2': ci_sigma2}