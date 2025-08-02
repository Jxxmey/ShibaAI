import os
import requests
import json
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึง API keys จาก environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
VEO3_API_KEY = os.getenv("VEO3_API_KEY")
UPLOAD_POST_API = os.getenv("UPLOAD_POST_API")

if not OPENROUTER_API_KEY or not VEO3_API_KEY or not UPLOAD_POST_API:
    raise ValueError("Missing API keys. Please check your .env file.")

# --- ฟังก์ชันสำหรับสร้างแคปชั่นด้วย OpenRouter ---
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

# --- ฟังก์ชันสำหรับสร้างวิดีโอด้วย Veo3 ---
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

# --- ฟังก์ชันสำหรับโพสต์ด้วย upload-post api ---
def post_with_upload_post_api(video_url, caption):
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
        return response.ok
    except requests.exceptions.RequestException as e:
        print(f"Error calling upload-post API: {e}")
        return False

# --- โค้ดหลักที่รันงานอัตโนมัติ ---
def run_daily_job():
    shiba_prompt = "A Shiba Inu dog speaks a life quote in a cute voice, daily life, quote, philosophical"
    print("Starting daily job...")
    
    # 1. สร้างวิดีโอ
    video_id = generate_video_with_veo3(shiba_prompt)
    if not video_id:
        print("Job failed: Failed to generate video")
        return

    # 2. สร้างแคปชั่น
    caption = generate_caption_with_openrouter(shiba_prompt)
    if not caption:
        print("Job failed: Failed to generate caption")
        return
    
    # URL ของวิดีโอ
    video_url = f"https://veo3api.com/download/{video_id}"

    # 3. โพสต์
    post_success = post_with_upload_post_api(video_url, caption)
    
    if post_success:
        print("Job completed successfully! Content posted.")
    else:
        print("Job failed: Failed to post to API.")

if __name__ == '__main__':
    run_daily_job()