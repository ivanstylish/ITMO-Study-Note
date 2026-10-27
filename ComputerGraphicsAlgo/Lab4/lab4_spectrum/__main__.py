"""Launch the Lab 4 GUI or calculate the default experiment."""
import argparse
from pathlib import Path
from .experiment import run
from .output import save, summary

BASE = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--output", type=Path, default=BASE / "results")
    args = parser.parse_args()
    if args.no_gui:
        data = run()
        save(data, args.output)
        print(summary(data))
    else:
        from .gui import launch
        launch()


if __name__ == "__main__":
    main()
