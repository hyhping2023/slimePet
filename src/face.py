from torchvision.models import swin_t
import torch
import sys, os, glob
import torch.nn as nn
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from torchvision import transforms
from PIL import Image


if sys.platform == "win32":
    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
elif sys.platform == "linux":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
elif sys.platform == "darwin":
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
else:
    raise NotImplementedError("Unsupported platform: {}".format(sys.platform))

print("Using device:", device)

types = {
    0: "surprise",
    1: "angry",
    2: "happy",
    3: "sad",
}

reversed_types = {
    "surprise": 0,
    "angry": 1,
    "happy": 2,
    "sad": 3,
}

model = swin_t().to(device)
model.head = nn.Linear(model.head.in_features, len(reversed_types)).to(device)  # 修改最后一层为7类
model.load_state_dict(torch.load("data/swint_best_model.pth", map_location=device))  # 加载模型参数
model.eval()
transform = transforms.Compose([
    transforms.Resize((48, 48)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])
confidence_threshold = 0.8

app = FastAPI()


@app.post('/')
def predict():
    images = glob.glob("tmp/capture/*.png")
    if len(images) == 0:
        return {"result": "No images found"}
    images = [Image.open(image_path).convert('RGB') for image_path in images]
    images = [transform(image).unsqueeze(0).to(device) for image in images]
    images = torch.cat(images, dim=0)
    with torch.no_grad():
        outputs = model(images)
        outputs = torch.softmax(outputs, dim=1)
        # 当输出的最大值大于置信度阈值时，才进行预测
        confidences = torch.max(outputs, dim=1).values.cpu().numpy()
        mask = confidences > confidence_threshold
        predictions = torch.argmax(outputs, dim=1).cpu().numpy()
        # 保留置信度大于阈值的预测结果
        predictions = predictions[mask].max(axis=0)
        return {"result": types[predictions] if len(predictions) > 0 else "No valid predictions"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

        