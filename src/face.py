from torchvision.models import swin_s
import os, glob
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
from torch.nn.utils.rnn import pad_sequence
from tqdm import tqdm

# 定义数据集类
class FacialExpressionDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = os.listdir(root_dir)
        self.image_paths = []
        self.labels = []
        self.types = {}
        for label, class_name in enumerate(self.classes):
            class_dir = os.path.join(root_dir, class_name)
            for file_name in os.listdir(class_dir):
                self.image_paths.append(os.path.join(class_dir, file_name))
                self.labels.append(label)
            self.types[label] = class_name

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        label = self.labels[idx]
        if self.transform:
            image = self.transform(image)
        return image, label

# 数据预处理
transform = transforms.Compose([
    transforms.Resize((299, 299)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载数据集
train_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/train', transform=transform)
test_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/test', transform=transform)
val_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/valid', transform=transform)

# 创建数据加载器
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

device = 'mps'
model = swin_s(pretrained=True).to(device)
optimizer = optim.SGD(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# 训练模型
num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    for images, labels in tqdm(train_loader):
        # 假设每个batch是一个序列，这里简单地将每个图像视为一个时间步
        optimizer.zero_grad()
        outputs = model(images.to(device))
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    for images, labels in val_loader:
        images = images.to(device)
        outputs = model(images)
        accuracy = (outputs.argmax(dim=1) == labels).float().mean()
        print(f'Validation Accuracy: {accuracy:.4f}')

# 评估模型
model.eval()
with torch.no_grad():
    correct = 0
    total = 0
    for images, labels in test_loader:
        images = images.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    print(f'Accuracy: {100 * correct / total:.2f}%')

types = {
    1: "angry",
    2: "disgust",
    3: "fear",
    4: "happy",
    5: "neutral",
    6: "sad",
    7: "surprise",
}

        