# 國考法律題型分析系統 - MVP Tech Spec

> **Version**: 1.0  
> **Date**: 2025-08-17  
> **Status**: Draft  
> **Mode**: MVP 快速迭代

---

## 1. 問題陳述與目標用戶

### 核心問題
準備法律相關證照考試的考生，面對**法條難懂的字彙和涵義**，需要快速做到**題型解析**、**對應考點**和**參考出處**的學習需求。

### 目標用戶
- **主要用戶**: 準備國家考試法律科目的考生
- **次要用戶**: 法律補習班講師、法律工作者

### 成功指標（MVP 階段最多 3 條）
1. **功能驗證**: 用戶能成功上傳 PDF 考題並獲得 AI 詳解（成功率 ≥ 90%）
2. **用戶價值**: 平均每題分析時間從 30 分鐘降至 3 分鐘（提升 10x 效率）
3. **系統穩定**: 系統可用性 ≥ 95%，平均響應時間 ≤ 5 秒

---

## 2. 高層設計

### 系統架構一句話
**基於 RAG 的法律文本分析系統**：透過 OCR + NLP 處理法條 PDF，建立知識向量庫，結合生成式 AI 提供題型詳解與考點關聯分析。

### 核心組件圖
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │    │  FastAPI Backend │    │  Vector Database│
│  (用戶介面)     │◄──►│  (API Gateway)   │◄──►│  (法條知識庫)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │  AI Processing   │
                       │  • OCR Engine    │
                       │  • NLP Pipeline  │
                       │  • LLM Inference │
                       └─────────────────┘
```

### 技術棧
- **前端**: React.js + TypeScript
- **後端**: Python FastAPI + AsyncIO
- **AI/ML**: PyTorch + Transformers + LangChain
- **數據庫**: PostgreSQL + Vector Extension (pgvector)
- **文件處理**: PyMuPDF + OCR (PaddleOCR)

---

## 3. 必要 API 契約（核心端點）

### 3.1 文件上傳與處理
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

Request:
- file: PDF 文件
- type: "exam_questions" | "legal_texts"

Response:
{
  "document_id": "uuid",
  "status": "processing",
  "estimated_time": 30
}
```

### 3.2 題型分析
```http
POST /api/v1/analysis/question
Content-Type: application/json

Request:
{
  "document_id": "uuid",
  "question_text": "optional_text_override"
}

Response:
{
  "analysis_id": "uuid",
  "question_analysis": {
    "question_type": "案例分析題",
    "legal_concepts": ["民法第184條", "侵權行為"],
    "difficulty_level": "medium",
    "frequency_score": 0.75
  },
  "detailed_explanation": "...",
  "related_references": [
    {
      "source": "民法第184條",
      "content": "...",
      "relevance_score": 0.9
    }
  ],
  "study_suggestions": [
    "重點複習侵權行為構成要件",
    "練習類似案例題"
  ]
}
```

### 3.3 知識圖譜查詢
```http
GET /api/v1/knowledge/graph?concept=侵權行為&depth=2

Response:
{
  "graph": {
    "nodes": [
      {"id": "侵權行為", "type": "concept", "frequency": 45},
      {"id": "民法第184條", "type": "article", "frequency": 38}
    ],
    "edges": [
      {"source": "侵權行為", "target": "民法第184條", "relation": "legal_basis"}
    ]
  }
}
```

### 3.4 用戶管理
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/user/profile
GET /api/v1/user/history
```

---

## 4. 資料表 Schema

### 4.1 用戶與文件管理
```sql
-- 用戶表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    subscription_type VARCHAR(20) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 文件表
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    processing_status VARCHAR(20) DEFAULT 'uploaded',
    extracted_text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 知識庫與分析結果
```sql
-- 法條知識庫
CREATE TABLE legal_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_code VARCHAR(100) NOT NULL,
    title TEXT,
    content TEXT,
    category VARCHAR(100),
    embedding VECTOR(1536), -- OpenAI embeddings
    frequency_score FLOAT DEFAULT 0
);

-- 分析結果
CREATE TABLE question_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id),
    question_text TEXT,
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 創建向量索引
CREATE INDEX ON legal_articles USING ivfflat (embedding vector_cosine_ops);
```

---

## 5. 風險與手動替代方案

### 5.1 技術風險
| 風險項目 | 影響等級 | 手動替代方案 |
|---------|---------|-------------|
| OCR 準確率不足 | 中 | 人工校對功能，允許用戶編輯 OCR 結果 |
| AI 分析準確率低 | 高 | 建立專家知識庫，回退到規則引擎 |
| 向量搜索延遲高 | 中 | 快取熱門查詢，降級到關鍵字搜索 |

### 5.2 業務風險
| 風險項目 | 影響等級 | 替代方案 |
|---------|---------|----------|
| 用戶上傳量超出預期 | 中 | 實施用量限制，引導付費升級 |
| 法律內容準確性質疑 | 高 | 明確免責聲明，建立反饋機制 |

### 5.3 運維風險
| 風險項目 | 影響等級 | 應急預案 |
|---------|---------|----------|
| AI 服務不可用 | 高 | 多供應商備援，本地模型備用 |
| 數據庫性能問題 | 中 | 讀寫分離，查詢優化 |

---

## 6. MVP 迭代計劃

### 第一迭代（2 週）
- [ ] 基礎文件上傳與 OCR 功能
- [ ] 簡單的文本分析與關鍵字提取
- [ ] 基礎用戶註冊登入

### 第二迭代（2 週）
- [ ] 整合 LLM 進行題型分析
- [ ] 建立基礎法條知識庫
- [ ] 實現相似題目推薦

### 第三迭代（2 週）
- [ ] 知識圖譜可視化
- [ ] 分析結果匯出功能
- [ ] 用戶歷史記錄查詢

---

## 7. 部署與監控

### 最小可運營要求
- **部署**: Docker + Docker Compose 單機部署
- **監控**: 基礎健康檢查端點 `/health`
- **日誌**: 結構化日誌輸出到標準輸出
- **備份**: 每日數據庫備份到雲端儲存

### 關鍵指標監控
- API 響應時間、成功率
- OCR 處理時間與準確率
- 用戶活躍度與留存率

---

**Gate 通過標準**: Tech Spec 被團隊認可；技術可行性驗證完成；MVP 功能範圍明確且可在 6 週內交付。