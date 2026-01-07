# GitHub Secrets Setup Guide

## Bước 1: Truy cập GitHub Repository Settings

1. Mở repository trên GitHub
2. Click **Settings** (tab phía trên)
3. Sidebar bên trái → **Secrets and variables** → **Actions**
4. Click nút **New repository secret**

## Bước 2: Thêm các Secrets cần thiết

### Secret 1: DEV_HOST
- **Name**: `DEV_HOST`
- **Value**: IP hoặc domain của server development
- **Ví dụ**: `192.168.1.100` hoặc `dev.example.com`

### Secret 2: DEV_USER
- **Name**: `DEV_USER`
- **Value**: Username SSH để login vào server
- **Ví dụ**: `ubuntu` hoặc `root`

### Secret 3: DEV_SSH_KEY
- **Name**: `DEV_SSH_KEY`
- **Value**: Private SSH key (toàn bộ nội dung file)

**Cách lấy SSH key:**
```bash
# Trên máy local, tạo SSH key nếu chưa có
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Copy nội dung private key
cat ~/.ssh/id_rsa
```

**Copy toàn bộ nội dung từ `-----BEGIN` đến `-----END`:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABlwAAAAdzc2gtcn
...
(nhiều dòng)
...
-----END OPENSSH PRIVATE KEY-----
```

**Sau đó copy public key lên server:**

**Bước 1: Lấy public key trên máy local**
```bash
# Trên máy local (Windows/Mac/Linux)
cat ~/.ssh/id_rsa.pub
# Hoặc trên Windows PowerShell:
type $env:USERPROFILE\.ssh\id_rsa.pub
```

**Bước 2: SSH vào server development**
```bash
# Thay YOUR_SERVER_IP và YOUR_USERNAME
ssh YOUR_USERNAME@YOUR_SERVER_IP
# Ví dụ: ssh ubuntu@192.168.1.100
```

**Bước 3: Thêm public key vào server**
```bash
# Trên server development
mkdir -p ~/.ssh
echo "ssh-rsa AAAA...your-public-key..." >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Server development là gì?**
- Là máy chủ Linux (VPS/EC2/VM) mà bạn muốn deploy ứng dụng lên
- Có thể là:
  - AWS EC2 instance
  - DigitalOcean Droplet
  - Azure VM
  - VPS từ nhà cung cấp khác
  - Máy chủ local trong mạng nội bộ

**Nếu chưa có server development:**
1. Thuê VPS (DigitalOcean, AWS, Vultr...)
2. Hoặc dùng máy local làm server (cài Ubuntu/Linux)
3. Đảm bảo có thể SSH vào được

### Secret 4: GROQ_API_KEY (Optional - nếu cần)
- **Name**: `GROQ_API_KEY`
- **Value**: API key từ Groq
- **Lấy tại**: https://console.groq.com/keys

## Bước 3: Kiểm tra Secrets đã thêm

Sau khi thêm xong, bạn sẽ thấy danh sách:
```
✓ DEV_HOST
✓ DEV_USER
✓ DEV_SSH_KEY
✓ GROQ_API_KEY (optional)
```

## Lưu ý bảo mật

⚠️ **QUAN TRỌNG:**
- Secrets trên GitHub **KHÔNG THỂ XEM LẠI** sau khi lưu
- **KHÔNG** commit secrets vào code
- **KHÔNG** share secrets qua chat/email
- Secrets chỉ được sử dụng trong GitHub Actions workflows

## File .env (Local Development)

File `.env` chỉ dùng cho **local development**, KHÔNG liên quan đến GitHub Secrets:

```bash
# .env - Chỉ dùng trên máy local
GROQ_API_KEY=your_groq_api_key_here
```

**GitHub Secrets** và **file .env** là 2 thứ khác nhau:
- `.env` → Dùng khi chạy local trên máy
- GitHub Secrets → Dùng trong CI/CD pipeline trên GitHub

## Test Deployment

Sau khi setup xong, test bằng cách:
1. Push code lên branch `develop`
2. Vào tab **Actions** trên GitHub
3. Xem workflow chạy và kiểm tra logs
