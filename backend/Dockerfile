# ---------- Base image ----------
FROM python:3.10-slim

# ---------- Set working directory ----------
WORKDIR /app

# ---------- System dependencies (for OpenCV) ----------
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy backend code ----------
COPY . .

# ---------- Expose FastAPI port ----------
EXPOSE 8000

# ---------- Run FastAPI ----------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
