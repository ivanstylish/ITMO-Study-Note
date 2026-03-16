# src/runner.py
from data_loader import DataLoader
from descriptive_stats import DescriptiveStats
from visualizer import Visualizer
from parameter_estimator import ParameterEstimator
from confidence_intervals import ConfidenceIntervals


def main():
    loader = DataLoader("../data/RGR1_A-12_X1-X4.csv")
    df = loader.load()
    if df is None:
        return

    visualizer = Visualizer("plots")
    ci_builder = ConfidenceIntervals(0.95)

    models = {'X1': 'exponential', 'X2': 'uniform', 'X3': 'normal'}

    for col in ['X1', 'X2', 'X3']:
        print(f"\n{'═' * 60}\nАнализ столбца {col}")

        data = loader.get_column(col)

        stats_calc = DescriptiveStats(data)
        stats_dict = stats_calc.compute_all()
        print("Статистики:", stats_dict)
        print("Форма распределения:", stats_calc.describe_distribution(stats_dict))

        visualizer.save_histogram(data, col, 'fd')
        visualizer.save_ecdf(data, col)
        visualizer.save_qqplot(data, col)

        if models[col] == 'exponential':
            params = ParameterEstimator.estimate_exponential(data)
        elif models[col] == 'uniform':
            params = ParameterEstimator.estimate_uniform(data)
        else:
            params = ParameterEstimator.estimate_normal(data)
        print("Параметры:", params)

        ci_asymp = ci_builder.asymptotic_ci_mean(data)
        print(f"Асимптотический 95% ДИ для EX: {ci_asymp}")

        if models[col] == 'normal':
            ci_exact = ci_builder.exact_normal_ci(data)
            print("Точные ДИ (нормальное):", ci_exact)


if __name__ == "__main__":
    main()