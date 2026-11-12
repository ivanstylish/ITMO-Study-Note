"""Original IDX bytes; no dataset library is used."""
import gzip
import hashlib
from pathlib import Path
import struct
from urllib.request import urlopen
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
BASE = 'https://storage.googleapis.com/cvdf-datasets/mnist/'
FILES = {
    'train-images-idx3-ubyte.gz': 'f68b3c2dcbeaaa9fbdd348bbdeb94873',
    'train-labels-idx1-ubyte.gz': 'd53e105ee54ea40749a09fcbcd1e9432',
    't10k-images-idx3-ubyte.gz': '9fb629c4189551a2d022fa330f9573f3',
    't10k-labels-idx1-ubyte.gz': 'ec29112dd5afa0611ce80d1b7f02629c',
}


def download():
    DATA.mkdir(exist_ok=True)
    for name, digest in FILES.items():
        path = DATA / name
        if not path.exists():
            print('Downloading', name, flush=True)
            with urlopen(BASE + name, timeout=90) as response:
                content = response.read()
            if hashlib.md5(content).hexdigest() != digest:
                raise ValueError('Download checksum mismatch: ' + name)
            path.write_bytes(content)
        if hashlib.md5(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Invalid MNIST file: ' + str(path))


def read_idx(path):
    path = Path(path)
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    if len(raw) < 8:
        raise ValueError('Truncated IDX header.')
    magic, count = struct.unpack('>II', raw[:8])
    if magic == 2051:
        if len(raw) < 16:
            raise ValueError('Truncated image header.')
        rows, cols = struct.unpack('>II', raw[8:16])
        if (rows, cols) != (28, 28) or len(raw) != 16 + count * rows * cols:
            raise ValueError('Invalid IDX image dimensions or byte count.')
        return np.frombuffer(raw, np.uint8, offset=16).reshape(count, rows, cols)
    if magic == 2049:
        if len(raw) != 8 + count:
            raise ValueError('Invalid IDX label byte count.')
        labels = np.frombuffer(raw, np.uint8, offset=8)
        if (labels > 9).any():
            raise ValueError('MNIST labels must be between 0 and 9.')
        return labels
    raise ValueError('Unsupported IDX magic number.')


def load_data():
    download()
    arrays = [read_idx(DATA / name) for name in FILES]
    if [a.shape for a in arrays] != [(60000, 28, 28), (60000,), (10000, 28, 28), (10000,)]:
        raise ValueError('Unexpected MNIST dataset sizes.')
    x, y, xt, yt = arrays
    return x.astype(np.float32) / 255, y, xt.astype(np.float32) / 255, yt


def one_hot(y):
    return np.eye(10, dtype=np.float32)[y]
