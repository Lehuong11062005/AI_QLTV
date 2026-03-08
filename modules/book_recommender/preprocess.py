import pandas as pd

# ==========================================
# 1. LÀM SẠCH DỮ LIỆU SÁCH
# ==========================================
def clean_book_data(df):
    """Làm sạch dữ liệu và đảm bảo các cột hiển thị UI không bị NULL."""
    if df is None or df.empty:
        return pd.DataFrame()

    df_cleaned = df.copy()

    # Danh sách các cột cần có để hiển thị trên Frontend
    # Lưu ý: Tên cột phải khớp chính xác với câu lệnh SQL AS ...
    ui_cols = ["TenSach", "TenTG", "TenDM", "MoTa", "AnhMinhHoa", "TinhTrang"]
    
    for col in ui_cols:
        if col in df_cleaned.columns:
            # fillna để tránh lỗi khi render giao diện hoặc xử lý string
            df_cleaned[col] = df_cleaned[col].fillna("Unknown").astype(str).str.strip()
        else:
            print(f"⚠️ Cảnh báo: Thiếu cột {col} trong dữ liệu SQL")
            df_cleaned[col] = "Unknown"

    # Xử lý các cột số (Giá, Số lượng)
    numeric_cols = ["GiaBan", "SoLuongCoSan", "SoLuongTon", "NamXuatBan"]
    for col in numeric_cols:
        if col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].fillna(0)
        else:
            df_cleaned[col] = 0

    return df_cleaned

# ==========================================
# 2. CHUẨN HÓA TEXT
# ==========================================
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    # Chuyển về chữ thường và xóa khoảng trắng thừa
    return " ".join(text.lower().split())

# ==========================================
# 3. TẠO FEATURE TAGS CHO MODEL
# ==========================================
def create_feature_tags(df):
    """Tạo cột tags cho AI nhưng giữ lại đầy đủ thông tin hiển thị."""
    # Bước 1: Làm sạch dữ liệu trước
    df_processed = clean_book_data(df)

    if df_processed.empty:
        return df_processed

    # Bước 2: Tạo bản sao các cột text để chuẩn hóa làm tags (không ghi đè lên dữ liệu hiển thị)
    # Chúng ta muốn 'TenSach' hiển thị có hoa thường, nhưng 'tags' thì phải chuẩn hóa
    tag_features = ["TenSach", "TenTG", "TenDM", "MoTa"]
    
    # Tạo một cột tạm để chứa nội dung gộp
    temp_tags = df_processed[tag_features].astype(str).apply(lambda x: ' '.join(x), axis=1)
    df_processed["tags"] = temp_tags.apply(normalize_text)

    # Bước 3: Trả về đầy đủ các cột để hiển thị giao diện theo yêu cầu của Hưởng
    return df_processed[[
        "MaSach", "TenSach", "TenTG", "TenDM", "AnhMinhHoa", 
        "GiaBan", "SoLuongCoSan", "SoLuongTon", "TinhTrang", 
        "MoTa", "NamXuatBan", "tags"
    ]]