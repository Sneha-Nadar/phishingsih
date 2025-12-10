# backend/models/mobilenet_model.py (FINAL VERSION)

import os
import torch
from torchvision import models, transforms
from PIL import Image

# --------------------------
# DEVICE
# --------------------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --------------------------
# MODEL WEIGHTS PATH
# --------------------------
BASE_DIR = os.path.dirname(__file__)
WEIGHTS_PATH = os.path.join(BASE_DIR, "mobilenet_weights.pth")

# --------------------------
# LOAD MODEL
# --------------------------
model = models.mobilenet_v3_small(
    weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
)

model.classifier[3] = torch.nn.Linear(1024, 2)

if os.path.exists(WEIGHTS_PATH):
    print(f"[INFO] Loading trained weights: {WEIGHTS_PATH}")
    state = torch.load(WEIGHTS_PATH, map_location=DEVICE)
    model.load_state_dict(state)
else:
    print("[WARNING] mobilenet_weights.pth not found! Using random weights.")

model.to(DEVICE)
model.eval()

# --------------------------
# IMAGE TRANSFORM (MUST MATCH TRAINING)
# --------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),   # SAME AS TRAINING
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

LABELS = ["phishing", "safe"]

# --------------------------
# PREDICT FUNCTION
# --------------------------
def predict_image(pil_img: Image.Image):
    img = pil_img.convert("RGB")
    tensor = transform(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    phishing_prob = float(probs[0])
    safe_prob = float(probs[1])
    verdict = "phishing" if phishing_prob > 0.5 else "safe"

    return {
        "phishing_prob": phishing_prob,
        "safe_prob": safe_prob,
        "verdict": verdict
    }
