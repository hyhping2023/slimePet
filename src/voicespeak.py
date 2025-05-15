import pyttsx3
import threading
# import re
import sys
import os
# import glob
import logging
# import tempfile
from shutil import copyfile
import multiprocessing as mp
from pydub import AudioSegment
from pydub.playback import play 
from functools import partial
from .utils import language_detect, contains_chinese, empty_remove
from .config import AVAIABLE_VOICES

now_dir = os.getcwd()
tmp_dir = os.path.join(now_dir, "tmp", 'voice')
os.environ['TMPDIR'] = tmp_dir
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

_voice_initialized = False
gpt_speak=False
client=None 
def initialize_voice():
    global _voice_initialized, gpt_speak, client 
    if _voice_initialized: 
        return
    
    try:
        from gradio_client import Client
        client = Client("http://10.4.174.156:9872/", 
                      download_files=os.path.join(os.getcwd(), "tmp", 'voice'),
                      timeout=5)  # 添加超时
        client.predict(api_name="/change_choices")
        gpt_speak = True
    except Exception as e:
        logging.warning(f"GPT服务器不可用: {e}")
        gpt_speak = False
        client = None
    finally:
        _voice_initialized = True

def change_voice(name):
    if not _voice_initialized:
        initialize_voice()
    if name not in AVAIABLE_VOICES:
        logging.warning(f"Invalid voice name: {name}. Available voices are: {', '.join(AVAIABLE_VOICES.keys())}")
        return
    if gpt_speak:  # 只有在GPT语音可用时才尝试改变权重
        try:
            change_weights(name)
            logging.info(f"Voice changed to: {name}")
        except NameError:  # 如果change_weights未定义
            logging.warning("GPT语音服务器不可用，无法改变语音权重")

def check_gpt_server():
    global client 
    if client is None:  # 首先检查client是否为None
        return False
    try:
        client.predict(api_name="/change_choices")
        return True
    except Exception as e:
        logging.error(f"Error connecting to GPT server: {e}")
        return False

    
if not gpt_speak:
    def sync_speak(text, SPEAKER=None):
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

    def speak(text, SPEAKER=None):
        if sys.platform == "win32":
            thread = threading.Thread(target=sync_speak, args=(text, ))
        elif sys.platform == "darwin":
            thread = mp.Process(target=sync_speak, args=(text, ))
        elif sys.platform == "linux":
            thread = mp.Process(target=sync_speak, args=(text, ))
        thread.start()
        return thread
    def gpt_sync_speak(text, SPEAKER='rencai'):
        """GPT同步语音合成的默认回退实现"""
        sync_speak(text, SPEAKER)

else:
    predict = partial(client.predict, 
        # ref_wav_path=file('/Users/hyhping/Music/people/rencai.wav'),
		prompt_text="",
		# prompt_language="日文",
		# text="黄烨华喜欢杨心选，但是杨心选喜欢的是黄烨华的好朋友新能源，但是新能源喜欢司空镇",
		# text_language="中文",
		how_to_cut="凑四句一切",
		top_k=15,
		top_p=1,
		temperature=1,
		ref_free=False,
		speed=1,
		if_freeze=False,
		inp_refs=None,
		sample_steps="32",
		if_sr=False,
		pause_second=0.3,
		api_name="/get_tts_wav")
    
    def sync_speak(text, SPEAKER='rencai'):
        result = predict(
            text=text,
            ref_wav_path=handle_file(AVAIABLE_VOICES[SPEAKER]["ref-wav"]),
            prompt_language=AVAIABLE_VOICES[SPEAKER]["language"],
            text_language=language_detect(text),
        )
        gpt_wav(result)

    def speak(text, SPEAKER=None):
        if sys.platform == "win32":
            thread = threading.Thread(target=sync_speak, args=(text, SPEAKER,))
        elif sys.platform == "darwin":
            thread = mp.Process(target=sync_speak, args=(text,SPEAKER,))
        elif sys.platform == "linux":
            thread = mp.Process(target=sync_speak, args=(text,SPEAKER,))
        thread.start()
        return thread

    change_sovit_weight = partial(client.predict, api_name="/change_sovits_weights")
    change_gpt_weight = partial(client.predict, api_name="/change_gpt_weights")

    def change_weights(SPEAKER):
        if SPEAKER not in AVAIABLE_VOICES:
            logging.warning(f"Invalid voice name: {SPEAKER}. Available voices are: {', '.join(AVAIABLE_VOICES.keys())}")
        change_gpt_weight(gpt_path=AVAIABLE_VOICES[SPEAKER]["gpt-weight"])
        change_sovit_weight(sovits_path=AVAIABLE_VOICES[SPEAKER]["sovit-weight"])

    def gpt_sync_speak(text, SPEAKER='rencai'):
        if SPEAKER not in AVAIABLE_VOICES:
            logging.warning(f"Invalid voice name: {SPEAKER}. Available voices are: {', '.join(AVAIABLE_VOICES.keys())}")
        result = predict(
            text=text,
            ref_wav_path=handle_file(AVAIABLE_VOICES[SPEAKER]["ref-wav"]),
            prompt_language=AVAIABLE_VOICES[SPEAKER]["language"],
            text_language=language_detect(text),
        )
        return result

def gpt_wav(file_dir):
    # 播放音频
    # 读取音频文件
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(file_dir, winsound.SND_FILENAME)
    else:
        song = AudioSegment.from_wav(file_dir)
        play(song)
    os.remove(file_dir)

if __name__ == "__main__":
    # playsound("/Users/hyhping/Music/people/rencai.wav")
    # print(result)
    # playsound(result)
    
    change_weights("rencai")
    result1 = predict(
        text="黄烨华喜欢杨心选，但是杨心选喜欢的是黄烨华的好朋友新能源，但是新能源喜欢司空镇",
        ref_wav_path=handle_file(AVAIABLE_VOICES["rencai"]["ref-wav"]),
        prompt_language=AVAIABLE_VOICES["rencai"]["language"],
        text_language="中文",
    )
    change_weights("486")
    result2 = predict(
        text="黄烨华喜欢杨心选，但是杨心选喜欢的是黄烨华的好朋友新能源，但是新能源喜欢司空镇",
        ref_wav_path=handle_file(AVAIABLE_VOICES["486"]["ref-wav"]),
        prompt_language=AVAIABLE_VOICES["486"]["language"],
        text_language="中文",
    )
    song = AudioSegment.from_wav(result1)
    gpt_wav(result1)
    song = AudioSegment.from_wav(result2)
    gpt_wav(result2)
    # 删除临时文件
    os.remove(result1)
    os.remove(result2)

    # check_language_support()
    # import time
    # # speak("hello everyone")
    # speak("我是稻妻城的神里绫华")
    # for i in range(10):
    #     print(f'主线程计时{i}')
    #     time.sleep(1)
