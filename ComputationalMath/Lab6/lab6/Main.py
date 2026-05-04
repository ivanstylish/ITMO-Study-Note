import traceback
import ODEEquation

from EquationBank import build_equation_bank
from Plotter import Plotter
from TablePrinter import TablePrinter
from Error import ErrorEstimator
from color import Color
from Input import InputHandler
from methods.Euler import EulerMethod
from methods.RungeKutta4 import RungeKutta4
from methods.Adams import AdamsMethod
from methods.ODEsolver import ODESolver


class Main:

    _DEFAULT_H = 0.1
    _DEFAULT_EPS = 1e-3

    def __init__(self):
        self._bank = build_equation_bank()
        self._solvers = {
            "euler": EulerMethod(),
            "rk4":   RungeKutta4(),
            "adams": AdamsMethod(),
        }
        self._inp = InputHandler()


    def run(self) -> None:
        self._banner()
        while True:
            try:
                self._session()
            except KeyboardInterrupt:
                print()
                Color.print_warn("Прерывание пользователем.")
            except Exception as e:
                Color.print_error(f"Непредвиденная ошибка: {e}")
                traceback.print_exc()

            if not self._inp.get_yes_no("\nЗапустить ещё раз"):
                break

        print(Color.ok("\n  IM OUT OF HERE!\n"))


    def _session(self) -> None:
        eq = self._choose_equation()
        x0, y0, xn, h, eps = self._get_params(eq)
        self._print_params(eq, x0, y0, xn, h, eps)

        collected: dict = {}

        # Метод Эйлера
        solver = self._solvers["euler"]
        res = self._safe_solve(solver, eq, x0, y0, xn, h)
        if res:
            TablePrinter.print(solver.name, eq, x0, y0, *res)
            self._runge_report(solver, eq, x0, y0, xn, h, eps)
            collected[solver.name] = res

        # Метод Рунге-Кутта 4
        solver = self._solvers["rk4"]
        res = self._safe_solve(solver, eq, x0, y0, xn, h)
        if res:
            TablePrinter.print(solver.name, eq, x0, y0, *res)
            self._runge_report(solver, eq, x0, y0, xn, h, eps)
            collected[solver.name] = res

        # Метод Адамса
        solver = self._solvers["adams"]
        res = self._safe_solve(solver, eq, x0, y0, xn, h, eps=eps)
        if res:
            TablePrinter.print(solver.name, eq, x0, y0, *res)
            self._max_norm_report(solver, eq, x0, y0, res)
            collected[solver.name] = res

        # Графики
        if collected:
            self._save_plot(eq, collected, x0, y0, xn, h)
        else:
            Color.print_warn("Ни один метод не дал результата — график не строится.")

    def _choose_equation(self) -> ODEEquation:
        print(f"\n{Color.header('  Доступные уравнения:')}")
        for num, eq in self._bank.all_items():
            print(f"    {Color.info(str(num))}.  {eq.label}"
                  f"   {Color.header('|')}  точное: {eq.exact_info}")
        num = self._inp.get_int_in_range(
            f"\nВыберите уравнение (1–{self._bank.count()}): ",
            1, self._bank.count(),
        )
        return self._bank.get(num)

    def _get_params(self, eq: ODEEquation) -> tuple:
        Color.print_info(
            f"Значения по умолчанию: "
            f"x0={eq.default_x0}, y0={eq.default_y0}, "
            f"xn={eq.default_xn}, h={self._DEFAULT_H}, ε={self._DEFAULT_EPS}"
        )
        if self._inp.get_yes_no("Использовать значения по умолчанию"):
            return (eq.default_x0, eq.default_y0, eq.default_xn,
                    self._DEFAULT_H, self._DEFAULT_EPS)

        x0 = self._inp.get_float("x0 (начало интервала): ")
        y0 = self._inp.get_float("y0 = y(x0): ")
        while True:
            xn = self._inp.get_float("xn (конец интервала, > x0): ")
            if xn > x0:
                break
            Color.print_error(f"xn должен быть > x0 = {x0}.")

        h   = self._inp.get_positive_float("Шаг h (> 0): ")
        eps = self._inp.get_positive_float("Точность ε (> 0): ")
        return x0, y0, xn, h, eps

    @staticmethod
    def _banner() -> None:
        line = "═" * 62
        print(Color.header(f"\n{line}"))
        print(Color.header("  Лабораторная работа N.6 — Численное решение ОДУ"))
        print(Color.header("  Вариант 15:  Эйлера  |  Рунге-Кутта 4  |  Адамса"))
        print(Color.header(line))

    @staticmethod
    def _print_params(eq, x0, y0, xn, h, eps) -> None:
        sep = "─" * 62
        print(f"\n{Color.header(sep)}")
        Color.print_info(f"Уравнение  : {eq.label}")
        Color.print_info(f"Нач. усл.  : y({x0}) = {y0}")
        Color.print_info(f"Интервал   : [{x0}, {xn}]")
        Color.print_info(f"Шаг h      : {h}")
        Color.print_info(f"Точность ε : {eps}")
        print(Color.header(sep))

    @staticmethod
    def _safe_solve(solver: ODESolver, eq: ODEEquation,
                    x0, y0, xn, h, **kw):
        try:
            return solver.solve(eq, x0, y0, xn, h, **kw)
        except ValueError as e:
            Color.print_error(f"[{solver.name}]  {e}")
            return None
        except OverflowError as e:
            Color.print_error(f"[{solver.name}] Переполнение:  {e}")
            return None
        except Exception as e:
            Color.print_error(f"[{solver.name}] Неожиданная ошибка:  {e}")
            traceback.print_exc()
            return None

    @staticmethod
    def _runge_report(solver, eq, x0, y0, xn, h, eps) -> None:
        try:
            R, ok = ErrorEstimator.runge_estimate(solver, eq, x0, y0, xn, h, eps)
            status = (Color.ok("достигнута") if ok
                      else Color.warn("не достигнута"))
            print(f"  Правило Рунге: R = {Color.info(f'{R:.2e}')}  ->  точность {status}")
        except Exception as e:
            Color.print_error(f"[{solver.name}] Правило Рунге — ошибка: {e}")

    @staticmethod
    def _max_norm_report(solver, eq, x0, y0, res) -> None:
        try:
            err = ErrorEstimator.max_norm_error(eq, x0, y0, *res)
            print(Color.ok(f"  ε = max|y_exact − y_i| = {err:.2e}"))
        except Exception as e:
            Color.print_error(
                f"[{solver.name}] Ошибка вычисления погрешности: {e}"
            )

    @staticmethod
    def _save_plot(eq, named_results, x0, y0, xn, h) -> None:
        try:
            path = Plotter.plot(eq, named_results, x0, y0, xn, h)
            Color.print_ok(f"График сохранён -> {path}")
        except Exception as e:
            Color.print_error(f"Не удалось построить график: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    Main().run()