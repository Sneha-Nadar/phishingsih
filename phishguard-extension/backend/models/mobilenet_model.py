# backend/models/mobilenet_model.py

import torch
from torchvision import models, transforms
from PIL import Image

# Use GPU if available, else CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 1️⃣ Load pretrained MobileNetV3-Small (ImageNet weights)
model = models.mobilenet_v3_small(
    weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
)

# 2️⃣ Replace final layer → 2 classes (phishing / safe)
# Original final layer: Linear(1024, 1000)
model.classifier[3] = torch.nn.Linear(1024, 2)

model.to(DEVICE)
model.eval()

# 3️⃣ Image preprocessing pipeline
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],   # standard ImageNet normalization
        std=[0.229, 0.224, 0.225],
    ),
])

LABELS = ["phishing", "safe"]   # index 0 → phishing, 1 → safe


def predict_image(pil_img: Image.Image):
    """
    Takes a PIL image, returns phishing_prob, safe_prob and verdict.
    """
    img = pil_img.convert("RGB")
    tensor = transform(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    phishing_prob = float(probs[0])  # assuming index 0 = phishing
    safe_prob = float(probs[1])

    # Threshold can be tuned; 0.5 is simple and OK for demo
    verdict = "phishing" if phishing_prob >= 0.5 else "safe"

    return {
        "phishing_prob": phishing_prob,
        "safe_prob": safe_prob,
        "verdict": verdict,
    }
