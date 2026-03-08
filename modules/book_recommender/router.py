# modules/book_recommender/router.py
from fastapi import APIRouter, HTTPException, Query
from modules.book_recommender.repository import (
    get_book_by_id,
    get_user_history,
    get_popular_books  # Thêm hàm này để xử lý user mới
)

router = APIRouter(
    prefix="/recommend",
    tags=["Recommendations"]
)

# ==========================================
# 1. RECOMMEND THEO BOOK (Sách tương tự)
# ==========================================
@router.get("/book/{book_id}")
async def recommend_by_book(
    book_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """
    API gợi ý sách tương tự dựa trên nội dung của một cuốn sách cụ thể.
    """
    # 1. Kiểm tra sách tồn tại trong DB
    book_check = get_book_by_id(book_id)

    if book_check.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy sách với ID {book_id}"
        )

    try:
        from app import recommender

        if recommender.df is None:
            raise HTTPException(
                status_code=503,
                detail="Mô hình AI đang được khởi tạo, vui lòng thử lại sau"
            )

        # 2. Lấy gợi ý từ model
        suggestions = recommender.get_recommendations(
            book_id,
            top_n=limit
        )

        return {
            "status": "success",
            "type": "content_based",
            "metadata": {
                "target_book": book_id,
                "total": len(suggestions),
                "limit": limit
            },
            "data": suggestions
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý AI: {str(e)}"
        )


# ==========================================
# 2. RECOMMEND THEO USER (Cá nhân hóa)
# ==========================================
@router.get("/user/{user_id}")
async def recommend_for_user(
    user_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """
    API gợi ý sách dựa trên lịch sử của user.
    Nếu user mới (Cold Start), sẽ gợi ý sách phổ biến nhất.
    """
    try:
        from app import recommender

        if recommender.df is None:
            raise HTTPException(
                status_code=503,
                detail="Mô hình AI đang được khởi tạo, vui lòng thử lại sau"
            )

        # 1. Lấy lịch sử tương tác của user (Mượn, Mua, Đánh giá)
        history = get_user_history(user_id)

        # 2. Xử lý logic gợi ý
        if not history:
            # TRƯỜNG HỢP COLD START: Gợi ý sách hot nhất hệ thống
            suggestions = get_popular_books(top_n=limit)
            recommendation_type = "popularity_based"
            message = "User mới - Gợi ý dựa trên xu hướng"
        else:
            # TRƯỜNG HỢP CÓ LỊCH SỬ: Gợi ý cá nhân hóa bằng AI
            suggestions = recommender.recommend_for_user(
                history,
                top_n=limit
            )
            recommendation_type = "personalized"
            message = "Gợi ý dựa trên sở thích cá nhân"

        return {
            "status": "success",
            "type": recommendation_type,
            "user_id": user_id,
            "message": message,
            "metadata": {
                "history_size": len(history),
                "total": len(suggestions),
                "limit": limit
            },
            "data": suggestions
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi hệ thống AI: {str(e)}"
        )