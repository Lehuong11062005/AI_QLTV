import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class BookRecommender:
    def __init__(self):
        self.df = None
        self.cosine_sim = None
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.indices = None 
        # Danh sách các cột cần thiết để hiển thị Card sách trên giao diện
        self.columns_for_ui = [
            "MaSach", "TenSach", "TenTG", "TenDM", "AnhMinhHoa", 
            "GiaBan", "SoLuongCoSan", "SoLuongTon", "TinhTrang", 
            "MoTa", "NamXuatBan"
        ]

    def train(self, df):
        if df is None or df.empty:
            print("Dữ liệu trống, không thể huấn luyện.")
            return

        self.df = df.reset_index(drop=True).copy()
        if "tags" not in self.df.columns:
            raise ValueError("DataFrame phải chứa cột 'tags'")

        self.df["tags"] = self.df["tags"].fillna('')
        tfidf_matrix = self.tfidf.fit_transform(self.df["tags"])
        self.cosine_sim = cosine_similarity(tfidf_matrix)
        self.indices = pd.Series(self.df.index, index=self.df["MaSach"]).to_dict()
        print(f"✅ Đã huấn luyện model với {len(self.df)} đầu sách.")

    # ==========================================
    # 1. GỢI Ý THEO SÁCH (Cập nhật để trả đủ data UI)
    # ==========================================
    def get_recommendations(self, book_id, top_n=5):
        """Gợi ý sách tương tự với 1 cuốn cụ thể, trả về đủ info để hiện Card."""
        if self.df is None or self.cosine_sim is None or book_id not in self.indices:
            return []

        idx = self.indices[book_id]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Lấy top N (bỏ qua chính nó)
        sim_scores = sim_scores[1: top_n + 1]
        book_indices = [i[0] for i in sim_scores]

        # Lọc các cột tồn tại để trả về cho UI
        available_cols = [col for col in self.columns_for_ui if col in self.df.columns]
        return self.df.iloc[book_indices][available_cols].to_dict("records")

    # ==========================================
    # 2. GỢI Ý THEO USER (Đã tối ưu)
    # ==========================================
    def recommend_for_user(self, user_history, top_n=5):
        """Gợi ý cá nhân hóa dựa trên lịch sử, trả về đủ info để hiện Card."""
        if self.df is None or self.cosine_sim is None or not user_history:
            return []

        try:
            history_idxs = [self.indices[bid] for bid in user_history if bid in self.indices]
            if not history_idxs:
                return []

            combined_sim = self.cosine_sim[history_idxs].sum(axis=0)
            scores = pd.Series(combined_sim, index=self.df.index)
            scores = scores.drop(history_idxs)
            top_indices = scores.nlargest(top_n).index

            # Lọc các cột tồn tại để trả về cho UI
            available_cols = [col for col in self.columns_for_ui if col in self.df.columns]
            return self.df.loc[top_indices, available_cols].to_dict("records")

        except Exception as e:
            print(f"❌ Lỗi gợi ý cho User: {e}")
            return []