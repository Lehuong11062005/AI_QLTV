from fastapi import APIRouter
from .service import get_ai_response

router = APIRouter(prefix="/chatbox", tags=["Chatbot"])

@router.post("/chat")
async def chat_endpoint(data: dict):
    user_message = data.get("message")
    reply = await get_ai_response(user_message)
    return {"reply": reply}