import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
from pynput import keyboard
import threading
import logging


# 全局变量
storage_dir = os.getcwd().split("slimePet")[0] + "slimePet" + os.sep + "tmp" + os.sep
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
file_dir = os.path.join(storage_dir, "voice.wav")
tmp_dir = os.path.join(storage_dir, "tmp.txt")
recording = False
frames = []
samplerate = 44100
channels = 1
dtype = 'int16'
model = None

def start_recording():
    global recording, frames
    recording = True
    frames = []
    print("开始录音...")

def stop_recording():
    global recording, model
    recording = False
    print("录音结束，正在识别...")
    # 将录音数据转换为适合识别的格式
    audio_data = np.array(frames, dtype=np.int16)
    # 保存到临时文件
    sf.write(file_dir, audio_data, samplerate)
    # 进行语音识别
    try:
        r = sr.Recognizer()
        with sr.AudioFile(file_dir) as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language='zh-CN')
            write_to_file(text)
            # print("识别结果：", text)
    except sr.UnknownValueError:
        print("无法识别的语音")
    except sr.RequestError:
        if os.name == 'nt':
            print("语音识别服务不可用")
        else:
            import whisper
            print("语音识别服务不可用，使用本地服务")
            if model is None:
                model = whisper.load_model("tiny")
            result = model.transcribe(file_dir)
            write_to_file(result['text'])
            print("本地识别结果：", result['text'])
    finally:
        # 删除临时文件
        if os.path.exists(file_dir):
            os.remove(file_dir)

def on_press(key):
    global recording
    if key == keyboard.Key.space and not recording:
        start_recording()
    elif key == keyboard.Key.space and recording:
        stop_recording()
    if key == keyboard.Key.esc:
        exit()
    try:
        if key.char.lower() == 'q':  # 新增Q键退出
            os._exit(0)
    except AttributeError:
        pass
    # ...原有空格键处理...

def write_to_file(data:str):
    with open(tmp_dir, "w") as f:
        f.write(data)

def record_audio():
    global recording, frames
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while True:
            if recording:
                data, overflowed = stream.read(int(samplerate * 0.1))
                frames.extend(data)

# 设置按键监听
def voice_control_thread():
    # 启动录音线程
    logging.info("You can use the SPACE key to start/stop recording. And ESC to exit.")
    threading.Thread(target=record_audio, daemon=True).start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    voice_control_thread()