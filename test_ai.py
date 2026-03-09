import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"Đang dùng Key: {key[:10]}...") # In ra 10 ký tự đầu để check xem key có nhận đúng không

genai.configure(api_key=key)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Xin chào")
    print("AI Trả lời:", response.text)
except Exception as e:
    print("LỖI CHI TIẾT:", e)