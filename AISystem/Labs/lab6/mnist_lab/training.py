import csv
import json
import time
import numpy as np
from .data import ROOT, load_data, one_hot
from .layers import SoftmaxWithLoss
from .model import Network, Adam

CONFIGS = [('A', [784, 128, 10], 0), ('B', [784, 256, 10], 0),
           ('C', [784, 256, 128, 10], 0), ('D', [784, 256, 128, 10], 0.2)]
OUT = ROOT / 'output'


def evaluate(model, x, y, batch=512):
    loss, correct, predictions = 0.0, 0, []
    criterion = SoftmaxWithLoss()
    for start in range(0, len(x), batch):
        logits = model.forward(x[start:start+batch])
        labels = y[start:start+batch]
        loss += criterion.forward(logits, one_hot(labels)) * len(labels)
        pred = logits.argmax(axis=1)
        correct += int((pred == labels).sum())
        predictions.append(pred)
    return loss / len(x), correct / len(x), np.concatenate(predictions)


def train_epoch(model, optimizer, x, y, rng, batch=128):
    criterion = SoftmaxWithLoss()
    order = rng.permutation(len(x))
    for start in range(0, len(x), batch):
        ids = order[start:start+batch]
        logits = model.forward(x[ids], training=True)
        loss = criterion.forward(logits, one_hot(y[ids]))
        if not np.isfinite(loss):
            raise FloatingPointError('Training loss is not finite.')
        model.backward(criterion.backward())
        optimizer.step(model.parameters())


def run_experiments():
    from .graphics import data_figures, learning_curves, test_figures
    OUT.mkdir(exist_ok=True)
    (OUT / 'figures').mkdir(exist_ok=True)
    x, y, xt, yt = load_data()
    order = np.random.default_rng(42).permutation(len(y))
    val, train = order[:6000], order[6000:]
    np.savez(OUT / 'split.npz', train=train, val=val)
    data_figures(x, y)
    results = []
    for name, widths, dropout in CONFIGS:
        model, optimizer = Network(widths, dropout), Adam()
        rng, history, best = np.random.default_rng(42), [], None
        start = time.perf_counter()
        for epoch in range(1, 16):
            train_epoch(model, optimizer, x[train], y[train], rng)
            tl, ta, _ = evaluate(model, x[train], y[train])
            vl, va, _ = evaluate(model, x[val], y[val])
            row = dict(epoch=epoch, train_loss=tl, train_accuracy=ta, val_loss=vl, val_accuracy=va)
            history.append(row)
            if best is None or (va, -vl) > (best['val_accuracy'], -best['val_loss']):
                best = row.copy()
                model.save(OUT / f'model_{name}.npz')
            print(f'{name} {epoch:02}/15 train={ta:.4%} val={va:.4%} loss={tl:.4f}/{vl:.4f}', flush=True)
        with (OUT / f'history_{name}.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(history[0])); writer.writeheader(); writer.writerows(history)
        learning_curves(name, history)
        results.append(dict(name=name, widths=widths, dropout=dropout, best=best,
                            seconds=time.perf_counter()-start))
    winner = max(results, key=lambda r: (r['best']['val_accuracy'], -r['best']['val_loss']))
    model = Network.load(OUT / f"model_{winner['name']}.npz")
    model.save(OUT / 'best_model.npz')
    loss, accuracy, predicted = evaluate(model, xt, yt)
    confusion = np.zeros((10, 10), dtype=int)
    np.add.at(confusion, (yt, predicted), 1)
    np.savetxt(OUT / 'confusion_matrix.csv', confusion, delimiter=',', fmt='%d')
    np.savetxt(OUT / 'test_predictions.csv', np.column_stack((yt, predicted)), delimiter=',',
               header='true,predicted', comments='', fmt='%d')
    test_figures(xt, yt, predicted, confusion)
    summary = dict(seed=42, train_size=len(train), val_size=len(val), test_size=len(yt),
                   epochs=15, batch_size=128, learning_rate=0.001,
                   train_classes=np.bincount(y[train], minlength=10).tolist(),
                   val_classes=np.bincount(y[val], minlength=10).tolist(),
                   test_classes=np.bincount(yt, minlength=10).tolist(),
                   experiments=results, winner=winner['name'], test_loss=loss,
                   test_accuracy=accuracy, errors=int((predicted != yt).sum()))
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2), flush=True)

