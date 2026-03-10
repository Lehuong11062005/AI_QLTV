import os
import pickle
import numpy as np
import requests
from io import BytesIO
from PIL import Image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from sklearn.metrics.pairwise import cosine_similarity

class ImageRecognizer:
    def __init__(self, saved_model_path="saved_models/image_model.pkl"):
        self.saved_model_path = saved_model_path
        self.model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        self.book_embeddings = {} 

    def _extract_features(self, image_source):
        """Hàm đọc ảnh từ URL hoặc Local path và trả về mảng đặc trưng."""
        try:
            # 1. Tải ảnh từ URL hoặc đọc từ máy
            if image_source.startswith("http://") or image_source.startswith("https://"):
                response = requests.get(image_source, timeout=10)
                response.raise_for_status() # Báo lỗi nếu link hỏng (404, 500...)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(image_source)

            # 2. Xử lý ảnh (Convert sang RGB để tránh lỗi với ảnh PNG nền trong suốt)
            img = img.convert("RGB")
            img = img.resize((224, 224))

            # 3. Đưa vào Model
            img_data = keras_image.img_to_array(img)
            img_data = np.expand_dims(img_data, axis=0)
            img_data = preprocess_input(img_data)
            
            features = self.model.predict(img_data, verbose=0)
            return features.flatten()
            
        except Exception as e:
            print(f"❌ Lỗi xử lý ảnh ({image_source}): {e}")
            return None

    def load_embeddings(self):
        """Tải vector từ file .pkl lên RAM."""
        if os.path.exists(self.saved_model_path):
            with open(self.saved_model_path, "rb") as f:
                self.book_embeddings = pickle.load(f)
            print(f"✅ Đã tải dữ liệu nhận diện cho {len(self.book_embeddings)} cuốn sách.")
        else:
            print("⚠️ Chưa có file image_model.pkl. Cần build embeddings.")

    def build_and_save_embeddings(self, book_images_dict):
        """
        Quét toàn bộ ảnh (URL) trong thư viện, tạo vector và lưu ra file.
        book_images_dict: dict dạng {'MaSach1': 'https://link-anh-1.com/a.jpg', ...}
        """
        print("🧠 Đang tải và trích xuất đặc trưng ảnh bìa sách từ URL...")
        for book_id, img_url in book_images_dict.items():
            if img_url and img_url.strip() != "":
                features = self._extract_features(img_url)
                if features is not None:
                    self.book_embeddings[book_id] = features

        # Lưu lại để dùng cho lần sau
        os.makedirs(os.path.dirname(self.saved_model_path), exist_ok=True)
        with open(self.saved_model_path, "wb") as f:
            pickle.dump(self.book_embeddings, f)
        print("✅ Đã lưu đặc trưng ảnh thành công.")

    def recognize(self, upload_img_path, threshold=0.75):
        """So sánh ảnh upload với kho dữ liệu."""
        if not self.book_embeddings:
            return {"status": "error", "message": "Hệ thống AI chưa sẵn sàng."}

        upload_features = self._extract_features(upload_img_path)
        if upload_features is None:
            return {"status": "error", "message": "Không thể phân tích ảnh tải lên."}

        best_match_id = None
        highest_score = -1

        for book_id, db_features in self.book_embeddings.items():
            score = cosine_similarity([upload_features], [db_features])[0][0]
            if score > highest_score:
                highest_score = float(score)
                best_match_id = book_id

        if highest_score >= threshold:
            return {
                "status": "success", 
                "MaSach": best_match_id, 
                "Confidence": round(highest_score * 100, 2)
            }
            
        return {"status": "fail", "message": "Không tìm thấy sách phù hợp trong thư viện."}