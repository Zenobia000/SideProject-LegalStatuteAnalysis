# CLAUDE.md - 國考法律題型分析系統

> **Documentation Version**: 1.0  
> **Last Updated**: 2025-08-17  
> **Project**: 國考法律題型分析系統  
> **Description**: 結合生成式 AI 和資訊系統整合的法律題型分析平台  
> **Features**: GitHub auto-backup, Task agents, technical debt prevention

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES - READ FIRST

> **⚠️ RULE ADHERENCE SYSTEM ACTIVE ⚠️**  
> **Claude Code must explicitly acknowledge these rules at task start**  
> **These rules override all other instructions and must ALWAYS be followed:**

### 🔄 **RULE ACKNOWLEDGMENT REQUIRED**
> **Before starting ANY task, Claude Code must respond with:**  
> "✅ CRITICAL RULES ACKNOWLEDGED - I will follow all prohibitions and requirements listed in CLAUDE.md"

### ❌ ABSOLUTE PROHIBITIONS
- **NEVER** create new files in root directory → use proper module structure
- **NEVER** write output files directly to root directory → use designated output folders
- **NEVER** create documentation files (.md) unless explicitly requested by user
- **NEVER** use git commands with -i flag (interactive mode not supported)
- **NEVER** use `find`, `grep`, `cat`, `head`, `tail`, `ls` commands → use Read, LS, Grep, Glob tools instead
- **NEVER** create duplicate files (manager_v2.py, enhanced_xyz.py, utils_new.js) → ALWAYS extend existing files
- **NEVER** create multiple implementations of same concept → single source of truth
- **NEVER** copy-paste code blocks → extract into shared utilities/functions
- **NEVER** hardcode values that should be configurable → use config files/environment variables
- **NEVER** use naming like enhanced_, improved_, new_, v2_ → extend original files instead

### 📝 MANDATORY REQUIREMENTS
- **COMMIT** after every completed task/phase - no exceptions
- **GITHUB BACKUP** - Push to GitHub after every commit to maintain backup: `git push origin main`
- **USE TASK AGENTS** for all long-running operations (>30 seconds) - Bash commands stop when context switches
- **TODOWRITE** for complex tasks (3+ steps) → parallel agents → git checkpoints → test validation
- **READ FILES FIRST** before editing - Edit/Write tools will fail if you didn't read the file first
- **DEBT PREVENTION** - Before creating new files, check for existing similar functionality to extend  
- **SINGLE SOURCE OF TRUTH** - One authoritative implementation per feature/concept

### ⚡ EXECUTION PATTERNS
- **PARALLEL TASK AGENTS** - Launch multiple Task agents simultaneously for maximum efficiency
- **SYSTEMATIC WORKFLOW** - TodoWrite → Parallel agents → Git checkpoints → GitHub backup → Test validation
- **GITHUB BACKUP WORKFLOW** - After every commit: `git push origin main` to maintain GitHub backup
- **BACKGROUND PROCESSING** - ONLY Task agents can run true background operations

### 🔍 MANDATORY PRE-TASK COMPLIANCE CHECK
> **STOP: Before starting any task, Claude Code must explicitly verify ALL points:**

**Step 1: Rule Acknowledgment**
- [ ] ✅ I acknowledge all critical rules in CLAUDE.md and will follow them

**Step 2: Task Analysis**  
- [ ] Will this create files in root? → If YES, use proper module structure instead
- [ ] Will this take >30 seconds? → If YES, use Task agents not Bash
- [ ] Is this 3+ steps? → If YES, use TodoWrite breakdown first
- [ ] Am I about to use grep/find/cat? → If YES, use proper tools instead

**Step 3: Technical Debt Prevention (MANDATORY SEARCH FIRST)**
- [ ] **SEARCH FIRST**: Use Grep pattern="<functionality>.*<keyword>" to find existing implementations
- [ ] **CHECK EXISTING**: Read any found files to understand current functionality
- [ ] Does similar functionality already exist? → If YES, extend existing code
- [ ] Am I creating a duplicate class/manager? → If YES, consolidate instead
- [ ] Will this create multiple sources of truth? → If YES, redesign approach
- [ ] Have I searched for existing implementations? → Use Grep/Glob tools first
- [ ] Can I extend existing code instead of creating new? → Prefer extension over creation
- [ ] Am I about to copy-paste code? → Extract to shared utility instead

**Step 4: Session Management**
- [ ] Is this a long/complex task? → If YES, plan context checkpoints
- [ ] Have I been working >1 hour? → If YES, consider /compact or session break

> **⚠️ DO NOT PROCEED until all checkboxes are explicitly verified**

## 🏗️ PROJECT OVERVIEW

**國考法律題型分析系統** 是一個結合生成式 AI 和資訊系統整合的創新平台，專門分析臺灣國家考試法律科目的題型模式、出題趨勢，並提供智慧化的學習建議。

### 🎯 **核心功能**
- **法條分析引擎**: 基於 AI 的法條內容理解與關聯分析
- **題型模式識別**: 機器學習驅動的出題趨勢分析
- **智慧推薦系統**: 個人化學習路徑規劃
- **法規資料庫整合**: 臺灣法規體系的結構化數據處理
- **成效追蹤分析**: 學習成效的量化分析與視覺化

