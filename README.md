# slimePet

## 首先是环境安装

1. 强烈建议运行前先安装conda，链接：https://www.anaconda.com/docs/getting-started/miniconda/install.
2. (如果安装了conda)运行，``conda create -n slimepet python=3.12 -y``, ``conda activate slimepet``
3. 运行``pip install -r requirements.txt``

## 接着是Ollama安装

1. 前往Ollama官网下载对应系统的Ollama软件并安装
2. 打开终端，输入``ollama pull qwen2.5:0.5b``
3. 运行``ollama serve``
