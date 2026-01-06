# First Cloud Journey Assistant

## Hướng dẫn setup:

### Cách 1: Chạy với Docker (Khuyến nghị)

1. **Cài đặt Docker:**
   - Tải Docker Desktop: https://www.docker.com/products/docker-desktop

2. **Build và chạy:**
```bash
docker-compose up --build
```

3. **Truy cập:**
   - Mở trình duyệt: http://localhost:8501

### Cách 2: Chạy local

1. **Clone repository:**
```bash
git clone https://github.com/hoanglong1812003/chatbotfcaj.git
cd chatbotfcaj
```

2. **Cài đặt packages:**
```bash
pip install -r requirements.txt
```

3. **Cấu hình API key:**
```bash
cp .env.example .env
# Chỉnh sửa .env và thêm GROQ_API_KEY
```

4. **Chuẩn bị dữ liệu:**
- Tạo thư mục `data/`
- Đặt tài liệu PDF/TXT vào thư mục `data/`

5. **Xử lý tài liệu:**
```bash
python process_docs.py
```

6. **Chạy chatbot:**
```bash
streamlit run app.py
```

## Docker Commands:

```bash
# Build image
docker build -t fcj-chatbot .

# Chạy container
docker run -p 8501:8501 --env-file .env fcj-chatbot

# Dừng container
docker-compose down

# Xem logs
docker-compose logs -f
```

## Cấu trúc thư mục:
```
├── data/                 # Tài liệu training (không push lên git)
├── vectorstore/          # Vector database (tự động tạo, không push)
├── app.py               # Ứng dụng chính
├── process_docs.py      # Script xử lý tài liệu
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose config
├── .env.example        # Template cho API keys
├── .gitignore          # Loại trừ file nhạy cảm
└── README.md           # Hướng dẫn
```

## Lưu ý bảo mật:
- File `.env` chứa API keys - KHÔNG push lên git
- Thư mục `data/` có thể chứa tài liệu nhạy cảm - đã loại trừ
- Vector database tự động tạo - không cần push

## Sử dụng:
- Mỗi khi thêm tài liệu mới, chạy lại `process_docs.py`
- Chatbot sẽ trả lời dựa trên tài liệu đã training
- Nếu không tìm thấy thông tin, chatbot sẽ thông báo