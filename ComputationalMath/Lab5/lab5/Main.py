from FiniteDiffTable import FiniteDiffTable
from Interpolator import Interpolator
from DrawChart import DrawChart as Plotter
from Data import Data
from Color import Color


class Main:

    MENU = {
        "1": "Ввод данных с клавиатуры",
        "2": "Загрузка данных из файла",
        "3": "Генерация данных из функции",
        "4": "Демо: вариант 15 (таблица 1.5)",
        "0": "Выход",
    }

    def run(self):
        print(Color.cyan("=" * 62))
        print(Color.cyan("  Лаб. работа №5: Интерполяция  |  Вариант 15"))
        print(Color.cyan("=" * 62))

        while True:
            print("\nГлавное меню:")
            for key, desc in self.MENU.items():
                print(f"  {key}. {desc}")

            choice = input("Выбор: ").strip()
            if choice == "0":
                print("SORRY IM OUT OF HERE...")
                break

            data = self._load_data(choice)
            if data is None:
                continue

            print("\n" + Color.cyan("=" * 62))
            print(Color.cyan("Таблица конечных разностей:"))
            try:
                FiniteDiffTable(data).print()
            except ValueError as e:
                print(Color.red(f"  Таблица недоступна: {e}"))

            ip = Interpolator(data)

            query_points = []
            while True:
                xp = self._ask_query_point(data)
                results = ip.compute_all(xp)
                Interpolator.print_results(xp, results)
                query_points.append((xp, f"x={xp}"))

                again = input(
                    "\nВычислить ещё одну точку? [y/n]: "
                ).strip().lower()
                if again not in ("д", "y", "yes", "да"):
                    break

            try:
                Plotter(data, ip).plot(
                    query_points,
                    title="Интерполяция (вариант 15)",
                )
            except Exception as e:
                print(Color.red(f"  Не удалось построить график: {e}"))

            again = input(
                "\nВернуться в главное меню? [y/n]: "
            ).strip().lower()
            if again not in ("д", "y", "yes", "да"):
                print("SORRY IM OUT OF HERE...")
                break

    @staticmethod
    def _load_data(choice):
        loaders = {
            "1": Data.from_keyboard,
            "2": Data.from_file,
            "3": Data.from_function,
            "4": Data.demo_var15,
        }
        loader = loaders.get(choice)
        if loader is None:
            print(Color.yellow("  Неверный пункт меню, попробуйте ещё раз."))
            return None
        try:
            return loader()
        except (ValueError, KeyboardInterrupt) as e:
            print(Color.red(f"  Ошибка: {e}"))
            return None

    @staticmethod
    def _ask_query_point(data):
        lo, hi = data.x[0], data.x[-1]
        while True:
            raw = input(
                f"Введите точку интерполяции (диапазон [{lo}, {hi}]): "
            ).strip()
            try:
                xp = float(raw)
            except ValueError:
                print(Color.red("  Ошибка: введите число."))
                continue
            if xp < lo or xp > hi:
                ans = input(Color.yellow(
                    f"  x={xp} вне диапазона (экстраполяция). "
                    f"Продолжить? [y/n]: "
                )).strip().lower()
                if ans not in ("д", "y", "yes", "да"):
                    continue
            return xp



if __name__ == "__main__":
    Main().run()