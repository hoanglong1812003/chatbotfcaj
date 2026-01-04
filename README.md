# First Cloud Journey Assistant

## Hướng dẫn setup:

### 1. Clone repository:
```bash
git clone https://github.com/hoanglong1812003/chatbotfcaj.git
cd chatbotfcaj
```

### 2. Cài đặt packages:
```bash
pip install -r requirements.txt
```

### 3. Cấu hình API key:
```bash
cp .env.example .env
# Chỉnh sửa .env và thêm GROQ_API_KEY
```

### 4. Chuẩn bị dữ liệu:
- Tạo thư mục `data/`
- Đặt tài liệu PDF/TXT vào thư mục `data/`
- Ví dụ: AWS documentation, slide bài giảng, FAQ...

### 5. Xử lý tài liệu:
```bash
python process_docs.py
```

### 6. Chạy chatbot:
```bash
streamlit run app.py
```

## Cấu trúc thư mục:
```
├── data/                 # Tài liệu training (không push lên git)
├── vectorstore/          # Vector database (tự động tạo, không push)
├── app.py               # Ứng dụng chính
├── process_docs.py      # Script xử lý tài liệu
├── requirements.txt     # Dependencies
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