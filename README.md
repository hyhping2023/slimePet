# slimePet

## 首先是环境安装

1. 强烈建议运行前先安装conda，链接：https://www.anaconda.com/docs/getting-started/miniconda/install.
2. (如果安装了conda)运行，``conda create -n slimepet python=3.12 -y``, ``conda activate slimepet``
3. 运行``pip install -r requirements.txt``

## 接着是Ollama安装

1. 前往Ollama官网下载对应系统的Ollama软件并安装
2. 打开终端，输入``ollama pull gemma3:4b``
3. 运行``ollama serve``

## 运行说明

1. 首先强烈建议打开VPN，确保你能链接到谷歌服务器以确保语音识别模块正常运行，对于无法访问Google语音识别模块的电脑，如果你是Windows系统，暂时没有解决方案，对于Linux和macOS系统，这会有本地的语音识别服务。
2. 运行global.py文件前，请先确保ollama服务正常运行
