import json
import numpy as np
from .layers import Linear, ReLU, Flatten, Dropout


class Network:
    def __init__(self, widths, dropout=0.0, seed=42):
        self.widths, self.dropout, self.seed = list(widths), dropout, seed
        rng = np.random.default_rng(seed)
        self.layers = [Flatten()]
        for i, (inputs, outputs) in enumerate(zip(widths[:-1], widths[1:])):
            self.layers.append(Linear(inputs, outputs, rng))
            if i < len(widths) - 2:
                self.layers.append(ReLU())
                if dropout:
                    self.layers.append(Dropout(dropout, rng))

    def forward(self, x, training=False):
        for layer in self.layers:
            x = layer.forward(x, training)
        return x

    def backward(self, dy):
        for layer in reversed(self.layers):
            dy = layer.backward(dy)
        return dy

    def parameters(self):
        for layer in self.layers:
            if isinstance(layer, Linear):
                yield layer.W, layer.dW
                yield layer.b, layer.db

    def save(self, path):
        values = {}
        for i, layer in enumerate(l for l in self.layers if isinstance(l, Linear)):
            values[f'W{i}'], values[f'b{i}'] = layer.W, layer.b
        metadata = dict(widths=self.widths, dropout=self.dropout, seed=self.seed)
        np.savez(path, metadata=json.dumps(metadata), **values)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as values:
            model = cls(**json.loads(str(values['metadata'])))
            for i, layer in enumerate(l for l in model.layers if isinstance(l, Linear)):
                for name in ('W', 'b'):
                    source, target = values[f'{name}{i}'], getattr(layer, name)
                    if source.shape != target.shape or not np.isfinite(source).all():
                        raise ValueError('Invalid saved weights.')
                    target[:] = source
        return model


class Adam:
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.lr, self.beta1, self.beta2, self.eps = lr, beta1, beta2, eps
        self.t, self.states = 0, []

    def step(self, parameters):
        pairs = list(parameters)
        if not self.states:
            self.states = [(np.zeros_like(p), np.zeros_like(p)) for p, _ in pairs]
        self.t += 1  # One time step per mini-batch, not per parameter.
        for (p, g), (m, v) in zip(pairs, self.states):
            m[:] = self.beta1 * m + (1 - self.beta1) * g
            v[:] = self.beta2 * v + (1 - self.beta2) * g * g
            m_hat = m / (1 - self.beta1 ** self.t)
            v_hat = v / (1 - self.beta2 ** self.t)
            p -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
