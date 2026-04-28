# Real Madrid Shop - E-commerce Website

Website thương mại điện tử chuyên bán quần áo và phụ kiện chính thức của câu lạc bộ Real Madrid.

## 🚀 Tính năng
- **Người dùng**: Đăng ký, Đăng nhập, Xem sản phẩm, Giỏ hàng, Thanh toán giả lập, Lịch sử đơn hàng.
- **Admin**: Quản lý sản phẩm (Thêm/Xóa), Xem thống kê doanh thu, Quản lý đơn hàng.
- **Thiết kế**: Giao diện premium theo phong cách Real Madrid (Trắng, Vàng, Xanh), Responsive.

## 🛠️ Công nghệ sử dụng
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript
- **Database**: SQLite (Mặc định), hỗ trợ PostgreSQL cho Render.
- **ORM**: SQLAlchemy
- **Auth**: Flask-Login, Flask-Bcrypt (Hashing password)

## 💻 Hướng dẫn chạy Local

1. **Clone repository**:
   ```bash
   git clone https://github.com/your-username/real-madrid-shop.git
   cd real-madrid-shop
   ```

2. **Cài đặt môi trường ảo (Khuyên dùng)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```

3. **Cài đặt thư viện**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Chạy ứng dụng**:
   ```bash
   python app.py
   ```
   Ứng dụng sẽ chạy tại: `http://127.0.0.1:5000`

**Tài khoản Admin mặc định:**
- Username: `admin`
- Password: `admin123`

## 🌐 Hướng dẫn Deploy lên Render

1. Tạo một repository mới trên GitHub và đẩy toàn bộ code lên.
2. Truy cập [Render.com](https://render.com) và tạo một **Web Service** mới.
3. Kết nối với GitHub repository của bạn.
4. Cấu hình các thông số sau:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Thêm các Environment Variables nếu cần (như `SECRET_KEY`).
6. Nhấn **Deploy**.

## 📁 Cấu trúc thư mục
- `app.py`: File thực thi chính.
- `models/`: Chứa định nghĩa database.
- `static/`: Chứa CSS, JS và hình ảnh.
- `templates/`: Các file HTML giao diện.
- `requirements.txt`: Danh sách thư viện cần thiết.

---
Thiết kế với ❤️ dành cho các Madridista!
Hala Madrid y Nada Más!
