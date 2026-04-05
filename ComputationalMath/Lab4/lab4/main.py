import matplotlib.pyplot as plt
import numpy as np

RED    = "\033[1;31m"
YELLOW = "\033[1;33m"
RESET  = "\033[0m"

def err(msg):
    print(f"{RED}Ошибка: {msg}{RESET}")

def hint(msg):
    print(f"{YELLOW}{msg}{RESET}")


def read_from_console():
    hint("Вводите точки в формате 'x y', по одной на строку.")
    hint("Введите 'quit', чтобы закончить ввод.")
    points = []
    while True:
        try:
            line = input("  > ").strip()
        except EOFError:
            break
        if line.lower() == 'quit':
            break
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            err(f"Ожидается ровно 2 числа через пробел. Получено: '{line}'")
            hint("Пример: 1.5 3.2")
            continue
        try:
            x_val, y_val = float(parts[0]), float(parts[1])
        except ValueError:
            err(f"Не удалось прочитать числа из '{line}'.")
            hint("Используйте точку как разделитель дробной части.")
            continue
        points.append((x_val, y_val))
        hint(f"  Добавлено: ({x_val}, {y_val})  [итого {len(points)} точек]")
    return points


def read_from_file(filepath):
    points = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(
                    f"строка {line_num}: ожидается 2 числа, "
                    f"получено {len(parts)} — '{line}'"
                )
            try:
                x_val, y_val = float(parts[0]), float(parts[1])
            except ValueError:
                raise ValueError(
                    f"строка {line_num}: не удалось прочитать числа — '{line}'"
                )
            points.append((x_val, y_val))
    return points


def get_variant_data():
    x = np.arange(-2.0, 0.0 + 0.1, 0.2)
    y = (4 * x) / (x ** 4 + 15)
    return list(zip(x.tolist(), y.tolist()))


# ── Валидация ─────────────────────────────────────────────────────────────────

def validate_data(points):
    if len(points) < 8:
        raise ValueError(
            f"Слишком мало точек: {len(points)}. Требуется минимум 8."
        )
    if len(points) > 12:
        raise ValueError(
            f"Слишком много точек: {len(points)}. Допускается максимум 12."
        )
    x_vals = [p[0] for p in points]
    if len(set(round(v, 10) for v in x_vals)) != len(x_vals):
        raise ValueError("Обнаружены дублирующиеся значения x.")


# ── Вывод результатов ─────────────────────────────────────────────────────────

def write_results(models, best_model, to_file=False, filepath=None):
    lines = []
    sep = "-" * 30
    lines.append(sep)
    for model in models:
        if not getattr(model, 'valid', True):
            lines.append(f"{model.name}:")
            lines.append(f"* Функция: {model.formula()}")
            lines.append("* Неприменима для данных значений (отрицательные x или y)")
            lines.append(sep)
            continue
        lines.append(f"{model.name}:")
        lines.append(f"* Функция: {model.formula()}")
        lines.append(f"* Коэффициенты: {model.print_coeffs()}")
        lines.append(f"* Среднеквадратичное отклонение: σ = {model.sigma:.5f}")
        lines.append(f"* {model.r_squared_message()}")
        lines.append(f"* Мера отклонения: S = {model.S:.5f}")
        if hasattr(model, 'pearson_r'):
            lines.append(f"* Коэффициент корреляции Пирсона: r = {model.pearson_r:.7f}")
        lines.append(sep)
    lines.append(f"Лучшая функция приближения: {best_model.name}")
    lines.append("Спасибо за использование программы!")
    result_text = "\n".join(lines)
    if to_file:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result_text)
        hint(f"Результаты сохранены в файл: {filepath}")
    else:
        print(result_text)


# ── Ввод источника данных ─────────────────────────────────────────────────────

def ask_input_source():
    """Спрашивает источник данных; при любой ошибке возвращает к выбору."""
    while True:
        hint("\nНапишите 'f' — из файла, 'e' — вариант 15, 't' — с клавиатуры:")
        try:
            choice = input("  > ").strip().lower()
        except EOFError:
            choice = 'e'

        if choice == 'f':
            points = ask_file_input()
            if points is None:
                continue          # пользователь сам вернулся назад
        elif choice == 'e':
            points = get_variant_data()
            hint(f"Загружены данные варианта 15 ({len(points)} точек).")
        elif choice == 't':
            points = read_from_console()
        else:
            err(f"Неизвестный вариант '{choice}'. Используйте f / e / t.")
            continue

        try:
            validate_data(points)
        except ValueError as e:
            err(str(e))
            hint("Попробуйте ввести данные снова.")
            continue

        return points


