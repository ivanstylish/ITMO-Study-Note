import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ==============================================================================
# ВАРИАНТ 6: Данные (5 образцов, 2 признака, 1 целевая переменная)
# ==============================================================================
X_data = np.array([[0.88, 1.14],
                   [1.92, 1.95],
                   [2.85, 3.04],
                   [3.88, 4.12],
                   [5.02, 5.03]])
y_data = np.array([-0.10, 1.72, 4.73, 2.27, 0.03])


class RBFNetwork:
    def __init__(self, n_neurons=2):
        self.n_neurons = n_neurons
        self.centers = None
        self.sigmas_sq = None
        self.weights = None  # [w0, w1, w2]

    def _kmeans_from_scratch(self, X, max_iter=100):
        """K-Means с нуля без sklearn для инициализации центров (без учителя)"""
        np.random.seed(42)
        # Выбираем первые и последние точки как начальные центры для стабильности
        centers = np.array([X[0], X[-1]])

        print("--- Запуск K-Means (Обучение без учителя) ---")
        for i in range(max_iter):
            # Вычисление расстояний
            distances = np.zeros((X.shape[0], self.n_neurons))
            for j in range(self.n_neurons):
                distances[:, j] = np.sqrt(np.sum((X - centers[j]) ** 2, axis=1))

            # Присвоение кластеров
            labels = np.argmin(distances, axis=1)

            # Обновление центров
            new_centers = np.copy(centers)
            for j in range(self.n_neurons):
                cluster_points = X[labels == j]
                if len(cluster_points) > 0:
                    new_centers[j] = np.mean(cluster_points, axis=0)

            print(f"Итерация K-Means {i + 1}: Центры = {new_centers}")

            if np.all(centers == new_centers):
                break
            centers = new_centers

        print(f"Итоговые центры: {centers}\n")
        return centers

    def fit(self, X, y, epochs=3000, lr=0.01):
        """Обучение RBF сети: K-means + Градиентный спуск (с учителем)"""
        N = X.shape[0]

        # 1. Без учителя: Инициализация центров
        self.centers = self._kmeans_from_scratch(X)

        # 2. Инициализация сигм (ширин)
        d = np.sqrt(np.sum((self.centers[0] - self.centers[1]) ** 2))
        self.sigmas_sq = np.array([d ** 2 / 4, d ** 2 / 4])  # sigma^2 = (d/2)^2

        # 3. Инициализация весов
        self.weights = np.array([0.0, 0.1, 0.1])  # w0, w1, w2

        print("--- Запуск Градиентного Спуска (Обучение с учителем) ---")
        loss_history = []

        for epoch in range(epochs):
            # Прямое распространение
            phi = np.zeros((N, self.n_neurons))
            for j in range(self.n_neurons):
                r_sq = np.sum((X - self.centers[j]) ** 2, axis=1)
                phi[:, j] = np.exp(-r_sq / (2 * self.sigmas_sq[j]))

            y_pred = self.weights[0] + np.dot(phi, self.weights[1:])
            errors = y_pred - y

            # Loss (MSE)
            mse = 0.5 * np.mean(errors ** 2)
            loss_history.append(mse)

            # Подробная запись каждые 500 итераций и на 1-й итерации
            if epoch % 500 == 0 or epoch == 0:
                print(f"Эпоха {epoch}: Loss = {mse:.6f} | Веса = {self.weights} | Сигмы^2 = {self.sigmas_sq}")

            # Вычисление градиентов
            grad_w0 = np.mean(errors)
            grad_w = np.zeros(self.n_neurons)
            grad_centers = np.zeros_like(self.centers)
            grad_sigmas_sq = np.zeros(self.n_neurons)

            for j in range(self.n_neurons):
                grad_w[j] = np.mean(errors * phi[:, j])
                # Градиент по центрам
                diff = X - self.centers[j]
                term = (errors * self.weights[j + 1] * phi[:, j])[:, np.newaxis] * diff
                grad_centers[j] = -np.mean(term, axis=0) / self.sigmas_sq[j]
                # Градиент по сигмам
                r_sq = np.sum(diff ** 2, axis=1)
                grad_sigmas_sq[j] = -np.mean(errors * self.weights[j + 1] * phi[:, j] * r_sq) / (
                            2 * self.sigmas_sq[j] ** 2)

            # Обновление параметров
            self.weights[0] -= lr * grad_w0
            self.weights[1:] -= lr * grad_w
            self.centers -= lr * grad_centers
            self.sigmas_sq -= lr * grad_sigmas_sq

            # Ограничение, чтобы сигма не стала отрицательной
            self.sigmas_sq = np.maximum(self.sigmas_sq, 0.1)

        print(f"Финальный результат: Loss = {loss_history[-1]:.6f}")
        return loss_history

    def predict(self, X):
        N = X.shape[0]
        phi = np.zeros((N, self.n_neurons))
        for j in range(self.n_neurons):
            r_sq = np.sum((X - self.centers[j]) ** 2, axis=1)
            phi[:, j] = np.exp(-r_sq / (2 * self.sigmas_sq[j]))
        return self.weights[0] + np.dot(phi, self.weights[1:])


# ==============================================================================
# Тренировка и визуализация
# ==============================================================================
rbf = RBFNetwork(n_neurons=2)
loss_history = rbf.fit(X_data, y_data, epochs=3000, lr=0.01)

# Предсказания и невязки
predictions = rbf.predict(X_data)
residuals = y_data - predictions

print("\nНевязки на объектах:")
for i in range(len(y_data)):
    print(f"Точка {i}: Реальное={y_data[i]:.2f}, Предсказание={predictions[i]:.2f}, Невязка={residuals[i]:.4f}")

# Аналитический вид модели
w0, w1, w2 = rbf.weights
cx1, cy1 = rbf.centers[0]
cx2, cy2 = rbf.centers[1]
s1, s2 = rbf.sigmas_sq
print(f"\nАналитический вид модели:")
print(
    f"z(x,y) = {w0:.4f} + {w1:.4f} * exp(-((x-{cx1:.4f})^2+(y-{cy1:.4f})^2)/(2*{s1:.4f})) + {w2:.4f} * exp(-((x-{cx2:.4f})^2+(y-{cy2:.4f})^2)/(2*{s2:.4f}))")

# Визуализация
fig = plt.figure(figsize=(18, 5))

# 1. Кривая обучения
ax1 = fig.add_subplot(131)
ax1.plot(loss_history, color='blue')
ax1.set_title('Кривая обучения (Loss по итерациям)')
ax1.set_xlabel('Итерация')
ax1.set_ylabel('MSE Loss')
ax1.grid(True)

# 2. 3D поверхность
x_grid = np.linspace(0, 6, 50)
y_grid = np.linspace(0, 6, 50)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
grid_points = np.c_[X_grid.ravel(), Y_grid.ravel()]
Z_grid = rbf.predict(grid_points).reshape(50, 50)

ax2 = fig.add_subplot(132, projection='3d')
ax2.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', alpha=0.8)
ax2.scatter(X_data[:, 0], X_data[:, 1], y_data, c='red', s=50, label='Данные')
ax2.set_title('3D-визуализация RBF-сети')

# 3. Линии уровня
ax3 = fig.add_subplot(133)
contour = ax3.contourf(X_grid, Y_grid, Z_grid, levels=25, cmap='viridis', alpha=0.9)
ax3.scatter(X_data[:, 0], X_data[:, 1], c=y_data, s=120, edgecolors='black', cmap='viridis')
ax3.set_title('Линии уровня')
plt.colorbar(contour, ax=ax3)

plt.tight_layout()
plt.show()