from color import Color


class InputHandler:

    @staticmethod
    def _ask(prompt: str) -> str:
        return input(Color.warn(f"  {prompt}"))

    @classmethod
    def get_float(cls, prompt: str) -> float:
        while True:
            raw = cls._ask(prompt)
            try:
                return float(raw)
            except ValueError:
                Color.print_error(f"«{raw}» — не число. Повторите ввод.")

    @classmethod
    def get_positive_float(cls, prompt: str) -> float:
        while True:
            val = cls.get_float(prompt)
            if val > 0:
                return val
            Color.print_error("Значение должно быть строго больше нуля.")

    @classmethod
    def get_int_in_range(cls, prompt: str, lo: int, hi: int) -> int:
        while True:
            raw = cls._ask(prompt)
            try:
                val = int(raw)
                if lo <= val <= hi:
                    return val
                Color.print_error(
                    f"Нужно число от {lo} до {hi}, получено: {val}."
                )
            except ValueError:
                Color.print_error(f"«{raw}» — не целое число.")

    @classmethod
    def get_yes_no(cls, prompt: str) -> bool:
        while True:
            raw = cls._ask(f"{prompt} (y/n): ").strip().lower()
            if raw in ("y", "yes", "д", "да"):
                return True
            if raw in ("n", "no", "н", "нет"):
                return False
            Color.print_error("Введите 'y' (да) или 'n' (нет).")
