import threading
import json
import os
import base64
import ollama
from .voicespeak import sync_speak, speak, gpt_sync_speak, gpt_wav, gpt_speak
from .utils import prompt_clear

CHAT_HISTORY = "tmp/chat_history.jsonl"
CHAT_HISTORY_MAX_LIMIT = 3 * 2 # 5 rounds of conversation
ollama_client = ollama.Client(
    "http://10.4.174.156:11434/",
)
speak_queue = {}
print(gpt_speak)
def gpt_async_speak(text, people, queue, index):
    result = gpt_sync_speak(text, people)
    queue[index] = result

def generate(prompt, model="gemma3:4b", new_chat=False, people="rencai"):
    threads_queue = []
    inx = 0
    spk_inx = 0
    spk_thread = None
    with open(CHAT_HISTORY, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > CHAT_HISTORY_MAX_LIMIT:
            lines = lines[-CHAT_HISTORY_MAX_LIMIT:]
        chat_history = [json.loads(line) for line in lines]
    if new_chat:
        chat_history = []
    chat_history.append({"role": "user", "content": prompt})
    print("chat_history:", chat_history)
    response = ""
    temp_response = ""
    for part_response in ollama_client.chat(
        model=model,
        messages=chat_history, 
        stream=True,
        options={
            "temperature": 0.2,
            "num_predict": 256,
        }, keep_alive=True):
        stream = part_response['message']['content']
        print(stream, end='', flush=True)
        response += stream
        temp_response += stream
        # 根据句号来进行分割
        if not gpt_speak:
            if temp_response.endswith(".") or temp_response.endswith("。") or temp_response.endswith("！") or temp_response.endswith("？"):
                threads_queue.append((threading.Thread(target=sync_speak, args=(temp_response,)), "created"))
                temp_response = ""
            if len(threads_queue) > 0:
                therad, status = threads_queue[0]
                if status == "created":
                    therad.start()
                    threads_queue[0] = (therad, "started")
                elif status == "started":
                    if not therad.is_alive():
                        threads_queue.pop(0)
                        if len(threads_queue) > 0:
                            threads_queue[0][0].start()
                            threads_queue[0] = (threads_queue[0][0], "started")
        else:
            if temp_response.endswith(".") or temp_response.endswith("。") or temp_response.endswith("！") or temp_response.endswith("？"):
                threading.Thread(target=gpt_async_speak, args=(prompt_clear(temp_response), people, speak_queue, inx)).start()
                inx += 1
                temp_response = ""
            if spk_inx in speak_queue:
                spk_thread = threading.Thread(target=gpt_wav, args=(speak_queue[spk_inx],))
                spk_thread.start()
                speak_queue.pop(spk_inx)
            if spk_thread and not spk_thread.is_alive():
                spk_inx += 1
                spk_thread = None            

        if part_response['done']:
            print("\nSpeed", part_response['eval_count']/part_response['eval_duration']*10**9, "tokens/s")


    if not gpt_speak:
        threads_queue.append((threading.Thread(target=sync_speak, args=(temp_response,)), "created"))
        while threads_queue:
            therad, status = threads_queue[0]
            if status == "created":
                therad.start()
                threads_queue[0] = (therad, "started")
            elif status == "started":
                if not therad.is_alive():
                    threads_queue.pop(0)
                    if len(threads_queue) > 0:
                        threads_queue[0][0].start()
                        threads_queue[0] = (threads_queue[0][0], "started")
    else:
        if len(prompt_clear(temp_response)) > 0:
            threading.Thread(target=gpt_async_speak, args=(prompt_clear(temp_response), people, speak_queue, inx)).start()
            inx += 1
        while spk_inx < inx:
            if spk_inx in speak_queue:
                spk_thread = threading.Thread(target=gpt_wav, args=(speak_queue[spk_inx],))
                spk_thread.start()
                speak_queue.pop(spk_inx)
            if spk_thread and not spk_thread.is_alive():
                spk_inx += 1
                spk_thread = None

    # Speak the final response
    with open(CHAT_HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps({"role": "user", "content": prompt}) + "\n")
        f.write(json.dumps({"role": "assistant", "content": response}) + "\n")
    return response

TASK_DESCRIPTION = """
You are a helpful desktop pet. 
You should try your best to serve me.
{}.
And I will provide you with a screenshot.
Please analyze the what I am doing and base on your understanding of me,
and my current feelings, please give me a response within 50 words.
Your response should not contains any information I have given you.
You should behave as if you are my friend and behave as we are just talking.
"""

EMOTION_PROMPT = { 
    0: "Please judge my current feelings",
    1: "My current feelings might be {}",
}

def scene_analyze(emotion, model="gemma3:4b"):
    image_base64 = tmp_picture_encode()
    if emotion == 'neutral':
        prompt = EMOTION_PROMPT[0]
    else:
        prompt = EMOTION_PROMPT[1].format(emotion)
    prompt = TASK_DESCRIPTION.format(prompt)
    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt, "images": [image_base64]},
        ],
        stream=False,
        options={
            "temperature": 0,
            "num_predict": 128,
        },
        keep_alive=True,
    )
    print(response['message']['content'])
    print("\nSpeed", response['eval_count']/response['eval_duration']*10**9, "tokens/s")
    sync_speak(response['message']['content'])
    return response["message"]["content"]

QUERY_PROMPT = """
You are a helpful desktop pet. 
You should try your best to serve me.
Please analyze what my current emotion is.
The possible emotions are:
surprise, angry, happy, sad, neutral.
If you don't know, please answer "neutral".
Only one of the words "surprise, angry, happy, sad, neutral" is allowed.
"""
emotion_types = ["neutral", "surprise", "angry", "happy", "sad", "neutral",]

def llm_emotion_query():
    image_base64 = tmp_picture_encode()
    response = ollama_client.chat(
        model="gemma3:4b",
        messages=[
            {"role": "user", "content": QUERY_PROMPT, "images": [image_base64]},
        ],
        stream=False,
        options={
            "temperature": 0.2,
            "num_predict": 128,
        },  
    )
    response = response['message']['content']
    for emotion in emotion_types:
        if emotion in response.lower():
            print("Emotion:", emotion)
            break
    return emotion


def tmp_picture_encode():
    with open("tmp/capture/capture_0.png", "rb") as f:
        image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64

if __name__ == "__main__":
    prompt = "请用50个字分析中国大陆能否攻下台湾"
    response = generate(prompt)

    emotion = "happy"
    response = scene_analyze(emotion)