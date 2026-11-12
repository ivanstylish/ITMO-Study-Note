import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .data import ROOT

FIG = ROOT / 'output' / 'figures'


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=160)
    plt.close(fig)


def data_figures(x, y):
    fig, axes = plt.subplots(5, 5, figsize=(7, 7))
    for i, ax in enumerate(axes.flat):
        ax.imshow(x[i], cmap='gray'); ax.set_title(str(y[i])); ax.axis('off')
    fig.suptitle('MNIST examples')
    save(fig, 'examples.png')
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.bar(range(10), np.bincount(y)); ax.set_xticks(range(10))
    ax.set(xlabel='Digit', ylabel='Count', title='Official training set: 60,000 images')
    save(fig, 'classes.png')


def learning_curves(name, history):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    for ax, metric in zip(axes, ('loss', 'accuracy')):
        for split in ('train', 'val'):
            ax.plot([r['epoch'] for r in history], [r[f'{split}_{metric}'] for r in history], label=split)
        ax.set(xlabel='Epoch', ylabel=metric.capitalize(), title=f'Model {name}: {metric}')
        ax.legend(); ax.grid(alpha=0.2)
    save(fig, f'curves_{name}.png')


def test_figures(x, y, predicted, confusion):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(confusion, cmap='Blues')
    for i in range(10):
        for j in range(10):
            ax.text(j, i, str(confusion[i, j]), ha='center', va='center', fontsize=7,
                    color='white' if confusion[i, j] > confusion.max()/2 else 'black')
    ax.set(xticks=range(10), yticks=range(10), xlabel='Predicted', ylabel='True', title='Test confusion matrix')
    fig.colorbar(im, ax=ax)
    save(fig, 'confusion.png')
    ids = np.flatnonzero(y != predicted)[:12]
    fig, axes = plt.subplots(3, 4, figsize=(8, 6))
    for ax in axes.flat:
        ax.axis('off')
    for ax, i in zip(axes.flat, ids):
        ax.imshow(x[i], cmap='gray'); ax.set_title(f'True {y[i]}, predicted {predicted[i]}')
    save(fig, 'errors.png')
