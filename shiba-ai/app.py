import os
import requests
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

app = Flask(__name__)

# ดึง API keys จาก environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
VEO3_API_KEY = os.getenv("VEO3_API_KEY")
UPLOAD_POS_API = os.getenv("UPLOAD_POS_API")

if not OPENROUTER_API_KEY or not VEO3_API_KEY or not UPLOAD_POS_API:
    raise ValueError("Missing API keys. Please check your .env file.")

# --- ฟังก์ชันสำหรับสร้างแคปชั่นด้วย OpenRouter (ไม่มีการเปลี่ยนแปลง) ---
def generate_caption_with_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "google/gemini-pro-1.5-flash",
        "messages": [
            {"role": "system", "content": "คุณเป็นผู้ช่วยเขียนแคปชั่นที่น่าสนใจสำหรับวิดีโอ"},
            {"role": "user", "content": f"เขียนแคปชั่นสั้นๆ สำหรับวิดีโอเกี่ยวกับ: {prompt}"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        caption = result['choices'][0]['message']['content']
        return caption
    except requests.exceptions.RequestException as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

# --- ฟังก์ชันสำหรับสร้างวิดีโอด้วย Veo3 (ไม่มีการเปลี่ยนแปลง) ---
def generate_video_with_veo3(prompt):
    url = "https://veo3api.com/generate"
    headers = {
        "Authorization": f"Bearer {VEO3_API_KEY}"
    }
    params = {
        "prompt": prompt,
        "model": "veo3",
        "watermark": "veo3"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        return result['video_id']
    except requests.exceptions.RequestException as e:
        print(f"Error calling Veo3 API with GET: {e}")
        return None

# --- ฟังก์ชันใหม่สำหรับโพสต์ด้วย upload-post api ---
def post_with_upload_post_api(video_url, caption):
    # สมมติว่า endpoint ของ upload-post api อยู่ที่ https://api.upload-post.com/v1/post
    url = "https://api.upload-post.com/v1/post"
    headers = {
        "Authorization": f"Bearer {UPLOAD_POS_API}",
        "Content-Type": "application/json"
    }
    data = {
        "video_url": video_url,
        "caption": caption
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        # API อาจจะส่งสถานะความสำเร็จกลับมา
        return response.ok
    except requests.exceptions.RequestException as e:
        print(f"Error calling upload-post API: {e}")
        return False

# --- Endpoint หลักของเว็บ (Backend) ---
@app.route('/generate_and_post', methods=['POST'])
def generate_and_post_content():
    data = request.json
    prompt = data.get('prompt')

    shiba_prompt = "A Shiba Inu dog speaks a life quote in a cute voice, daily life, quote, philosophical"
    
    # 1. สร้างวิดีโอด้วย Veo3
    video_id = generate_video_with_veo3(shiba_prompt)
    if not video_id:
        return jsonify({"error": "Failed to generate video"}), 500

    # 2. สร้างแคปชั่นด้วย OpenRouter
    caption = generate_caption_with_openrouter(shiba_prompt)
    if not caption:
        return jsonify({"error": "Failed to generate caption"}), 500
    
    # URL ของวิดีโอ (ต้องเป็น URL ที่สามารถเข้าถึงได้จากภายนอก)
    video_url = f"https://veo3api.com/download/{video_id}"

    # 3. โพสต์ด้วย upload-post api (ใช้ฟังก์ชันใหม่)
    post_success = post_with_upload_post_api(video_url, caption)
    
    if post_success:
        return jsonify({
            "status": "success",
            "message": "Content generated and posted successfully!",
            "video_url": video_url,
            "caption": caption
        })
    else:
        return jsonify({"error": "Failed to post using upload-post api"}), 500

if __name__ == '__main__':
    app.run(debug=True)