# =====================================================================
#  Color — ANSI цветовые константы для терминала
# =====================================================================

class Color:
    RED    = "\033[1;31m"   # ошибки
    YELLOW = "\033[1;33m"   # предупреждения / подсказки
    GREEN  = "\033[1;32m"   # успех
    CYAN   = "\033[1;36m"   # информация / заголовки
    RESET  = "\033[0m"

    @staticmethod
    def red(text):    return f"{Color.RED}{text}{Color.RESET}"
    @staticmethod
    def yellow(text): return f"{Color.YELLOW}{text}{Color.RESET}"
    @staticmethod
    def green(text):  return f"{Color.GREEN}{text}{Color.RESET}"
    @staticmethod
    def cyan(text):   return f"{Color.CYAN}{text}{Color.RESET}"