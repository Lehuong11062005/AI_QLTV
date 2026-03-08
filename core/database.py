import pyodbc
import os
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# 1. Xác định đường dẫn tuyệt đối tới file .env
# Cách này giúp Python tìm thấy file .env dù bạn chạy app từ bất kỳ thư mục nào
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / '.env'
load_dotenv(dotenv_path=env_path)

class Database:
    def __init__(self):
        # 2. Lấy thông tin từ .env
        self.server = os.getenv('DB_SERVER')
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        
        # 3. Tự động chọn Driver phù hợp
        # Thử 'ODBC Driver 17 for SQL Server' trước, nếu không có thì dùng 'SQL Server'
        self.driver = '{SQL Server}' 
        
        # Kiểm tra cấu hình ngay khi khởi tạo để báo lỗi sớm
        self._check_config()

    def _check_config(self):
        """Kiểm tra xem các biến môi trường có tồn tại không."""
        missing = []
        if not self.server: missing.append("DB_SERVER")
        if not self.database: missing.append("DB_DATABASE")
        if not self.username: missing.append("DB_USER")
        
        if missing:
            print(f"❌ LỖI: Thiếu cấu hình trong .env: {', '.join(missing)}")
            print(f"Kiểm tra file tại: {env_path}")
        else:
            print(f"✅ Đã tải cấu hình Database: {self.database} trên {self.server}")

    def _get_connection(self):
        """Tạo kết nối mới tới SQL Server."""
        try:
            conn_str = (
                f"DRIVER={self.driver};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "Connection Timeout=30;"
            )
            return pyodbc.connect(conn_str)
        except Exception as e:
            print(f"❌ Lỗi kết nối SQL Server: {e}")
            raise

    def query_to_dataframe(self, sql_query, params=None):
        """Thực thi câu lệnh SQL và trả về DataFrame của Pandas."""
        conn = None
        try:
            conn = self._get_connection()
            # Sử dụng pandas để đọc trực tiếp từ kết nối
            # User warning: pandas khuyến khích dùng SQLAlchemy nhưng pyodbc vẫn hoạt động tốt cho dự án này
            df = pd.read_sql(sql_query, conn, params=params)
            return df
        except Exception as e:
            print(f"❌ Lỗi truy vấn Database: {e}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

# Khởi tạo đối tượng dùng chung duy nhất (Singleton)
db = Database()