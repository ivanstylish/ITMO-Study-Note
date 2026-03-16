import numpy as np
from scipy import stats


class DescriptiveStats:

    def __init__(self, data: np.ndarray):
        self.data = data
        self.n = len(data)

    def compute_all(self) -> dict:
        mean = np.mean(self.data)
        median = np.median(self.data)
        var_biased = np.var(self.data, ddof=0)
        var_unbiased = np.var(self.data, ddof=1)
        std_biased = np.std(self.data, ddof=0)
        std_unbiased = np.std(self.data, ddof=1)
        skew = stats.skew(self.data)
        kurt = stats.kurtosis(self.data)
        min_val = np.min(self.data)
        max_val = np.max(self.data)
        q25, q75 = np.percentile(self.data, [25, 75])

        return {
            'n': self.n,
            'mean': mean,
            'median': median,
            'var_biased': var_biased,
            'var_unbiased': var_unbiased,
            'std_biased': std_biased,
            'std_unbiased': std_unbiased,
            'skewness': skew,
            'kurtosis': kurt,
            'min': min_val,
            'max': max_val,
            'q25': q25,
            'q75': q75,
            'iqr': q75 - q25
        }

    def describe_distribution(self, stats_dict: dict) -> str:
        skew = stats_dict['skewness']
        kurt = stats_dict['kurtosis']
        if abs(skew) < 0.2 and abs(kurt) < 0.5:
            return "симметричное, близко к нормальному"
        elif skew > 1.0:
            return "сильная положительная асимметрия, тяжёлый правый хвост"
        elif skew < -1.0:
            return "сильная отрицательная асимметрия"
        else:
            return "лёгкая асимметрия"