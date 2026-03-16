import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
import os


class Visualizer:

    def __init__(self, output_dir: str = "plots"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style("whitegrid")

    def save_histogram(self, data: np.ndarray, col_name: str, bins='fd'):
        plt.figure(figsize=(8, 5))
        sns.histplot(data, bins=bins, stat='density', color='teal', alpha=0.7)
        plt.title(f"Гистограмма — {col_name} (bins={bins})")
        plt.xlabel("Значение")
        plt.ylabel("Плотность")
        path = os.path.join(self.output_dir, f"hist_{col_name}_{bins}.png")
        plt.savefig(path, dpi=140, bbox_inches='tight')
        plt.close()
        return path

    def save_ecdf(self, data: np.ndarray, col_name: str):
        x = np.sort(data)
        y = np.arange(1, len(x) + 1) / len(x)
        plt.figure(figsize=(7, 4.5))
        plt.step(x, y, where='post', color='darkblue')
        plt.title(f"Эмпирическая ФР — {col_name}")
        plt.xlabel("x")
        plt.ylabel("Fₙ(x)")
        path = os.path.join(self.output_dir, f"ecdf_{col_name}.png")
        plt.savefig(path, dpi=140, bbox_inches='tight')
        plt.close()
        return path

    def save_qqplot(self, data: np.ndarray, col_name: str):
        plt.figure(figsize=(6, 6))
        stats.probplot(data, dist="norm", plot=plt)
        plt.title(f"QQ-график — {col_name}")
        path = os.path.join(self.output_dir, f"qq_{col_name}.png")
        plt.savefig(path, dpi=140, bbox_inches='tight')
        plt.close()
        return path