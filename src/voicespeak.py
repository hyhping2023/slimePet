import pyttsx3
import threading
import re
import sys
import multiprocessing as mp

def async_speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 250)
    engine.setProperty('volume', 1)
    voices = engine.getProperty('voices')
    if sys.platform == "win32":
        engine.setProperty('voice', voices[0].id)
    elif sys.platform == "darwin":
        if contains_chinese(text):
            for voice in voices:
                if "zh-CN" in voice.id:
                    engine.setProperty('voice', voice.id)
                    break
    elif sys.platform == "linux":
        engine.setProperty('voice', voices[0].id)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def check_language_support():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice.id)

def speak(text):
    if sys.platform == "win32":
        thread = threading.Thread(target=async_speak, args=(text,))
    elif sys.platform == "darwin":
        thread = mp.Process(target=async_speak, args=(text,))
    elif sys.platform == "linux":
        thread = mp.Process(target=async_speak, args=(text,))
    thread.start()
    return thread

def contains_chinese(text):
    # 使用正则表达式匹配中文字符
    pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(pattern.search(text))

if __name__ == "__main__":
    check_language_support()
    import time
    # speak("hello everyone")
    speak("我是稻妻城的神里绫华")
    for i in range(10):
        print(f'主线程计时{i}')
        time.sleep(1)
