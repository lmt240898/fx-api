# Chọn base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a directory for the app code and set it as the working directory
WORKDIR /code

# Set python path to the code directory so it can find the 'app' package
ENV PYTHONPATH=/code

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into a subdirectory named 'app'
COPY ./app ./app

# Mở cổng cần thiết
EXPOSE 8000

# Chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
