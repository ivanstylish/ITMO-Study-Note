import argparse
from .data import ROOT
from .model import Network


def main():
    parser = argparse.ArgumentParser(description='NumPy MNIST laboratory')
    parser.add_argument('mode', choices=['train', 'predict', 'drawings'])
    parser.add_argument('image', nargs='?')
    args = parser.parse_args()
    if args.mode == 'train':
        from .training import run_experiments
        run_experiments()
        return
    path = ROOT / 'output' / 'best_model.npz'
    if not path.exists():
        parser.error('Saved weights not found. Run training first.')
    model = Network.load(path)
    if args.mode == 'drawings':
        from .inference import evaluate_drawings
        print(evaluate_drawings(model))
    else:
        if not args.image:
            parser.error('predict requires an image path.')
        from .inference import show_prediction
        figure, _, _ = show_prediction(model, args.image)
        figure.savefig(ROOT / 'output' / 'prediction.png', dpi=160)
        print('Saved output/prediction.png')


if __name__ == '__main__':
    main()
