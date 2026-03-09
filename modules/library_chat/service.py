import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def get_ai_response(user_input: str):
    context = "Bạn là trợ lý ảo thư viện QLTV. Trả lời thân thiện bằng tiếng Việt."
    
    try:
        # BẮT BUỘC DÙNG 2.0 VÌ 1.5 ĐÃ BỊ KHAI TỬ
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=f"{context}\nNgười dùng: {user_input}"
        )
        return response.text

    except Exception as e:
        # Xử lý êm ái lỗi 429 (vượt hạn mức miễn phí)
        if "429" in str(e):
            return "Trợ lý thư viện đang phục vụ quá nhiều người, Hưởng đợi khoảng 1 phút rồi hỏi lại nhé!"
        
        return f"Lỗi hệ thống: {e}"