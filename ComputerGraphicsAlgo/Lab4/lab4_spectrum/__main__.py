"""Launch the GUI or reproduce the experiment without a window."""
import argparse
from pathlib import Path
import sys

# Preserve direct IDE execution as well as python -m lab4_spectrum.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "lab4_spectrum"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-gui", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent.parent / "results")
    args = parser.parse_args()
    if args.no_gui:
        from .experiment import run
        from .output import save, summary
        data = run()
        save(data, args.output)
        print(summary(data))
    else:
        from .gui import launch
        launch()


if __name__ == "__main__":
    main()
