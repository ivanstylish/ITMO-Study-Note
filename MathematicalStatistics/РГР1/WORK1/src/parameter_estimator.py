import numpy as np
from scipy import stats


class ParameterEstimator:

    @staticmethod
    def estimate_exponential(data: np.ndarray) -> dict:
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        c_mom = mean - std
        lam_mom = 1 / std
        c_mle = np.min(data)
        lam_mle = 1 / (mean - c_mle)

        return {
            'method_moments': {'c': c_mom, 'λ': lam_mom},
            'mle': {'c': c_mle, 'λ': lam_mle}
        }

    @staticmethod
    def estimate_uniform(data: np.ndarray) -> dict:
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        a_mom = mean - np.sqrt(3) * std
        b_mom = mean + np.sqrt(3) * std
        a_mle = np.min(data)
        b_mle = np.max(data)

        return {
            'method_moments': {'a': a_mom, 'b': b_mom},
            'mle': {'a': a_mle, 'b': b_mle}
        }

    @staticmethod
    def estimate_normal(data: np.ndarray) -> dict:
        mu = np.mean(data)
        var_biased = np.var(data, ddof=0)
        var_unbiased = np.var(data, ddof=1)
        return {
            'mu': mu,
            'sigma2_biased': var_biased,
            'sigma2_unbiased': var_unbiased
        }