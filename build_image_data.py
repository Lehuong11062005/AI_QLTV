# File: build_image_data.py
# Script này sẽ được chạy một lần để tạo dữ liệu vector từ ảnh bìa sách và lưu vào file .pkl
from core.database import db
from modules.image_recognition.model import ImageRecognizer

def run_build():
    print("Bắt đầu tiến trình tạo dữ liệu AI nhận diện ảnh...")
    
    # 1. Truy vấn lấy danh sách sách và link ảnh từ SQL
    sql = "SELECT MaSach, AnhMinhHoa FROM Sach WHERE AnhMinhHoa IS NOT NULL AND AnhMinhHoa != ''"
    df_books = db.query_to_dataframe(sql)
    
    if df_books.empty:
        print("Không có sách nào có ảnh minh họa.")
        return

    # 2. Chuyển thành dạng Dict { 'MaSach': 'Link_URL' }
    book_images_dict = dict(zip(df_books['MaSach'], df_books['AnhMinhHoa']))
    print(f"Tìm thấy {len(book_images_dict)} link ảnh cần phân tích.")

    # 3. Gọi model để tải ảnh, trích xuất vector và lưu file .pkl
    recognizer = ImageRecognizer()
    recognizer.build_and_save_embeddings(book_images_dict)

if __name__ == "__main__":
    run_build()