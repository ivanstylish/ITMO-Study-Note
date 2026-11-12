"""Each backward receives the gradient of the scalar loss."""
import numpy as np


class Linear:
    def __init__(self, inputs, outputs, rng):
        self.W = (rng.standard_normal((inputs, outputs)) * np.sqrt(2 / inputs)).astype(np.float32)
        self.b = np.zeros(outputs, dtype=np.float32)

    def forward(self, x, training=False):
        self.x = x
        return x @ self.W + self.b

    def backward(self, dy):
        self.dW = self.x.T @ dy
        self.db = dy.sum(axis=0)
        return dy @ self.W.T


class ReLU:
    def forward(self, x, training=False):
        self.positive = x > 0
        return np.maximum(x, 0)

    def backward(self, dy):
        return dy * self.positive


class Flatten:
    def forward(self, x, training=False):
        self.shape = x.shape
        return x.reshape(len(x), -1)

    def backward(self, dy):
        return dy.reshape(self.shape)


class Dropout:
    def __init__(self, rate, rng):
        if not 0 <= rate < 1:
            raise ValueError('Dropout rate must be in [0, 1).')
        self.rate, self.rng = rate, rng

    def forward(self, x, training=False):
        self.mask = ((self.rng.random(x.shape) >= self.rate) / (1 - self.rate)).astype(x.dtype) if training else np.ones_like(x)
        return x * self.mask

    def backward(self, dy):
        return dy * self.mask


class SoftmaxWithLoss:
    def forward(self, logits, targets):
        shifted = logits - logits.max(axis=1, keepdims=True)
        log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
        self.probs, self.targets = np.exp(log_probs), targets
        return float(-(targets * log_probs).sum() / len(logits))

    def backward(self):
        return (self.probs - self.targets) / len(self.targets)
