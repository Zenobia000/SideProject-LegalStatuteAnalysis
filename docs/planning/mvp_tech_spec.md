# 國考法律題型分析系統 - MVP Tech Spec

> **Version**: 1.1  
> **Date**: 2025-08-17  
> **Status**: Draft  
> **Mode**: MVP 快速迭代  
> **Owner(s)**: 產品經理, 技術負責人  
> **Reviewers**: 架構師, SRE  

---

## 0. 溯源與對齊（Traceability）
- 來源文件：
  - PRD：`docs/planning/project_brief_prd_summary.md`
  - SA：`開發遵循文件/02_system_architecture_document_template.md`
  - SDD：`開發遵循文件/03_system_design_document_template.md`
- 覆蓋範圍：本 Tech Spec 為 MVP 的唯一實作契約；如與其他文件衝突，以本文件為準。重大設計權衡另建 `01_adr_template.md` 條目並在本文引用。

---

## 1. 問題陳述與目標用戶

### 核心問題
準備法律相關證照考試的考生，面對**法條難懂的字彙和涵義**，需要快速做到**題型解析**、**對應考點**和**參考出處**的學習需求。

### 目標用戶
- **主要用戶**: 準備國家考試法律科目的考生
- **次要用戶**: 法律補習班講師、法律工作者

### 成功指標（MVP 階段最多 3 條）
1. **功能驗證**: 上傳 PDF 並獲得 AI 詳解成功率 ≥ 90%
2. **用戶價值**: 平均每題分析時間 ≤ 3 分鐘（從 30 分鐘降至 3 分鐘）
3. **系統穩定**: 可用性 ≥ 95%，API 平均響應時間 ≤ 5 秒

- 非目標（Out of Scope）：支付、多人協作、權限分層、完整知識圖譜編輯器

---

## 2. 高層設計

### 2.1 系統架構一句話
**基於 RAG 的法律文本分析系統**：透過 OCR + NLP 處理法條 PDF，建立知識向量庫，結合生成式 AI 提供題型詳解與考點關聯分析。

### 2.2 核心組件圖
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

### 2.3 組件職責表
| 組件 | 職責 | 關鍵輸入 | 關鍵輸出 |
| :-- | :-- | :-- | :-- |
| Frontend | 上傳/呈現/互動 | PDF 檔、使用者操作 | API 請求/回應渲染 |
| API Gateway (FastAPI) | 路由、驗證、契約落地 | 前端請求、JWT | 標準化回應、錯誤碼 |
| OCR Engine | 影像文字擷取 | PDF | 純文字內容 |
| NLP Pipeline | 文本清理/切分 | OCR 文本 | 段落、索引單位 |
| Vector DB | 向量索引/檢索 | 文章嵌入 | 相似片段與分數 |
| LLM Inference | 生成詳解/要點 | 提示、檢索結果 | 詳解、參考法條 |

### 2.4 前端範圍與路由/頁面
| 頁面 | 路由 | 主要功能 | 依賴 API | 核心組件 |
| :-- | :-- | :-- | :-- | :-- |
| 上傳頁 | `/upload` | 上傳 PDF、顯示處理狀態 | `POST /api/v1/documents/upload`、`GET /api/v1/documents/{id}` | `UploadForm`, `StatusBadge` |
| 分析結果頁 | `/analysis/:id` | 顯示題型分析、詳解、參考法條 | `POST /api/v1/analysis/question`、`GET /api/v1/user/history` | `AnalysisView`, `ReferenceList` |
| 歷史記錄頁 | `/history` | 列出歷史分析紀錄、重看詳解 | `GET /api/v1/user/history` | `HistoryTable` |
| 登入/註冊頁 | `/auth/login`, `/auth/register` | 用戶登入/註冊 | `POST /api/v1/auth/login`、`POST /api/v1/auth/register` | `AuthForm` |

