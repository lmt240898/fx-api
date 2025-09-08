# Chọn base image
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt và cài đặt dependencies
COPY requirements.txt .

# Cài đặt FastAPI và các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn vào thư mục làm việc
COPY ./app /app

# Mở cổng cần thiết
EXPOSE 8000

# Chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
