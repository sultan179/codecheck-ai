-- One row per review run: what was checked, with which models, at what cost.
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    document_type TEXT NOT NULL DEFAULT 'spec',
    document_name TEXT NOT NULL,
    document_text TEXT NOT NULL,
    llm_model TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    total_cost_usd NUMERIC(10, 6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per claim: the evidence, what the model said, and what we kept.
CREATE TABLE IF NOT EXISTS review_items (
    id BIGSERIAL PRIMARY KEY,
    review_id BIGINT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    claim_statement TEXT NOT NULL,
    source_quote TEXT NOT NULL,
    retrieved_article_ids TEXT[] NOT NULL,
    model_verdict TEXT NOT NULL
        CHECK (model_verdict IN ('potential_issue', 'no_issue_found', 'needs_review')),
    verdict TEXT NOT NULL
        CHECK (verdict IN ('potential_issue', 'no_issue_found', 'needs_review')),
    citation_check_passed BOOLEAN NOT NULL,
    cited_article_id TEXT NOT NULL,
    evidence_quote TEXT NOT NULL,
    explanation TEXT NOT NULL
);