- 前端狀態管理：React Query（或等價方案）管理 API 請求與快取
- UI 規範：字體、色票、錯誤提示一致化（MVP 可簡化為系統預設）

---

## 3. 必要 API 契約（核心端點）

> 標準：URL 版本化（/api/v1）、JSON 回應、錯誤物件統一、Idempotency-Key（適用創建類請求）、速率限制 100 req/min/IP。

### 3.1 文件上傳與處理
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data
Authorization: Bearer <JWT>
Idempotency-Key: <uuid>  # 建議

Request:
- file: PDF 文件
- type: "exam_questions" | "legal_texts"

Response 202:
{ "document_id": "uuid", "status": "processing", "estimated_time": 30 }

Errors:
- 400 parameter_invalid
- 401 authentication_failed
- 413 payload_too_large
- 500 internal_server_error
```

### 3.2 題型分析
```http
POST /api/v1/analysis/question
Content-Type: application/json
Authorization: Bearer <JWT>
Idempotency-Key: <uuid>

Request:
{ "document_id": "uuid", "question_text": "optional_text_override" }

Response 200:
{ "analysis_id": "uuid", "question_analysis": { ... }, "detailed_explanation": "...", "related_references": [ ... ], "study_suggestions": [ ... ] }

Errors:
- 400 parameter_missing/invalid
- 404 resource_not_found (document)
- 422 idempotency_key_reused
- 500 internal_server_error
```

### 3.3 知識圖譜查詢
```http
GET /api/v1/knowledge/graph?concept=侵權行為&depth=2
Authorization: Bearer <JWT>

Response 200:
{ "graph": { "nodes": [ ... ], "edges": [ ... ] } }
```

### 3.4 用戶管理
```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/user/profile
GET  /api/v1/user/history
```

### 3.5 API 通用規範
- 錯誤物件格式：
```json
{ "error": { "code": "parameter_invalid", "message": "...", "field": "file", "request_id": "..." } }
```
- 分頁：`?page=1&page_size=20`；排序：`?sort=-created_at`
- Idempotency：採 `Idempotency-Key` header；服務端保存 24h 去重
- 速率限制：每 IP 100 req/min；超限回 429，`Retry-After` 秒數
- 版本控制：URL Path `/v1`；棄用以 `Deprecation` header 通知（至少 30 天）

---

## 4. 資料模型與字典（Schema & Dictionary）

### 4.1 用戶與文件管理（關聯簡述）
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  subscription_type VARCHAR(20) DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW()
);

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
CREATE TABLE legal_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_code VARCHAR(100) NOT NULL,
  title TEXT,
  content TEXT,
  category VARCHAR(100),
  embedding VECTOR(1536),
  frequency_score FLOAT DEFAULT 0
);

CREATE TABLE question_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES documents(id),
  question_text TEXT,
  analysis_result JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON legal_articles USING ivfflat (embedding vector_cosine_ops);
```

### 4.3 數據字典（節選）
| 表 | 欄位 | 型別 | 描述 |
| :-- | :-- | :-- | :-- |
| users | email | varchar(255) | 登入識別（PII） |
| documents | processing_status | varchar(20) | uploaded/processing/done/failed |
| legal_articles | embedding | vector(1536) | 文章向量（不可導出） |
| question_analyses | analysis_result | jsonb | 包含詳解、法條參考、建議 |

- 保留策略：分析結果與上傳檔案保存 90 天；PII（email）遵守刪除請求處理（7 天內）

---

## 5. 非功能需求（NFR）與性能預算
- 可用性：≥ 95%（MVP）
- 延遲：API 平均響應 ≤ 5 秒；文件上傳 10MB 限制
- 併發：同時 5+ 用戶無錯；隊列化 OCR 任務避免資源爭用
- 可擴展：先垂直擴展，必要時引入背景任務隊列（ADR-Queue）
- 容錯：外部 AI 失效時提供降級（僅檢索與規則解釋）

---

