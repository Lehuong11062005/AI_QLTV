import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

async def get_ai_response(user_input: str):
    context = "Bạn là trợ lý ảo thư viện QLTV. Trả lời thân thiện bằng tiếng Việt."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": f"{context}\nNgười dùng: {user_input}"}
                    ]
                }
            ]
        )

        return response.text

    except Exception as e:
        return f"Lỗi kết nối AI: {e}"