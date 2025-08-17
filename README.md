# 國考法律題型分析系統

**結合生成式 AI 和資訊系統整合的法律題型分析平台**

## 🚀 Quick Start

### 📋 開發狀態
**當前版本**: v0.1.0 (MVP 開發中)  
**完成度**: 80% (第一迭代)  
**運行狀態**: ✅ 本地開發環境運行中

### 🏃‍♂️ 快速啟動
```bash
# 1. 克隆專案
git clone [repository-url]
cd LegalStatuteAnalysis

# 2. 安裝依賴 (使用 Poetry)
poetry install

# 3. 配置環境變數
cp .env.example .env
# 編輯 .env 填入必要配置

# 4. 初始化資料庫
poetry run python -c "from src.main.python.core.database_init import initialize_database; initialize_database()"

# 5. 啟動 API 服務
poetry run uvicorn src.main.python.main:app --host 0.0.0.0 --port 8000 --reload

# 6. 查看 API 文檔
# 瀏覽器開啟: http://localhost:8000/docs
```

### ✅ 已實現功能
- 🔐 **用戶認證系統** - JWT 登入/註冊/驗證
- 🗄️ **資料庫架構** - 完整 ORM 模型 (4張核心表)
- 🌐 **REST API 基礎** - FastAPI + 自動 Swagger 文檔
- ⚙️ **系統配置** - 環境管理 + 結構化日誌

### 🔄 開發中功能  
- 📄 **文件處理服務** (下個任務)
- 🤖 **AI 分析引擎** (規劃中)
- 📚 **法條知識庫** (規劃中)

## 專案概述

國考法律題型分析系統是一個創新的 AI 驅動平台，專門分析臺灣國家考試法律科目的題型模式、出題趨勢，並提供智慧化的學習建議。

### 🎯 核心功能

- **法條分析引擎**: 基於 AI 的法條內容理解與關聯分析
- **題型模式識別**: 機器學習驅動的出題趨勢分析
- **智慧推薦系統**: 個人化學習路徑規劃
- **法規資料庫整合**: 臺灣法規體系的結構化數據處理
- **成效追蹤分析**: 學習成效的量化分析與視覺化

### 🏗️ 技術架構

- **AI/ML Pipeline**: 自然語言處理、文本分析、模式識別
- **數據處理層**: 法規文件解析、結構化數據轉換
- **服務整合層**: RESTful API、微服務架構
- **前端展示層**: 響應式 Web 介面、數據視覺化
- **持久化層**: 法規資料庫、用戶數據、分析結果

## 專案結構

```
國考法律題型分析系統/
├── src/main/python/       # Python 核心代碼
│   ├── core/              # 核心法律分析算法
│   ├── utils/             # 數據處理工具
│   ├── models/            # AI 模型定義
│   ├── services/          # 業務邏輯服務
│   ├── api/               # REST API 端點
│   ├── training/          # 模型訓練腳本
│   ├── inference/         # 法律分析推理
│   └── evaluation/        # 模型評估指標
├── data/                  # 法律文件數據集
├── notebooks/             # Jupyter 分析筆記本
├── models/                # 訓練好的 AI 模型
├── experiments/           # ML 實驗追蹤
└── docs/                  # 項目文檔
```

## 🔧 開發環境需求

### 系統需求
- **Python**: 3.11+
- **Poetry**: 1.5+ (依賴管理)
- **資料庫**: SQLite (開發) / PostgreSQL (生產)
- **作業系統**: Windows/macOS/Linux

### 開發工具
```bash
# Poetry 安裝 (如未安裝)
curl -sSL https://install.python-poetry.org | python3 -

# 開發環境設置
poetry install --with dev

# 代碼格式化
poetry run black src/
poetry run isort src/

# 啟動 Jupyter (可選)
poetry run jupyter lab notebooks/
```

### 🧪 測試
```bash
# 單元測試 (規劃中)
poetry run pytest src/test/

# API 測試
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

## 開發指南

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating  
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - works with Python, JS, Java, etc.
- **Scalable** - start simple, grow as needed
- **Flexible** - choose complexity level based on project needs

## 法律文件資源

本專案包含關鍵的臺灣法律文件：
- `不動產經紀業管理條例.pdf`
- `公寓大廈管理條例.pdf`
- `公平交易法.pdf`
- `消費者保護法.pdf`
- `113年不動產經紀法規.pdf`

## 貢獻指南

1. 遵循 CLAUDE.md 中的開發規範
2. 使用 AI/ML 專案結構
3. 編寫完整的測試用例
4. 更新相應的文檔

## 授權

[待添加授權信息]