# ocr_test.py
import pytesseract
from PIL import Image
import sys
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


img_path = sys.argv[1]  # run: python ocr_test.py screenshot.png
img = Image.open(img_path)
text = pytesseract.image_to_string(img)
print("OCR output:\n", text)