def ask_file_input():
    """Читает файл; возвращает None если пользователь вводит 'back'."""
    while True:
        hint("Введите путь к файлу (или 'back' для возврата к выбору источника):")
        try:
            filepath = input("  > ").strip()
        except EOFError:
            return None

        if filepath.lower() == 'back':
            return None
        if not filepath:
            err("Путь не может быть пустым.")
            continue

        try:
            points = read_from_file(filepath)
            hint(f"Файл прочитан успешно: {len(points)} точек.")
            return points
        except FileNotFoundError:
            err(f"Файл '{filepath}' не найден.")
            hint("Проверьте путь и попробуйте ещё раз.")
        except PermissionError:
            err(f"Нет доступа к файлу '{filepath}'.")
        except ValueError as e:
            err(f"Ошибка формата файла: {e}")
            hint("Каждая строка должна содержать два числа через пробел: 'x y'")
        except Exception as e:
            err(f"Неожиданная ошибка: {e}")


# ── Запрос пути для вывода в файл ─────────────────────────────────────────────

def ask_output_file():
    while True:
        hint("Введите путь для сохранения результатов:")
        try:
            path = input("  > ").strip()
        except EOFError:
            return None
        if not path:
            err("Путь не может быть пустым.")
            continue
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("")
            return path
        except (OSError, PermissionError) as e:
            err(f"Не удалось создать файл '{path}': {e}")
            hint("Проверьте путь и права доступа.")


# ── Запрос направления вывода ─────────────────────────────────────────────────

def ask_output_mode():
    while True:
        hint("\nВывод в файл 'f' или в терминал 't'? [f/t]:")
        try:
            choice = input("  > ").strip().lower()
        except EOFError:
            choice = 't'

        if choice == 't':
            hint("Выбран вывод в терминал.")
            return False, None
        elif choice == 'f':
            path = ask_output_file()
            if path is None:
                continue
            hint("Выбран вывод в файл.")
            return True, path
        else:
            err(f"Неизвестный вариант '{choice}'. Введите f или t.")


# ── График ────────────────────────────────────────────────────────────────────

def build_plot(x, y, models):
    margin = (x[-1] - x[0]) * 0.1
    x_plot = np.linspace(x[0] - margin, x[-1] + margin, 300)

    plt.figure(figsize=(12, 7))
    plt.scatter(x, y, color='red', zorder=5, label='Исходные данные', s=50)

    colors = ['blue', 'green', 'orange', 'purple', 'brown', 'magenta']
    for model, color in zip(models, colors):
        if not getattr(model, 'valid', True):
            continue
        try:
            y_plot = model.predict(x_plot)
            if np.any(np.isnan(y_plot)) or np.any(np.isinf(y_plot)):
                continue
            plt.plot(x_plot, y_plot, color=color, label=model.name, linewidth=1.5)
        except Exception:
            pass

    plt.title("Аппроксимация функции методом наименьших квадратов")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ── Главный цикл ──────────────────────────────────────────────────────────────

def main():
    from models.approximations import (LinearApproximation, QuadraticApproximation,
                                 CubicApproximation, ExponentialApproximation,
                                 LogarithmicApproximation, PowerApproximation)

    print("=" * 50)
    print("  Аппроксимация функции методом наименьших квадратов")
    print("=" * 50)

    while True:
        # 1. Получить данные
        points = ask_input_source()
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])

        # 2. Направление вывода
        to_file, out_path = ask_output_mode()

        # 3. Аппроксимация
        models = [
            LinearApproximation(),
            QuadraticApproximation(),
            CubicApproximation(),
            ExponentialApproximation(),
            LogarithmicApproximation(),
            PowerApproximation(),
        ]

        best_model = None
        min_sigma = float('inf')

        for model in models:
            try:
                model.fit(x, y)
            except Exception as e:
                err(f"Ошибка при обучении модели '{model.name}': {e}")
                model.valid = False
                continue
            if model.sigma < min_sigma:
                min_sigma = model.sigma
                best_model = model

        if best_model is None:
            err("Не удалось построить ни одну аппроксимацию для данных значений.")
            hint("Попробуйте ввести другой набор данных.")
            continue

        # 4. Вывод
        try:
            write_results(models, best_model, to_file, out_path)
        except (OSError, PermissionError) as e:
            err(f"Не удалось записать в файл: {e}")
            hint("Вывод в терминал:")
            write_results(models, best_model, to_file=False)

        # 5. График
        try:
            build_plot(x, y, models)
        except Exception as e:
            err(f"Не удалось построить график: {e}")

        # 6. Продолжить или выйти
        print()
        hint("Нажмите Enter для нового запуска или введите 'exit' для выхода:")
        try:
            again = input("  > ").strip().lower()
        except EOFError:
            again = 'exit'

        if again == 'exit':
            hint("До свидания!")
            break


if __name__ == "__main__":
    main()