import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core
from core.database import db

# ML modules
from modules.book_recommender.model import BookRecommender
from modules.book_recommender.repository import get_all_books_for_recommendation
from modules.book_recommender.preprocess import create_feature_tags

# ==========================================
# 1. KHỞI TẠO FASTAPI
# ==========================================
app = FastAPI(
    title="QLTV AI Service",
    description="Dịch vụ AI gợi ý sách cho hệ thống Quản lý Thư viện",
    version="1.0.0"
)

# ==========================================
# 2. CẤU HÌNH CORS
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. KHỞI TẠO MODEL
# ==========================================
recommender = BookRecommender()

# ==========================================
# 4. IMPORT ROUTER
# ==========================================
from modules.book_recommender.router import router as book_router

app.include_router(
    book_router,
    prefix="/ai",
    tags=["Book Recommendation"]
)

# ==========================================
# 5. STARTUP EVENT
# ==========================================
@app.on_event("startup")
async def startup_event():

    print("====================================")
    print("🚀 Đang khởi động AI Recommendation Service...")
    print("====================================")

    try:
        # 1. Lấy dữ liệu sách từ database
        df_books = get_all_books_for_recommendation()

        if df_books.empty:
            print("⚠️ Không có dữ liệu sách trong database")
            return

        print(f"📚 Đã tải {len(df_books)} sách từ database")

        # 2. Preprocess dữ liệu
        df_processed = create_feature_tags(df_books)

        print("🧠 Đang huấn luyện mô hình AI...")

        # 3. Train model
        recommender.train(df_processed)

        print("✅ Mô hình gợi ý sách đã sẵn sàng")

    except Exception as e:
        print("❌ Lỗi khi khởi động AI model")
        print(e)


# ==========================================
# 6. API TEST
# ==========================================
@app.get("/")
async def root():

    sample_ids = []

    if recommender.df is not None:
        sample_ids = recommender.df["MaSach"].head().tolist()

    return {
        "service": "QLTV AI Recommendation Service",
        "status": "online",
        "sample_book_ids": sample_ids
    }


# ==========================================
# 7. CHẠY SERVER
# ==========================================
if __name__ == "__main__":

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )