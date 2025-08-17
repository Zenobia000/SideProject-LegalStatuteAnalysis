# 國考法律題型分析系統

**結合生成式 AI 和資訊系統整合的法律題型分析平台**

## Quick Start

1. **Read CLAUDE.md first** - Contains essential rules for Claude Code
2. Follow the pre-task compliance checklist before starting any work
3. Use proper module structure under `src/main/python/`
4. Commit after every completed task

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

## 環境設置

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 啟動 Jupyter Lab
jupyter lab notebooks/
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