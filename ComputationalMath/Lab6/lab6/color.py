class Color:
    _RED = "\033[91m"
    _YELLOW = "\033[93m"
    _GREEN = "\033[92m"
    _CYAN = "\033[96m"
    _BOLD = "\033[1m"
    _RESET = "\033[0m"

    @classmethod
    def _fmt(cls, code: str, text: str) -> str:
        return f"{code}{text}{cls._RESET}"

    @classmethod
    def error(cls, text: str) -> str:   return cls._fmt(cls._RED, text)

    @classmethod
    def warn(cls, text: str) -> str:    return cls._fmt(cls._YELLOW, text)

    @classmethod
    def ok(cls, text: str) -> str:      return cls._fmt(cls._GREEN, text)

    @classmethod
    def info(cls, text: str) -> str:    return cls._fmt(cls._CYAN, text)

    @classmethod
    def header(cls, text: str) -> str:  return cls._fmt(cls._BOLD, text)

    @classmethod
    def print_error(cls, text: str) -> None:
        print(cls.error(f"{text}"))

    @classmethod
    def print_warn(cls, text: str) -> None:
        print(cls.warn(f"{text}"))

    @classmethod
    def print_ok(cls, text: str) -> None:
        print(cls.ok(f"{text}"))

    @classmethod
    def print_info(cls, text: str) -> None:
        print(cls.info(f"{text}"))