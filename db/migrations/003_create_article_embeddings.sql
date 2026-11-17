-- Vectors are derived data: rebuildable from articles.body at any time.
-- One row per (article, model) so a new model never overwrites the baseline.
CREATE TABLE IF NOT EXISTS article_embeddings (
    id BIGSERIAL PRIMARY KEY,
    article_row_id BIGINT NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (article_row_id, model_name)
);