from fastapi import APIRouter
from pydantic import BaseModel
from .service import get_ai_response

router = APIRouter(prefix="/chatbox", tags=["Chatbot"])

# Tạo một class chuẩn để quy định dữ liệu gửi lên
class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(data: ChatRequest):
    # Lấy message từ dữ liệu gửi lên
    user_message = data.message 
    
    # Gọi AI xử lý
    reply = await get_ai_response(user_message)
    
    # Trả về kết quả
    return {"reply": reply} 