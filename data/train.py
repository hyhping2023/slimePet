from torchvision.models import swin_t, swin_s, swin_b, resnet50, mobilenet_v3_small
import os, glob
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
from torch.nn.utils.rnn import pad_sequence
from tqdm import tqdm

if sys.platform == "win32":
    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
elif sys.platform == "linux":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
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

# 定义数据集类
class FacialExpressionDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = os.listdir(root_dir)
        self.image_paths = []
        self.labels = []
        self.types = {}
        for class_name in self.classes:
            if class_name not in reversed_types:
                continue
            class_dir = os.path.join(root_dir, class_name)
            label = reversed_types[class_name]
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
    # transforms.Resize((299, 299)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# 加载数据集
train_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/train', transform=transform)
test_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/test', transform=transform)
val_dataset = FacialExpressionDataset(root_dir='data/MMAFEDB/valid', transform=transform)

# 创建数据加载器
batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

# model = resnet50(pretrained=True).to(device)
# model.fc = nn.Linear(model.fc.in_features, len(reversed_types)).to(device)  # 修改最后一层为7类

# model = mobilenet_v3_small(pretrained=True).to(device)
# model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(reversed_types)).to(device)  # 修改最后一层为7类

model = swin_t(pretrained=True).to(device)
model.head = nn.Linear(model.head.in_features, len(reversed_types)).to(device)  # 修改最后一层为7类

optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
criterion = nn.CrossEntropyLoss()

# 训练模型
num_epochs = 100
best = 0
for epoch in range(num_epochs):
    model.train()
    for images, labels in tqdm(train_loader):
        # 假设每个batch是一个序列，这里简单地将每个图像视为一个时间步
        optimizer.zero_grad()
        outputs = model(images.to(device))
        labels = labels.to(device)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
    correct = 0
    total = 0
    for images, labels in val_loader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        # 计算全部的正确率
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    acc = 100 * correct / total
    print(f'Accuracy: {acc:.2f}%')
    if acc > best:
        best = acc
        torch.save(model.state_dict(), 'swint_best_model.pth')
    

# 评估模型
model.eval()
with torch.no_grad():
    correct = 0
    total = 0
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    print(f'Accuracy: {100 * correct / total:.2f}%')



if __name__ == "__main__":
    # 这里可以添加一些测试代码，比如加载模型，进行预测等
    pass

        