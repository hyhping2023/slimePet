import requests

def generate(prompt):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:0.5b",
        "prompt": prompt,
        "stream": False
    })
    return response.json()['response']

if __name__ == "__main__":
    prompt = "请问神里绫华是谁"
    response = generate(prompt)
    print(response)