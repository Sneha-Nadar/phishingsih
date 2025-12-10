import io
import torch
import torch.nn.functional as F
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from PIL import Image
# --- NEW IMPORTS (for OCR + YOLO + STEGO) ---
import numpy as np
import pytesseract
from ultralytics import YOLO
import cv2

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from models.mobilenet_model import predict_image as predict_image_mobilenet

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
# LOAD URL + TEXT MODELS (BERT)
# ---------------------------------------------------------
URL_MODEL = "imanoop7/bert-phishing-detector"
TEXT_MODEL = "ealvaradob/bert-finetuned-phishing"
yolo_model = YOLO("models/yolov8n.pt")

url_tokenizer = AutoTokenizer.from_pretrained(URL_MODEL)
url_model = AutoModelForSequenceClassification.from_pretrained(URL_MODEL).to(device)

text_tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL)
text_model = AutoModelForSequenceClassification.from_pretrained(TEXT_MODEL).to(device)

# ---------------------------------------------------------
# HELPER FOR BERT PREDICTIONS
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
# REQUEST MODELS (if you want JSON-based endpoints later)
# ---------------------------------------------------------
class URLRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    body: str

# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------
@app.get("/")
def home():
    return {"status": "backend running"}

# ---------------------------------------------------------
# URL ENDPOINT (BERT)
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
# TEXT / EMAIL ENDPOINT (BERT)
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
# IMAGE ENDPOINT (MobileNetV3 image model)
# ---------------------------------------------------------
@app.post("/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image, runs your trained MobileNetV3 model,
    and returns phishing_prob, safe_prob, and verdict.
    """
    img_bytes = await file.read()
    try:
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return {"error": "Invalid image file"}

    result = predict_image_mobilenet(pil_img)

    return {
        "phishing_prob": round(result["phishing_prob"] * 100, 2),
        "safe_prob": round(result["safe_prob"] * 100, 2),
        "verdict": result["verdict"],
    }
# ---------------------------------------------------------
# STEGO DETECTION FUNCTIONS
# ---------------------------------------------------------
def analyze_stego(image: Image.Image):
    img = np.array(image)

    # ENTROPY
    hist, _ = np.histogram(img.flatten(), bins=256, density=True)
    entropy = -np.sum(hist * np.log2(hist + 1e-10))

    # LSB CHECK
    bits = img & 1
    ones = int(np.sum(bits))
    zeros = bits.size - ones
    prop_diff = abs(ones - zeros) / (bits.size + 1e-10)

    # CHI-SQUARE TEST
    flat = img.flatten()
    observed_even = np.sum(flat % 2 == 0)
    observed_odd = flat.size - observed_even
    expected = flat.size / 2
    chi2 = ((observed_even - expected) ** 2 + (observed_odd - expected) ** 2) / expected

    suspicious = (
        entropy < 3.0 or
        prop_diff > 0.05 or
        chi2 > 10_000
    )

    return {
        "entropy": float(entropy),
        "lsb_prop_diff": float(prop_diff),
        "chi_square": float(chi2),
        "stego_detected": suspicious
    }
# ---------------------------------------------------------
# OCR FUNCTION
# ---------------------------------------------------------
def extract_text_ocr(image: Image.Image):
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except:
        return ""
# ---------------------------------------------------------
# YOLO PHISHING UI DETECTION
# ---------------------------------------------------------
def analyze_yolo(image: Image.Image):
    img = np.array(image)
    results = yolo_model.predict(img, imgsz=640)

    detections = []
    for r in results:
        if hasattr(r, "boxes"):
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                name = r.names.get(cls, "unknown")
                detections.append({"label": name, "confidence": conf})

    return detections
# ---------------------------------------------------------
# FULL IMAGE ANALYZER (OCR + YOLO + STEGO + MobileNet)
# ---------------------------------------------------------
@app.post("/analyze/image/full")
async def analyze_image_full(file: UploadFile = File(...)):
    img_bytes = await file.read()

    try:
        pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except:
        return {"error": "invalid image"}

    # 1️⃣ MobileNet phishing classifier
    mobilenet_result = predict_image_mobilenet(pil_img)

    # 2️⃣ OCR extraction
    ocr_text = extract_text_ocr(pil_img)

    # 3️⃣ YOLO phishing UI detection
    yolo_detections = analyze_yolo(pil_img)

    # 4️⃣ Steganography analysis
    stego_result = analyze_stego(pil_img)

    # Combined result
    return {
        "mobilenet": mobilenet_result,
        "ocr_text": ocr_text,
        "yolo_detections": yolo_detections,
        "stego_analysis": stego_result,
        "final_verdict": "suspicious" if (
            mobilenet_result["verdict"] == "phishing" or
            stego_result["stego_detected"] or
            len(yolo_detections) > 0
        ) else "safe"
    }

