import struct
import tempfile
from pathlib import Path
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from mnist_lab.layers import Linear, ReLU, Flatten, Dropout, SoftmaxWithLoss
from mnist_lab.model import Network, Adam
from mnist_lab.data import read_idx, one_hot
from mnist_lab.inference import preprocess_image
from mnist_lab.training import train_epoch, evaluate


class Checks(unittest.TestCase):
    def test_linear_gradient(self):
        rng = np.random.default_rng(2)
        layer = Linear(3, 2, rng)
        layer.W = layer.W.astype(float); layer.b = layer.b.astype(float)
        x, dy = rng.normal(size=(4, 3)), rng.normal(size=(4, 2))
        layer.forward(x)
        dx = layer.backward(dy)
        for values, analytic in ((x, dx), (layer.W, layer.dW), (layer.b, layer.db)):
            numeric = np.zeros_like(values)
            for index in np.ndindex(values.shape):
                old = values[index]
                values[index] = old + 1e-5
                plus = (layer.forward(x) * dy).sum()
                values[index] = old - 1e-5
                minus = (layer.forward(x) * dy).sum()
                values[index] = old
                numeric[index] = (plus - minus) / 2e-5
            np.testing.assert_allclose(analytic, numeric, atol=1e-8)

    def test_network_gradient(self):
        model = Network([3, 4, 10])
        for layer in model.layers:
            if isinstance(layer, Linear):
                layer.W = layer.W.astype(float); layer.b = layer.b.astype(float) + 0.2
        x = np.array([[0.2, -0.4, 0.6], [0.9, 0.7, -0.1]])
        targets, criterion = one_hot(np.array([2, 5])), SoftmaxWithLoss()
        criterion.forward(model.forward(x), targets)
        model.backward(criterion.backward())
        for parameter, gradient in model.parameters():
            numeric = np.zeros_like(parameter)
            for index in np.ndindex(parameter.shape):
                old = parameter[index]
                parameter[index] = old + 1e-5
                plus = criterion.forward(model.forward(x), targets)
                parameter[index] = old - 1e-5
                minus = criterion.forward(model.forward(x), targets)
                parameter[index] = old
                numeric[index] = (plus - minus) / 2e-5
            np.testing.assert_allclose(gradient, numeric, atol=1e-8)

    def test_stable_loss(self):
        loss = SoftmaxWithLoss()
        value = loss.forward(np.array([[10000., -10000., 0.]]), np.array([[0., 1., 0.]]))
        self.assertEqual(value, 20000.)
        np.testing.assert_allclose(loss.backward(), [[1, -1, 0]])

    def test_relu_flatten(self):
        relu, flatten = ReLU(), Flatten()
        x = np.array([[[-2., 0., 3.]]])
        np.testing.assert_array_equal(relu.forward(x), [[[0, 0, 3]]])
        np.testing.assert_array_equal(relu.backward(np.ones_like(x)), [[[0, 0, 1]]])
        self.assertEqual(flatten.forward(x).shape, (1, 3))
        self.assertEqual(flatten.backward(np.ones((1, 3))).shape, x.shape)

    def test_dropout(self):
        layer, x = Dropout(0.25, np.random.default_rng(42)), np.ones((200, 300))
        output = layer.forward(x, True)
        self.assertAlmostEqual(float(output.mean()), 1, delta=0.015)
        np.testing.assert_array_equal(layer.backward(x), output)
        np.testing.assert_array_equal(layer.forward(x), x)
        np.testing.assert_array_equal(layer.backward(x), x)
        with self.assertRaises(ValueError): Dropout(1, np.random.default_rng())

    def test_adam_two_steps(self):
        p, q = np.array([1.]), np.array([2.])
        opt = Adam()
        opt.step([(p, np.array([2.])), (q, np.array([-3.]))])
        np.testing.assert_allclose(p, [0.999]); np.testing.assert_allclose(q, [2.001])
        opt.step([(p, np.array([4.])), (q, np.array([-3.]))])
        m, v = 0.9 * 0.2 + 0.1 * 4, 0.999 * 0.004 + 0.001 * 16
        expected = 0.999 - 0.001 * (m / (1-0.9**2)) / (np.sqrt(v / (1-0.999**2)) + 1e-8)
        np.testing.assert_allclose(p, [expected]); np.testing.assert_allclose(q, [2.002])
        self.assertEqual(opt.t, 2)

    def test_idx(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'sample.idx'
            p.write_bytes(struct.pack('>IIII', 2051, 1, 28, 28) + bytes(784))
            self.assertEqual(read_idx(p).shape, (1, 28, 28))
            p.write_bytes(struct.pack('>II', 2049, 2) + bytes([0, 9]))
            np.testing.assert_array_equal(read_idx(p), [0, 9])
            for raw in (b'', struct.pack('>II', 2049, 1)+bytes([10]), struct.pack('>II', 42, 0),
                        struct.pack('>IIII', 2051, 1, 28, 28)+bytes(783)):
                p.write_bytes(raw)
                with self.assertRaises(ValueError): read_idx(p)

    def test_save_reload(self):
        model, x = Network([784, 16, 10], 0.2), np.ones((2, 28, 28), np.float32)
        before = model.forward(x).copy()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'model.npz'
            model.save(path)
            np.testing.assert_array_equal(Network.load(path).forward(x), before)

    def test_preprocessing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'off center.png'
            image = Image.new('L', (150, 100), 'white')
            draw = ImageDraw.Draw(image); draw.line([(20, 15), (20, 60), (40, 60)], fill=0, width=7)
            image.save(path); a = preprocess_image(path)
            ImageOps.invert(image).save(path); b = preprocess_image(path)
            np.testing.assert_array_equal(a, b)
            self.assertEqual(a.shape, (28, 28)); self.assertTrue(0 <= a.min() <= a.max() <= 1)
            yy, xx = np.indices(a.shape)
            self.assertAlmostEqual(float((a*xx).sum()/a.sum()), 13.5, delta=0.6)
            self.assertAlmostEqual(float((a*yy).sum()/a.sum()), 13.5, delta=0.6)
            Image.new('L', (80, 80), 'white').save(path)
            with self.assertRaises(ValueError): preprocess_image(path)

    def test_training_learns(self):
        rng = np.random.default_rng(5)
        x = rng.normal(size=(40, 3)).astype(np.float32)
        y = (x[:, 0] > 0).astype(int)
        model, opt = Network([3, 8, 10]), Adam(lr=0.02)
        initial, _, _ = evaluate(model, x, y)
        for _ in range(25): train_epoch(model, opt, x, y, rng, batch=10)
        final, accuracy, _ = evaluate(model, x, y)
        self.assertLess(final, initial / 3); self.assertGreaterEqual(accuracy, 0.9)


if __name__ == '__main__':
    unittest.main()
