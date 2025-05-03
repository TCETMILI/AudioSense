# 1. Temel imaj
FROM python:3.10-slim

# 2. Çalışma dizini
WORKDIR /app

# 3. Gereksinimler dosyasını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kodu kopyala
COPY . .

# 5. Gradio port’u expose et
EXPOSE 7860
#    FastAPI port’u expose et
EXPOSE 8000

# 6. Uvicorn + Gradio’yı aynı anda çalıştırmak için tini
RUN pip install --no-cache-dir multitool

# 7. Başlatma komutu: önce backend, sonra frontend
CMD ["multitool", \
     "run", "uvicorn backend:app --host 0.0.0.0 --port 8000", \
     "run", "python frontend.py --server.port 7860 --server.host 0.0.0.0" \
    ]
