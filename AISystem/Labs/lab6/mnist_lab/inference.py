from pathlib import Path
import json
import time
import numpy as np
from PIL import Image, ImageOps
from .data import ROOT


def preprocess_image(path):
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image).convert('RGBA')
        background = Image.new('RGBA', image.size, 'white')
        background.alpha_composite(image)
        gray = np.asarray(background.convert('L'), dtype=np.float32)
    border = np.concatenate((gray[0], gray[-1], gray[:, 0], gray[:, -1]))
    if np.median(border) > 127:
        gray = 255 - gray
    if gray.max() - gray.min() < 15:
        raise ValueError('Blank image: draw one digit with a contrasting background.')
    gray = np.maximum(gray - np.median(np.concatenate((gray[0], gray[-1], gray[:, 0], gray[:, -1]))), 0)
    ys, xs = np.where(gray > max(15, gray.max() * 0.1))
    if len(xs) == 0:
        raise ValueError('No digit found.')
    crop = Image.fromarray(gray[ys.min():ys.max()+1, xs.min():xs.max()+1].astype(np.uint8))
    scale = 20 / max(crop.size)
    crop = crop.resize(tuple(max(1, round(v * scale)) for v in crop.size), Image.Resampling.LANCZOS)
    canvas = Image.new('L', (28, 28))
    canvas.paste(crop, ((28-crop.width)//2, (28-crop.height)//2))
    pixels = np.asarray(canvas, dtype=np.float32)
    yy, xx = np.indices(pixels.shape)
    dx = round(13.5 - float((pixels * xx).sum() / pixels.sum()))
    dy = round(13.5 - float((pixels * yy).sum() / pixels.sum()))
    centered = Image.new('L', (28, 28))
    centered.paste(canvas, (dx, dy))  # Paste clips rather than wrapping pixels.
    return np.asarray(centered, dtype=np.float32) / 255


def predict_image(model, path):
    pixels = preprocess_image(path)
    logits = model.forward(pixels[None])
    probs = np.exp(logits - logits.max())
    probs /= probs.sum()
    return int(probs.argmax()), probs[0]


def show_prediction(model, path):
    import matplotlib.pyplot as plt
    start = time.perf_counter()
    digit, probs = predict_image(model, path)
    elapsed = time.perf_counter() - start
    fig, axes = plt.subplots(1, 3, figsize=(10, 3))
    with Image.open(path) as image:
        axes[0].imshow(image.copy())
    axes[0].set_title('Original'); axes[0].axis('off')
    axes[1].imshow(preprocess_image(path), cmap='gray', vmin=0, vmax=1)
    axes[1].set_title('MNIST preprocessing'); axes[1].axis('off')
    axes[2].bar(range(10), probs); axes[2].set_xticks(range(10))
    axes[2].set(xlabel='Digit', ylabel='Probability', title=f'Prediction: {digit}')
    fig.tight_layout()
    print(f'Prediction: {digit}; inference: {elapsed:.4f} s')
    print(dict(enumerate(probs.tolist())))
    return fig, digit, probs


def evaluate_drawings(model):
    """Only user-provided drawings belong in drawings/, named 0.png ... 9_2.png."""
    import matplotlib.pyplot as plt
    records = []
    for path in sorted((ROOT / 'drawings').glob('*')):
        if path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.bmp'):
            continue
        if not path.stem.split('_')[0].isdigit() or not 0 <= int(path.stem.split('_')[0]) <= 9:
            raise ValueError('Drawing filename must start with its true digit: ' + path.name)
        figure, digit, probs = show_prediction(model, path)
        output = ROOT / 'output' / 'figures' / ('drawing_' + path.stem + '.png')
        figure.savefig(output, dpi=160); plt.close(figure)
        records.append(dict(file=path.name, true=int(path.stem.split('_')[0]), predicted=digit,
                            probabilities=probs.tolist(), figure=output.name))
    (ROOT / 'output' / 'drawings.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    return records