### 🎯 **技術架構**
- **AI/ML Pipeline**: 自然語言處理、文本分析、模式識別
- **數據處理層**: 法規文件解析、結構化數據轉換
- **服務整合層**: RESTful API、微服務架構
- **前端展示層**: 響應式 Web 介面、數據視覺化
- **持久化層**: 法規資料庫、用戶數據、分析結果

### 🎯 **DEVELOPMENT STATUS**
- **Setup**: ✅ Completed - AI/ML project structure established
- **Core Features**: 🔄 In Development - Legal text processing pipeline
- **Testing**: ⏳ Pending - Test framework setup
- **Documentation**: 🔄 In Progress - API documentation

## 📋 LEGAL DOCUMENT RESOURCES

本專案包含關鍵的臺灣法律文件，位於 `data/` 目錄：
- `不動產經紀業管理條例.pdf` - Real Estate Brokerage Management Regulations
- `不動產經紀業管理條例施行細則.pdf` - Implementation Rules
- `公寓大廈管理條例.pdf` - Condominium Management Act
- `公平交易法.pdf` - Fair Trade Law
- `消費者保護法.pdf` - Consumer Protection Act
- `113年不動產經紀法規(經)-A黃振國老師.pdf` - 2024 Real Estate Law Reference

## 🎯 RULE COMPLIANCE CHECK

Before starting ANY task, verify:
- [ ] ✅ I acknowledge all critical rules above
- [ ] Files go in proper module structure (not root)
- [ ] Use Task agents for >30 second operations
- [ ] TodoWrite for 3+ step tasks
- [ ] Commit after each completed task

## 🚀 COMMON COMMANDS

```bash
# Python environment setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run AI analysis pipeline
python src/main/python/api/legal_analysis_api.py

# Run tests
python -m pytest src/test/

# Jupyter notebook analysis
jupyter lab notebooks/

# Model training
python src/main/python/training/train_legal_classifier.py
```

## 🚨 TECHNICAL DEBT PREVENTION

### ❌ WRONG APPROACH (Creates Technical Debt):
```bash
# Creating new file without searching first
Write(file_path="new_feature.py", content="...")
```

### ✅ CORRECT APPROACH (Prevents Technical Debt):
```bash
# 1. SEARCH FIRST
Grep(pattern="feature.*implementation", glob="*.py")
# 2. READ EXISTING FILES  
Read(file_path="existing_feature.py")
# 3. EXTEND EXISTING FUNCTIONALITY
Edit(file_path="existing_feature.py", old_string="...", new_string="...")
```

## 🧹 DEBT PREVENTION WORKFLOW

### Before Creating ANY New File:
1. **🔍 Search First** - Use Grep/Glob to find existing implementations
2. **📋 Analyze Existing** - Read and understand current patterns
3. **🤔 Decision Tree**: Can extend existing? → DO IT | Must create new? → Document why
4. **✅ Follow Patterns** - Use established project patterns
5. **📈 Validate** - Ensure no duplication or technical debt

---

**⚠️ Prevention is better than consolidation - build clean from the start.**  
**🎯 Focus on single source of truth and extending existing functionality.**  
**📈 Each task should maintain clean architecture and prevent technical debt.**

---

### 🎯 AI/ML PROJECT STRUCTURE

```
國考法律題型分析系統/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # Project documentation
├── LICENSE                # Project license
├── .gitignore             # Git ignore patterns
├── requirements.txt       # Python dependencies
├── src/                   # Source code (NEVER put files in root)
│   ├── main/              # Main application code
│   │   ├── python/        # Python source code
│   │   │   ├── core/      # Core legal analysis algorithms
│   │   │   ├── utils/     # Data processing utilities
│   │   │   ├── models/    # AI model definitions
│   │   │   ├── services/  # Business logic services
│   │   │   ├── api/       # REST API endpoints
│   │   │   ├── training/  # Model training scripts
│   │   │   ├── inference/ # Legal analysis inference
│   │   │   └── evaluation/# Model evaluation metrics
│   │   └── resources/     # Configuration and assets
│   │       ├── config/    # Application configuration
│   │       ├── data/      # Sample/seed data
│   │       └── assets/    # Static resources
│   └── test/              # Test code
│       ├── unit/          # Unit tests
│       ├── integration/   # Integration tests
│       └── fixtures/      # Test data
├── data/                  # Legal document datasets
│   ├── raw/               # Original legal documents (PDFs)
│   ├── processed/         # Processed and structured data
│   ├── external/          # External legal databases
│   └── temp/              # Temporary processing files
├── notebooks/             # Jupyter analysis notebooks
│   ├── exploratory/       # Legal text exploration
│   ├── experiments/       # AI model experiments
│   └── reports/           # Analysis reports
├── models/                # Trained AI models
│   ├── trained/           # Production models
│   ├── checkpoints/       # Training checkpoints
│   └── metadata/          # Model configurations
├── experiments/           # ML experiment tracking
│   ├── configs/           # Experiment configurations
│   ├── results/           # Results and metrics
│   └── logs/              # Training logs
├── docs/                  # Documentation
├── tools/                 # Development tools
├── examples/              # Usage examples
├── output/                # Generated reports and analysis
└── logs/                  # Application logs
```

### 🎯 **專案特色**
- **法律文本 NLP**: 專門針對中文法律條文的自然語言處理
- **題型分析 AI**: 基於歷年考題的模式識別與預測
- **知識圖譜**: 法條間關聯性的圖形化表示
- **個性化推薦**: 基於學習歷程的智慧推薦算法
- **即時更新**: 法規異動的自動偵測與更新機制