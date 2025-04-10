import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import os
from pynput import keyboard
import threading

# 全局变量
storage_dir = "../tmp"
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)
file_dir = os.path.join(storage_dir, "voice.wav")
recording = False
frames = []
samplerate = 44100
channels = 1
dtype = 'int16'

def start_recording():
    global recording, frames
    recording = True
    frames = []
    print("开始录音...")

def stop_recording():
    global recording
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
            text = r.recognize_google(audio, language='en-US')
            print("识别结果：", text)
    except sr.UnknownValueError:
        print("无法识别的语音")
    except sr.RequestError:
        print("语音识别服务不可用")
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

def record_audio():
    global recording, frames
    with sd.InputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
        while True:
            if recording:
                data, overflowed = stream.read(int(samplerate * 0.1))
                frames.extend(data)

# 设置按键监听
def main():
    # 启动录音线程
    threading.Thread(target=record_audio, daemon=True).start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()