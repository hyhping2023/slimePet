# slimePet

## 首先是环境安装

1. 强烈建议运行前先安装conda，链接：https://www.anaconda.com/docs/getting-started/miniconda/install.
2. (如果安装了conda)运行，``conda create -n slimepet python=3.12 -y``, ``conda activate slimepet``
3. 运行``pip install -r requirements.txt``

## 接着是Ollama安装

1. 前往Ollama官网[](https://ollama.com/)下载对应系统的Ollama软件并安装
2. 打开终端，输入``ollama pull gemma3:4b``
3. 运行``ollama serve``

## 接下来是GPT-SoVITS的安装

可以参考[](https://github.com/RVC-Boss/GPT-SoVITS)里的文档根据系统版本自定义安装。也可以使用我们提供的安装包GPT-SoVITS-v4-20250422-nvidia50.zip(只可以在Windows下运行，Linux和macOS系统可以去官网下载，然后把整合包内的模型移动到安装文件夹下)，解压后运行go-webui.bat文件，在打开的网站下选择1-GPT-SoVITS-TTS选项，并在下方选择1C-推理，接下来选择"开TTS推理WebUI"。

## 运行说明

1. 首先强烈建议打开VPN，确保你能链接到谷歌服务器以确保语音识别模块正常运行，对于无法访问Google语音识别模块的电脑，如果你是Windows系统，暂时没有解决方案，对于Linux和macOS系统，这会有本地的语音识别服务。
2. 运行global.py文件前，请先确保ollama，GPT-SoVITS服务正常运行，对于跨节点访问，确保服务的监听地址包含127.0.0.1:port.
3. 运行前修改src/voicespeak.py和src/language_server.py下的url为服务节点的url
4. 无误后运行根目录下的global.py. `
