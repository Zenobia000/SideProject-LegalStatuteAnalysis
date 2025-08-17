# ADR 使用說明（docs/dev/adr）

## 目錄位置與命名
- 位置：`docs/dev/adr/`
- 檔名：`ADR-<序號三位>-<kebab-slug>.md` 例如：`ADR-001-upload-size-limit.md`
- 標題：檔內第一行與檔名一致（可簡述）

## 何時需要 ADR
- 涉及設計權衡/技術選型/契約變更（API/Schema/版本策略/安全）
- 涉及跨團隊影響或中高成本影響（基礎設施、可觀測性、部署策略）
- 任何需要追溯或未來可能被重新評估的決策

## 模板
- 使用：`開發遵循文件/01_adr_template.md`
- 關鍵欄位：Context、Options（含成本/複雜度）、Decision、Consequences（含重評觸發）、Implementation Outline

## 流程（建議）
1. 在分支中新增 `docs/dev/adr/ADR-xxx-<slug>.md`
2. 在 PR 中引用該 ADR；在相關文件（`mvp_tech_spec.md`、`system_design_document.md`、`development_progress_report.md`）回填 ADR 編號
3. 決策接受後，將 ADR 狀態標記為 Accepted；若被取代，更新為 Superseded 並指向新 ADR

## 與進度報告/Spec 的連結
- 進度報告的「變更摘要 / Spec 差異追蹤」表需填入 ADR 編號（若屬設計/選型/契約層級）
- Spec/SDD 的「技術選型詳述/對應表」中維護 ADR 連結，確保溯源一致
