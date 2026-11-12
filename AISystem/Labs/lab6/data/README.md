# MNIST 原始文件

任务书指定数据：https://www.kaggle.com/datasets/hojjatk/mnist-dataset 。
本实现从公开 CVDF 镜像获取同一原始 MNIST IDX gzip 文件：
https://storage.googleapis.com/cvdf-datasets/mnist/ 。无账号、无数据加载框架。

| 文件 | 解压后的内容 | 下载文件 MD5 |
|---|---|---|
| train-images-idx3-ubyte.gz | 60000×28×28 uint8 | f68b3c2dcbeaaa9fbdd348bbdeb94873 |
| train-labels-idx1-ubyte.gz | 60000 uint8 标签 | d53e105ee54ea40749a09fcbcd1e9432 |
| t10k-images-idx3-ubyte.gz | 10000×28×28 uint8 | 9fb629c4189551a2d022fa330f9573f3 |
| t10k-labels-idx1-ubyte.gz | 10000 uint8 标签 | ec29112dd5afa0611ce80d1b7f02629c |

原始 MNIST 作者为 Yann LeCun、Corinna Cortes、Christopher J. C. Burges。
校验用于识别文件内容和传输损坏，不将 MD5 用作安全认证。
data.py 自行解析大端 IDX 头，不调用 torchvision、keras 或其他现成加载器。
