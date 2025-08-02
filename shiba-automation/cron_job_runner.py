import requests

# URL ของ endpoint ที่คุณต้องการเรียก
# ใน Render จะต้องใช้ public URL ของแอปคุณ
RENDER_APP_URL = "https://your-render-app-name.onrender.com"

# ข้อมูลที่ต้องการส่งไปยัง endpoint
payload = {
    "prompt": "Shiba Inu life quote"
}

try:
    response = requests.post(
        f"{RENDER_APP_URL}/generate_and_post",
        json=payload
    )
    response.raise_for_status() # ตรวจสอบว่ามี error หรือไม่
    print("AI Automation job completed successfully!")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Failed to run AI Automation job: {e}")