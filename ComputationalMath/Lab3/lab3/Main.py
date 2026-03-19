from Functions import Functions
from Methods import Methods
from Integrator import Integrator


class Main:
    """Консольный интерфейс приложения."""

    @staticmethod
    def run() -> None:
        print("=" * 55)
        print("  Лабораторная работа №3. Численное интегрирование")
        print("=" * 55)

        while True:
            print("\n\033[36mВыберите действие:\033[0m")
            print("  1. Вычислить интеграл")
            print("  0. Выйти из программы")
            action = Main._get_int("Ваш выбор: ", 0, 1)
            if action == 0:
                print("\nПрограмма завершена.")
                break

            func_names = list(Functions.REGISTRY.keys())
            func_name  = Main._select(func_names, "функцию")
            func_entry = Functions.REGISTRY[func_name]

            a = Main._get_float("Введите нижний предел интегрирования: ")
            b = Main._get_float("Введите верхний предел интегрирования: ")
            if a >= b:
                print("\033[31mОшибка: нижний предел должен быть меньше верхнего.\033[0m")
                continue

            method_names = list(Methods.REGISTRY.keys())
            method_name  = Main._select(method_names, "метод интегрирования")
            method_entry = Methods.REGISTRY[method_name]

            eps = Main._get_float("Введите требуемую точность: ")
            if eps <= 0:
                print("\033[31mОшибка: точность должна быть положительной.\033[0m")
                continue

            try:
                value, n_final = Integrator.compute(func_entry, method_entry, a, b, eps)
                print(f"\n\033[32mЗначение интеграла: {value}\033[0m")
                print(f"\033[32mЧисло разбиений для достижения точности {eps}: {n_final}\033[0m")
            except (ValueError, RuntimeError) as e:
                print(f"\n\033[31m{e}\033[0m")


    @staticmethod
    def _select(items: list[str], label: str) -> str:
        print(f"\nВыберите {label}:")
        for i, name in enumerate(items, 1):
            print(f"  {i}. {name}")
        while True:
            try:
                choice = int(input("\033[33mВаш выбор: \033[0m"))
                if 1 <= choice <= len(items):
                    return items[choice - 1]
                print(f"Введите число от 1 до {len(items)}.")
            except ValueError:
                print("\033[31mНеверный ввод.\033[0m")

    @staticmethod
    def _get_int(prompt: str, lo: int, hi: int) -> int:
        while True:
            try:
                val = int(input(prompt))
                if lo <= val <= hi:
                    return val
                print(f"\033[31mВведите число от {lo} до {hi}.\033[0m")
            except ValueError:
                print("\033[31mНеверный ввод.\033[0m")

    @staticmethod
    def _get_float(prompt: str) -> float:
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("\033[31mНеверный ввод, введите число.\033[0m")


if __name__ == "__main__":
    Main.run()