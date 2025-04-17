import threading
import json
import base64
from ollama import Client
from .voicespeak import async_speak, speak

EMOTION_PROMPT = "You are a helpful desktop pet. You should try your best to serve me. Your owner is {}. You should use your word to share your owner's feelings" 
CHAT_HISTORY = "tmp/chat_history.jsonl"
CHAT_HISTORY_MAX_LIMIT = 3 * 2 # 5 rounds of conversation
client = Client(
    "http://localhost:11434/",
)

def generate(prompt, model="gemma3:4b", new_chat=False):
    threads_queue = []
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
    for part_response in client.chat(
        model=model,
        messages=chat_history, 
        stream=True,
        options={
            "temperature": 0.2,
            "num_predict": 512,
        }):
        stream = part_response['message']['content']
        print(stream, end='', flush=True)
        response += stream
        temp_response += stream
        # 根据句号来进行分割
        if temp_response.endswith(".") or temp_response.endswith("。") or temp_response.endswith("！") or temp_response.endswith("？"):
            threads_queue.append((threading.Thread(target=async_speak, args=(temp_response,)), "created"))
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

        if part_response['done']:
            print("\nSpeed", part_response['eval_count']/part_response['eval_duration']*10**9, "tokens/s")
    threads_queue.append((threading.Thread(target=async_speak, args=(temp_response,)), "created"))
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
    # Speak the final response
    with open(CHAT_HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps({"role": "user", "content": prompt}) + "\n")
        f.write(json.dumps({"role": "assistant", "content": response}) + "\n")
    return response

TASK_DESCRIPTION = """
You are a helpful desktop pet. 
You should try your best to serve me.
I will tell you my current feelings might be {}.
And I will provide you with a screenshot.
Please analyze the what I am doing and base on your understanding of me,
and my current feelings, please give me a response within 50 words.
Your response should not contains any information I have given you.
You should behave as if you are my friend and behave as we are just talking.
"""
def scene_analyze(emotion, model="gemma3:4b"):
    image_base64 = tmp_picture_encode()
    prompt = TASK_DESCRIPTION.format(emotion)
    response = client.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt, "images": [image_base64]},
        ],
        stream=False,
        options={
            "temperature": 0.2,
            "num_predict": 128,
        },  
    )
    print(response['message']['content'])
    print("\nSpeed", response['eval_count']/response['eval_duration']*10**9, "tokens/s")
    speak(response['message']['content'])
    return response["message"]["content"]

def tmp_picture_encode():
    with open("tmp/capture/capture_0.png", "rb") as f:
        image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64

if __name__ == "__main__":
    prompt = "她和楪祈谁强一点"
    response = generate(prompt)

    emotion = "开心"
    response = scene_analyze(emotion)