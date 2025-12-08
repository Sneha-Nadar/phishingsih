import requests
import io
from PIL import Image, ImageDraw, ImageFont

# CONFIGURATION
API_URL = "http://127.0.0.1:8000/scan/full"


def create_suspicious_image():
    """
    Creates a dummy image in memory that looks like a phishing attempt.
    It has a white background and text saying "PayPal: Verify Account".
    This tests both the Visual Model (CLIP) and the OCR Model.
    """
    print("🎨 Generating a synthetic phishing image for testing...")
    # Create white background image
    img = Image.new("RGB", (600, 400), color="white")
    d = ImageDraw.Draw(img)

    # Add suspicious text (Simulating a screenshot of an email)
    # Note: We use default font, it might look small but OCR can read it.
    text_content = "URGENT: PAYPAL ACCOUNT LOCKED.\nPLEASE LOGIN BELOW TO VERIFY."
    d.text((50, 150), text_content, fill=(0, 0, 0))  # Black text

    # Save to memory buffer
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    return img_byte_arr


def run_test(name, payload=None, file_buffer=None):
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING TEST: {name}")
    print(f"{'='*60}")

    files = {}
    if file_buffer:
        # 'file' matches the @app.post parameter name in main.py
        files = {"file": ("test_image.png", file_buffer, "image/png")}

    try:
        response = requests.post(API_URL, data=payload, files=files)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ VERDICT: {data['verdict']}")
            print(f"📊 Final Risk Score: {data['final_risk_score']}")
            print(f"📝 Risk Factors Found:")
            for risk in data["risk_factors"]:
                print(f"   - {risk}")

            print("\n--- Detailed Debug Info ---")
            print(f"   URL Score:    {data.get('url_score')}")
            print(f"   Text Score:   {data.get('text_score')}")
            print(
                f"   Visual Score: {data.get('visual_score')} (Context: {data.get('visual_context')})"
            )
            print(f"   OCR Score:    {data.get('ocr_phish_score')}")
            if data.get("ocr_text_snippet"):
                print(f"   OCR Text Read: '{data.get('ocr_text_snippet')}'")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("   (Make sure 'uvicorn main:app --reload' is running!)")


# ==========================================
# EXECUTE SCENARIOS
# ==========================================

if __name__ == "__main__":
    # SCENARIO 1: Text Phishing (Nigerian Prince Style)
    run_test(
        name="Text Only Attack",
        payload={
            "subject": "Urgent Assistance Needed",
            "body": "I am Prince Abako. I need your help to transfer $50 million. Send your bank details.",
        },
    )

    # SCENARIO 2: URL Phishing
    run_test(
        name="Malicious URL Attack",
        payload={
            "url": "http://secure-login-paypal-update-required.com",
            "body": "Click here",
        },
    )

    # SCENARIO 3: Image Phishing (Generated on the fly)
    # This simulates an image with hidden text "URGENT PAYPAL LOCKED"
    fake_image = create_suspicious_image()
    run_test(
        name="Image/OCR Phishing Attack",
        payload={"body": "Check the attachment"},  # Body is innocent
        file_buffer=fake_image,
    )

    # SCENARIO 4: Safe Request
    run_test(
        name="Safe/Legit Request",
        payload={
            "url": "http://google.com",
            "body": "Hey, did you see the meeting notes?",
        },
    )
