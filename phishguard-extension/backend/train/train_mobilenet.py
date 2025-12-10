# --------------------------------------------------
# train_mobilenet.py (FINAL VERSION — FULL MERGE)
# --------------------------------------------------

import os
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report


# --------------------------
# CONFIG
# --------------------------
DATASET_DIR = "datasets"
SAVE_PATH = "../models/mobilenet_weights.pth"

BATCH_SIZE = 16
EPOCHS = 10
LR = 1e-4
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Training on:", DEVICE)


# --------------------------
# SAFE PIL LOADER
# --------------------------
def safe_loader(path):
    try:
        img = Image.open(path)
        img = img.convert("RGB")
    except Exception as e:
        print("Unreadable image:", path, e)
        return Image.new("RGB", (224, 224))

    w, h = img.size
    if w < 20 or h < 20:
        print("Tiny/broken image:", path)
        return Image.new("RGB", (224, 224))

    return img


# --------------------------
# TRANSFORMS
# --------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------
# DATASET
# --------------------------
train_ds = datasets.ImageFolder(
    DATASET_DIR,
    loader=safe_loader,
    transform=transform
)

train_loader = DataLoader(
    train_ds,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

print("Classes:", train_ds.classes)
print("Total images:", len(train_ds))


# --------------------------
# MODEL
# --------------------------
model = models.mobilenet_v3_small(
    weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
)

model.classifier[3] = nn.Linear(1024, 2)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)


# --------------------------
# TRACK LOSS & ACCURACY
# --------------------------
history_loss = []
history_acc = []


# --------------------------
# TRAINING LOOP
# --------------------------
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for imgs, labels in train_loader:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)

        optimizer.zero_grad()
        preds = model(imgs)
        loss = criterion(preds, labels)

        if torch.isnan(loss) or torch.isinf(loss):
            print("Skipping corrupted batch")
            continue

        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        correct += (preds.argmax(1) == labels).sum().item()
        total += labels.size(0)

    epoch_loss = total_loss
    epoch_acc = correct / total

    history_loss.append(epoch_loss)
    history_acc.append(epoch_acc)

    print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {epoch_loss:.4f}, Acc: {epoch_acc:.4f}")


# --------------------------
# SAVE WEIGHTS
# --------------------------
torch.save(model.state_dict(), SAVE_PATH)
print("Training complete! Saved:", SAVE_PATH)


# --------------------------
# PLOT LOSS & ACCURACY
# --------------------------
plt.figure(figsize=(8, 4))
plt.plot(history_loss, label="Loss", color="red")
plt.plot(history_acc, label="Accuracy", color="green")
plt.xlabel("Epoch")
plt.title("Training Loss & Accuracy")
plt.grid(True)
plt.legend()
plt.show()


# --------------------------
# CONFUSION MATRIX + METRICS
# --------------------------
print("\n[INFO] Running evaluation and generating confusion matrix...")

model.eval()
all_labels = []
all_preds = []

with torch.no_grad():
    for imgs, labels in train_loader:   # Replace with val_loader if you add validation
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        outputs = model(imgs)
        preds = outputs.argmax(1)

        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())

all_labels = np.array(all_labels)
all_preds = np.array(all_preds)


# CONFUSION MATRIX
cm = confusion_matrix(all_labels, all_preds)
class_names = ["Phishing", "Safe"]

plt.figure(figsize=(6, 5))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title("Confusion Matrix", fontsize=16)
plt.colorbar()

tick_marks = np.arange(len(class_names))
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)

thresh = cm.max() / 2.0
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(
            j, i, str(cm[i, j]),
            ha="center",
            color="white" if cm[i, j] > thresh else "black",
            fontsize=12
        )

plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.show()


# PRINT METRICS
print("\nClassification Report:")
print(classification_report(all_labels, all_preds, target_names=class_names))


# # --------------------------
# # MATPLOTLIB PLOTS
# # --------------------------
# plt.figure(figsize=(8,4))
# plt.plot(history_loss, label="Loss", color="red")
# plt.plot(history_acc, label="Accuracy", color="green")
# plt.legend()
# plt.title("Training Loss & Accuracy")
# plt.xlabel("Epoch")
# plt.grid(True)
# plt.show()
# ---------------------------------------
# EVALUATION + CONFUSION MATRIX PLOTTING
# ---------------------------------------
