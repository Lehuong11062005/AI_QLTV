import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.database import db

router = APIRouter(prefix="/image", tags=["Image Recognition"])

@router.post("/recognize")
async def recognize_book_cover(file: UploadFile = File(...)):
    """API nhận file ảnh và trả về thông tin sách tương ứng."""
    # 1. Kiểm tra định dạng
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên định dạng ảnh.")

    # 2. Lưu file tạm thời
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = f"{temp_dir}/{file.filename}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Gọi model AI xử lý
        from app import image_recognizer # Import biến toàn cục từ app
        result = image_recognizer.recognize(temp_file_path)

        if result["status"] == "success":
            # (Tùy chọn) Truy vấn thêm DB để trả về tên sách, ảnh minh họa...
            sql = """
                SELECT 
                    s.TenSach, 
                    s.AnhMinhHoa, 
                    COALESCE(tg.TenTG, N'Chưa rõ') AS TacGia 
                FROM Sach s
                LEFT JOIN TacGia tg ON s.MaTG = tg.MaTG
                WHERE s.MaSach = ?
            """
            df_book = db.query_to_dataframe(sql, params=[result["MaSach"]])
            if not df_book.empty:
                book_info = df_book.to_dict("records")[0]
                result["BookInfo"] = book_info

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. Dọn dẹp: Xóa file tạm sau khi nhận diện xong
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)