import numpy as np
import matplotlib.pyplot as plt

x_centers = np.array([20, 520, 1020, 1520, 2020, 2520])
y_centers = np.array([1200, 2700, 4200, 6700, 8200, 9700, 11200, 12700])

frequencies = np.array([
    [4, 2, 5, 0, 0, 0, 0, 0],      
    [0, 0, 7, 5, 2, 0, 0, 0],      
    [0, 0, 0, 9, 14, 6, 0, 0],     
    [0, 0, 0, 7, 8, 6, 0, 0],      
    [0, 0, 0, 0, 4, 5, 7, 0],     
    [0, 0, 0, 0, 0, 3, 2, 4]       
])

row_sums = frequencies.sum(axis=1)
col_sums = frequencies.sum(axis=0)
expected_mx = np.array([11, 14, 29, 21, 16, 9])
expected_my = np.array([4, 2, 12, 21, 28, 20, 9, 4])

print("Проверка корректности данных:")
print(f"Суммы по строкам (mx): {row_sums} (ожидается: {expected_mx})")
print(f"Суммы по столбцам (my): {col_sums} (ожидается: {expected_my})")
print(f"Строки корректны: {np.allclose(row_sums, expected_mx)}")
print(f"Столбцы корректны: {np.allclose(col_sums, expected_my)}")
print()

N = np.sum(frequencies)

x_expanded = []
y_expanded = []

for i in range(len(x_centers)):      
    for j in range(len(y_centers)):   
        count = frequencies[i][j]
        if count > 0:
            x_expanded.extend([x_centers[i]] * count) 
            y_expanded.extend([y_centers[j]] * count)  

x_arr = np.array(x_expanded)
y_arr = np.array(y_expanded)

mean_x = np.mean(x_arr)
mean_y = np.mean(y_arr)

var_x = np.var(x_arr, ddof=1)
var_y = np.var(y_arr, ddof=1)
std_x = np.std(x_arr, ddof=1)
std_y = np.std(y_arr, ddof=1)

covariance = np.cov(x_arr, y_arr)[0, 1]
r_xy = np.corrcoef(x_arr, y_arr)[0, 1]

a = r_xy * (std_y / std_x)
b = mean_y - a * mean_x

print("=" * 60)
print("РЕЗУЛЬТАТЫ РАСЧЕТОВ")
print("=" * 60)
print(f"Общее количество наблюдений N: {N}")
print(f"\nВыборочные средние:")
print(f"  x̄ = {mean_x:.2f} тыс. ден. ед.")
print(f"  ȳ = {mean_y:.2f} тыс. ед.")
print(f"\nВыборочные дисперсии:")
print(f"  s²ₓ = {var_x:.2f}")
print(f"  s²ᵧ = {var_y:.2f}")
print(f"\nСтандартные отклонения:")
print(f"  sₓ = {std_x:.2f}")
print(f"  sᵧ = {std_y:.2f}")
print(f"\nКорреляционный момент:")
print(f"  sₓᵧ = {covariance:.2f}")
print(f"\nКоэффициент корреляции:")
print(f"  r = {r_xy:.4f}")
print(f"\nУравнение регрессии Y на X:")
print(f"  y = {a:.4f}x + {b:.2f}")
print("=" * 60)

plt.figure(figsize=(12, 8))
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']

for i in range(len(x_centers)):
    for j in range(len(y_centers)):
        count = frequencies[i][j]
        if count > 0:
            plt.scatter(x_centers[i], y_centers[j],
                       s=count*30, c='blue', alpha=0.6,
                       edgecolors='navy', linewidth=1.5,
                       label='Наблюдения' if i==0 and j==0 else "")

            plt.text(x_centers[i], y_centers[j], str(count),
                    ha='center', va='center', fontsize=8, color='white', weight='bold')

x_line = np.linspace(min(x_centers)-100, max(x_centers)+100, 100)
y_line = a * x_line + b
plt.plot(x_line, y_line, color='red', linewidth=2.5,
         label=f'Регрессия: y = {a:.2f}x + {b:.0f}')

conditional_means_x = []
conditional_means_y = []
for i in range(len(x_centers)):
    if frequencies[i].sum() > 0:
        y_mean = np.sum(frequencies[i] * y_centers) / frequencies[i].sum()
        conditional_means_x.append(x_centers[i])
        conditional_means_y.append(y_mean)

plt.scatter(conditional_means_x, conditional_means_y,
           s=100, c='green', marker='D',
           edgecolors='darkgreen', linewidth=2,
           label='Условные средние', zorder=5)

plt.xlabel('Производственные средства X (тыс. ден. ед.)', fontsize=12)
plt.ylabel('Суточная выработка Y (тыс. ед.)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11, loc='upper left')
plt.tight_layout()

plt.savefig('regression_plot.png', dpi=300, bbox_inches='tight')
print("\nГрафик сохранен как 'regression_plot.png'")

plt.show()