## 6. 安全與隱私
- 認證：JWT（HS256）；`Authorization: Bearer <token>`；存活 24h
- 授權：MVP 單租戶單角色；管理端後續規劃
- 輸入驗證：檔案類型白名單（pdf），大小 ≤ 10MB
- Secrets：環境變數管理，不入庫/不入版控
- CORS：限制來源清單（本地 + 預設前端域）
- 日誌打點：避免紀錄 PDF 內容與 PII
- 隱私分類：email 屬 PII；上傳 PDF 可能含敏感資料，禁止外洩到第三方日誌/遙測
- 法遵：加入免責聲明；提供刪除請求處理流程

---

## 7. 可觀測性與錯誤處理
- 日誌：結構化（JSON）；關鍵欄位：`request_id`, `user_id`, `endpoint`, `latency_ms`, `error.code`
- 指標（Metrics）：`http_requests_total`, `http_request_duration_ms`, `ocr_job_duration_ms`, `llm_inference_duration_ms`, `rate_limit_hits`
- 追蹤：為主要 API 與 OCR/LLM 任務建立 trace/span（可選）
- 錯誤處理：使用統一錯誤碼表；5xx 自動告警（Slack/Email）

---

## 8. Gate 通過標準
- Tech Spec 完成並審閱通過（Owner/Reviewers 簽核）
- 技術可行性驗證完成（PoC/Spike）
- MVP 功能可在 6 週內交付（3 個 2 週迭代）
- 風險與替代方案明確（降級策略）
- 部署與監控最小要求可落地（/health、日誌、每日備份）

---

## 9. 環境與部署策略
- 本地：SQLite 可選（開發便利）；
- 生產：PostgreSQL + pgvector；每日自動備份；容器化（Docker Compose 單機）
- 組態：`.env` + Secrets；差異化變數：DB_URL、AI_API_KEY、RATE_LIMIT
- 回滾：以容器標籤回滾；資料庫 schema 變更需提供 down 腳本

---

## 10. 測試計畫與驗收標準（DoD）
- 單元：服務/工具層（最小關鍵路徑）
- 整合：上傳→OCR→檢索→詳解 端到端
- 錯誤路徑：非 PDF、超大文件、OCR 失敗、AI 超時
- 安全：基本認證/授權測試；Secrets 不出現在日誌
- 效能：認證端點 p50 < 200ms；分析端點在樣例下 ≤ 5 秒
- 驗收（每端點）：契約測試（請求/回應/錯誤碼）通過即視為完成

---

## 11. 依賴、假設與外部系統
- 外部：OpenAI/Anthropic（LLM），OCR 引擎（PaddleOCR/Tesseract）
- 假設：可使用網路服務；法條資料可合法載入
- 風險：外部 API 限流/費用；備援：本地模型/緩存策略

---

## 12. 版本控制與棄用策略
- 版本：URL `/v1`；重大破壞性變更升級 `/v2`
- 棄用：`Deprecation` header + 文件公告，至少 30 天日落期

---

## 13. 變更管理與 ADR
- 重大決策建立 ADR（技術選型、儲存、隊列、觀測方案）
- 本文件每次更新需寫入變更摘要並對應 PR/Issue

---

## 14. Traceability Matrix（PRD → Spec → API/Schema）
| 用例/故事（PRD） | Spec 條目 | API/Schema |
| :-- | :-- | :-- |
| 上傳 PDF 並獲得詳解 | 3.1/3.2/4.1/10 | `POST /documents/upload`、`POST /analysis/question`、`documents`、`question_analyses` |
| 查詢關聯法條 | 3.3/4.2 | `GET /knowledge/graph`、`legal_articles` |

---

本 Tech Spec 與 `開發遵循文件/產品開發流程使用說明書.md` 第 8 節之規範一致。任何新增端點或資料表，請遵循本文件之章節順序與表示法，並同步更新 Traceability Matrix 與 KPI。