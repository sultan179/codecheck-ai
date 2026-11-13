CREATE TABLE IF NOT EXISTS articles (
    id               BIGSERIAL PRIMARY KEY,
    doc_type         TEXT NOT NULL DEFAULT 'code',
    jurisdiction     TEXT NOT NULL DEFAULT 'AB',
    edition          TEXT NOT NULL,
    article_id       TEXT NOT NULL,
    title            TEXT NOT NULL,
    body             TEXT NOT NULL,
    cross_references TEXT[] NOT NULL DEFAULT '{}',
    source_page      INTEGER NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (edition, article_id)
);