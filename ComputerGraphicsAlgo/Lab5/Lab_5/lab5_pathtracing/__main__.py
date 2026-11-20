"""Render Lab 5 from a scene JSON file."""

import argparse
from pathlib import Path

from experiment import RESULTS_DIR, SCENE_FILE, Settings, load_scene, run, save


def arguments():
    parser = argparse.ArgumentParser(description="Обратная трассировка путей")
    defaults = Settings()
    parser.add_argument("--gui", action="store_true", help="открыть сравнение изображений")
    parser.add_argument("--scene", type=Path, default=SCENE_FILE, help="файл сцены JSON")
    parser.add_argument("--output", type=Path, default=RESULTS_DIR, help="каталог вывода CLI")
    parser.add_argument("--size", type=int, default=defaults.size, metavar="500..1000")
    parser.add_argument("--samples", type=int, default=defaults.samples, help="число путей на пиксель")
    parser.add_argument("--depth", type=int, default=defaults.depth, help="максимум попаданий пути в поверхности")
    parser.add_argument("--seed", type=int, default=defaults.seed)
    parser.add_argument("--white", type=float, default=defaults.white, help="уровень белого в Вт/(м²·ср)")
    return parser, parser.parse_args()


def main():
    parser, args = arguments()
    try:
        settings = Settings(args.size, args.samples, args.depth, args.seed, args.white)
        config, scene = load_scene(args.scene)
    except (OSError, TypeError, ValueError, KeyError) as error:
        parser.error(f"{args.scene}: {error}")

    if args.gui:
        from gui import launch

        launch(args.scene, config, settings)
        return

    # 报告 §5：命令行和 GUI 共用渲染设置、计算与输出入口，便于复现实验。
    shown = -1

    def progress(fraction):
        nonlocal shown
        step = int(10 * fraction)
        if step > shown:
            print(f"Rendering: {step * 10}%", flush=True)
            shown = step

    data, summary = run(config, scene, settings, progress)
    save(args.output, data, summary)
    print(f"Saved to {args.output.resolve()}")


if __name__ == "__main__":
    main()
