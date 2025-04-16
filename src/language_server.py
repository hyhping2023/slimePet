import requests
import json
import base64

EMOTION_PROMPT = "You are a helpful desktop pet. You should try your best to serve me. Your owner is {}. You should use your word to share your owner's feelings" 
CHAT_HISTORY = "tmp/chat_history.jsonl"
CHAT_HISTORY_MAX_LIMIT = 5 * 2 # 5 rounds of conversation

def generate(prompt):
    with open(CHAT_HISTORY, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) > CHAT_HISTORY_MAX_LIMIT:
            lines = lines[-CHAT_HISTORY_MAX_LIMIT:]
        chat_history = [json.loads(line) for line in lines]
    chat_history.append({"role": "user", "content": prompt})
    print("chat_history:", chat_history)
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "gemma3:1b",
        "messages": chat_history,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 128,
            "main_gpu": 1,
        }
    })
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None
    with open(CHAT_HISTORY, "a", encoding="utf-8") as f:
        f.write(json.dumps({"role": "user", "content": prompt}) + "\n")
        f.write(json.dumps({"role": "assistant", "content": response.json()['message']['content']}) + "\n")
    return response.json()['message']['content']

def scene_analyze():
    image_base64 = tmp_picture_encode()
    response = requests.post("http://localhost:11434/api/scene_analyze", json={
        
    })

def tmp_picture_encode():
    with open("tmp/capture/captrue_0.png", "rb") as f:
        image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return image_base64

if __name__ == "__main__":
    prompt = "请问神里绫华是谁"
    response = generate(prompt)
    print(response)