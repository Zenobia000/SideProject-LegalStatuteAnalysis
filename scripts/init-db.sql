-- 初始化 PostgreSQL 資料庫腳本
-- 國考法律題型分析系統 - 支援向量搜索和法條分析

-- 啟用必要的擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 設定時區
SET timezone = 'Asia/Taipei';

-- 確保資料庫使用 UTF-8 編碼
-- 注意：在 Docker 環境中，資料庫名稱可能不同
-- ALTER DATABASE legal_analysis_db SET client_encoding TO 'UTF8';
-- ALTER DATABASE legal_analysis_db SET default_text_search_config TO 'pg_catalog.simple';

-- 創建向量搜索相關函數
CREATE OR REPLACE FUNCTION create_vector_indexes()
RETURNS void AS $$
BEGIN
    -- 為 legal_articles 表創建向量索引 (如果表存在)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'legal_articles') THEN
        -- 使用 HNSW 索引提高向量搜索性能
        CREATE INDEX IF NOT EXISTS legal_articles_embedding_hnsw_idx 
        ON legal_articles USING hnsw (embedding vector_cosine_ops);
        
        -- 備用：使用 IVFFlat 索引
        -- CREATE INDEX IF NOT EXISTS legal_articles_embedding_ivfflat_idx 
        -- ON legal_articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        
        RAISE NOTICE 'Vector indexes created for legal_articles table';
    ELSE
        RAISE NOTICE 'legal_articles table does not exist yet';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 創建法條文本預處理函數
CREATE OR REPLACE FUNCTION clean_legal_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    -- 清理法條文本：移除多餘空白、標準化格式
    RETURN regexp_replace(
        regexp_replace(
            trim(input_text), 
            '\s+', ' ', 'g'  -- 將多個空白字符替換為單個空格
        ),
        '[\r\n]+', ' ', 'g'  -- 將換行符替換為空格
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;