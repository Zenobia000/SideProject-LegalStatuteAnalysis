# 國考法律題型分析系統 - FastAPI Docker Image
# 支持 PDF 處理、OCR 識別、AI 分析

FROM python:3.11-slim

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴 (OCR 和 PDF 處理所需)
RUN apt-get update && apt-get install -y \
    # 基本工具
    curl \
    wget \
    # OCR 相關依賴
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    tesseract-ocr-chi-sim \
    libtesseract-dev \
    # 圖像處理
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # PDF 處理
    poppler-utils \
    # 清理快取
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 安裝 Poetry
RUN pip install poetry==1.6.1

# 配置 Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# 複製依賴文件
COPY pyproject.toml poetry.lock ./

# 安裝 Python 依賴
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# 複製應用程式碼
COPY . .

# 創建必要的目錄
RUN mkdir -p /app/data/uploads /app/logs /app/data/temp

# 設定權限
RUN chown -R nobody:nogroup /app/data /app/logs

# 切換到非 root 用戶
USER nobody

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["poetry", "run", "uvicorn", "src.main.python.main:app", "--host", "0.0.0.0", "--port", "8000"]