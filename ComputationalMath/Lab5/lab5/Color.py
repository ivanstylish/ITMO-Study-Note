class Color:
    RED    = "\033[1;31m"
    YELLOW = "\033[1;33m"
    GREEN  = "\033[1;32m"
    CYAN   = "\033[1;36m"
    RESET  = "\033[0m"

    @staticmethod
    def red(text):    return f"{Color.RED}{text}{Color.RESET}"
    @staticmethod
    def yellow(text): return f"{Color.YELLOW}{text}{Color.RESET}"
    @staticmethod
    def green(text):  return f"{Color.GREEN}{text}{Color.RESET}"
    @staticmethod
    def cyan(text):   return f"{Color.CYAN}{text}{Color.RESET}"