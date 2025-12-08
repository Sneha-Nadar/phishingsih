import io
import torch
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from PIL import Image

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torchvision import models, transforms

# ---------------------------------------------------------
# DEVICE
# ---------------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(title="PhishGuard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# LOAD URL + TEXT MODELS (NO CHANGE)
# ---------------------------------------------------------
URL_MODEL = "imanoop7/bert-phishing-detector"
TEXT_MODEL = "ealvaradob/bert-finetuned-phishing"

url_tokenizer = AutoTokenizer.from_pretrained(URL_MODEL)
url_model = AutoModelForSequenceClassification.from_pretrained(URL_MODEL).to(device)

text_tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL)
text_model = AutoModelForSequenceClassification.from_pretrained(TEXT_MODEL).to(device)

# ---------------------------------------------------------
# HELPER FOR BERT PREDICTIONS (NO CHANGE)
# ---------------------------------------------------------
def predict_phish(text: str, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=1)[0]

    # find phishing class index dynamically
    label_map = model.config.id2label
    phish_idx = 1
    for i, lbl in label_map.items():
        if "phish" in lbl.lower():
            phish_idx = i

    score = float(probs[phish_idx])
    verdict = "phishing" if score > 0.6 else "safe"
    return score, verdict


# ---------------------------------------------------------
# 📌 ADDED — IMAGE CLASSIFIER (MobileNetV3)
# ---------------------------------------------------------
# Load pretrained MobileNetV3-Small (ImageNet weights)
img_model = models.mobilenet_v3_small(
    weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
)
img_model.classifier[3] = torch.nn.Linear(1024, 2)
img_model.to(device)
img_model.eval()

# Image transforms
img_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

def predict_image_mobilenet(pil_img: Image.Image):
    img = pil_img.convert("RGB")
    tensor = img_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = img_model(tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    phishing_prob = float(probs[0])
    verdict = "phishing" if phishing_prob > 0.5 else "safe"

    return phishing_prob, verdict


# ---------------------------------------------------------
# URL ENDPOINT (NO CHANGE)
# ---------------------------------------------------------
@app.post("/analyze/url")
async def analyze_url(url: str = Form(...)):
    score, verdict = predict_phish(url, url_tokenizer, url_model)
    return {
        "url": url,
        "score": round(score * 100),
        "verdict": verdict,
    }


# ---------------------------------------------------------
# TEXT ENDPOINT (NO CHANGE)
# ---------------------------------------------------------
@app.post("/analyze/text")
async def analyze_text(body: str = Form(...)):
    score, verdict = predict_phish(body, text_tokenizer, text_model)
    return {
        "text": body,
        "score": round(score * 100),
        "verdict": verdict,
    }


# ---------------------------------------------------------
# 📌 IMAGE ENDPOINT (ADDED — FULL IMAGE SCAN)
# ---------------------------------------------------------
@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    img_bytes = await file.read()
    pil_img = Image.open(io.BytesIO(img_bytes))

    # 1️⃣ Image ML model (MobileNetV3)
    img_score, img_verdict = predict_image_mobilenet(pil_img)

    # 2️⃣ OCR extraction (OPTIONAL but safer)
    try:
        import easyocr
        ocr_reader = easyocr.Reader(["en"], gpu=False)
        extracted_text = " ".join(ocr_reader.readtext(img_bytes, detail=0))
    except:
        extracted_text = ""

    # 3️⃣ Text model applied on OCR text (fallback)
    if extracted_text.strip():
        text_score, text_verdict = predict_phish(extracted_text, text_tokenizer, text_model)
    else:
        text_score, text_verdict = 0.0, "safe"

    # Final fusion
    final_verdict = "phishing" if (img_verdict == "phishing" or text_verdict == "phishing") else "safe"
    final_score = max(img_score, text_score)

    return {
        "ocr_text": extracted_text,
        "image_model_score": round(img_score * 100),
        "text_model_score": round(text_score * 100),
        "final_score": round(final_score * 100),
        "verdict": final_verdict,
    }


@app.get("/")
def home():
    return {"status": "backend running"}
