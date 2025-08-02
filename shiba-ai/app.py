import os
from flask import Flask
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

app = Flask(__name__)

# ดึง API keys จาก environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
VEO3_API_KEY = os.getenv("VEO3_API_KEY")
UPLOAD_POST_API = os.getenv("UPLOAD_POST_API")

# นี่คือส่วนที่รับคำสั่งจาก Cron Job หรือจากภายนอก
@app.route('/run-job', methods=['GET'])
def trigger_job():
    # เรียกใช้สคริปต์ run_job.py จากภายใน
    os.system("python run_job.py")
    return "Job triggered!", 200

if __name__ == '__main__':
    app.run(debug=True)