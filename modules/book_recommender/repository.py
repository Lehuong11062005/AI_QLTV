from core.database import db
import pandas as pd

# ==========================================
# 1. LẤY TẤT CẢ SÁCH (Dùng nạp dữ liệu cho Model AI)
# ==========================================
def get_all_books_for_recommendation():
    """Lấy dữ liệu sách đầy đủ thuộc tính để model có sẵn data hiển thị."""
    sql = """
        SELECT 
            s.MaSach, s.TenSach, s.MoTa, s.NamXuatBan, s.AnhMinhHoa, s.GiaBan, 
            s.SoLuongTon, s.TinhTrang,
            COALESCE(tg.TenTG, N'Chưa rõ') AS TenTG,
            COALESCE(dm.TenDM, N'Khác') AS TenDM,
            (SELECT COUNT(*) FROM BanSao_ThuVien bs 
             WHERE bs.MaSach = s.MaSach AND bs.TrangThaiBanSao = N'SanSang') AS SoLuongCoSan
        FROM Sach s
        LEFT JOIN TacGia tg ON s.MaTG = tg.MaTG
        LEFT JOIN DanhMuc dm ON s.MaDM = dm.MaDM
    """
    df = db.query_to_dataframe(sql)
    return df if df is not None else pd.DataFrame()

# ==========================================
# 2. LẤY CHI TIẾT 1 CUỐN SÁCH
# ==========================================
def get_book_by_id(book_id):
    """Lấy thông tin chi tiết đầy đủ của một cuốn sách."""
    sql = """
        SELECT 
            s.MaSach, s.TenSach, s.MoTa, s.NamXuatBan, s.AnhMinhHoa, s.GiaBan,
            s.SoLuongTon, s.TinhTrang,
            COALESCE(tg.TenTG, N'Chưa rõ') AS TenTG,
            COALESCE(dm.TenDM, N'Khác') AS TenDM,
            (SELECT COUNT(*) FROM BanSao_ThuVien bs 
             WHERE bs.MaSach = s.MaSach AND bs.TrangThaiBanSao = N'SanSang') AS SoLuongCoSan
        FROM Sach s
        LEFT JOIN TacGia tg ON s.MaTG = tg.MaTG
        LEFT JOIN DanhMuc dm ON s.MaDM = dm.MaDM
        WHERE s.MaSach = ?
    """
    df = db.query_to_dataframe(sql, params=[book_id])
    return df if df is not None else pd.DataFrame()

# ==========================================
# 3. LỊCH SỬ USER TỔNG HỢP
# ==========================================
def get_user_history(ma_dg):
    """Giữ nguyên vì chỉ cần lấy danh sách ID để làm đầu vào cho AI."""
    sql = """
        SELECT MaSach FROM (
            SELECT bs.MaSach FROM MuonSach ms
            JOIN MuonSach_Sach mss ON ms.MaMuon = mss.MaMuon
            JOIN BanSao_ThuVien bs ON mss.MaBanSao = bs.MaBanSao
            WHERE ms.MaDG = ?
            UNION
            SELECT dhs.MaSach FROM DonHang_Sach dhs
            JOIN DonHang dh ON dhs.MaDH = dh.MaDH
            WHERE dh.MaDG = ?
            UNION
            SELECT MaSach FROM DanhGiaSach WHERE MaDG = ?
        ) AS CombinedHistory
    """
    df = db.query_to_dataframe(sql, params=[ma_dg, ma_dg, ma_dg])
    return df["MaSach"].tolist() if df is not None and not df.empty else []

# ==========================================
# 4. SÁCH PHỔ BIẾN (Dự phòng Cold Start)
# ==========================================
def get_popular_books(top_n=5):
    """Lấy sách hot kèm đầy đủ thông tin để render Cards ngay lập tức."""
    sql = """
        SELECT TOP (?) 
            s.MaSach, s.TenSach, s.AnhMinhHoa, s.GiaBan, 
            s.SoLuongTon, s.TinhTrang, s.MoTa, s.NamXuatBan,
            tg.TenTG, dm.TenDM,
            (SELECT COUNT(*) FROM BanSao_ThuVien bs 
             WHERE bs.MaSach = s.MaSach AND bs.TrangThaiBanSao = N'SanSang') AS SoLuongCoSan,
            COUNT(mss.MaBanSao) as SoLuotMuon
        FROM Sach s
        LEFT JOIN TacGia tg ON s.MaTG = tg.MaTG
        LEFT JOIN DanhMuc dm ON s.MaDM = dm.MaDM
        LEFT JOIN BanSao_ThuVien bs ON s.MaSach = bs.MaSach
        LEFT JOIN MuonSach_Sach mss ON bs.MaBanSao = mss.MaBanSao
        GROUP BY s.MaSach, s.TenSach, s.AnhMinhHoa, s.GiaBan, 
                 s.SoLuongTon, s.TinhTrang, s.MoTa, s.NamXuatBan, tg.TenTG, dm.TenDM
        ORDER BY SoLuotMuon DESC, s.MaSach DESC
    """
    df = db.query_to_dataframe(sql, params=[top_n])
    return df.to_dict("records") if df is not None else []