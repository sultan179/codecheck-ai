import psycopg
from pydantic import BaseModel
from app.claims import ExtractedClaim
from app.verdicts import Verdict

INSERT_REVIEW_SQL="""
INSERT INTO reviews (document_name, document_text, llm_model,
embedding_model, total_cost_usd)
VALUES (%s, %s, %s, %s, %s)
RETURNING id
"""

INSERT_REVIEW_ITEM_SQL="""
INSERT INTO review_items (review_id,
claim_statement, source_quote,
retrieved_article_ids, model_verdict,
verdict, citation_check_passed,
cited_article_id, evidence_quote, explanation
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

class ReviewItem(BaseModel):
    claim: ExtractedClaim
    retrieved_article_ids: list[str]
    model_verdict: str
    final_verdict: Verdict
    citation_check_passed: bool


def save_review(connection: psycopg.Connection,document_name:str, document_text:str, llm_model:str,
                embedding_model:str, total_cost:float, items:list[ReviewItem]
                )->int:
    row=connection.execute(INSERT_REVIEW_SQL, (document_name,document_text, llm_model, 
                                               embedding_model, total_cost)).fetchone()
    review_id=row[0]
    for item in items:
        verdict=item.final_verdict
        connection.execute(INSERT_REVIEW_ITEM_SQL, (
            review_id, item.claim.statement, item.claim.source_quote,
            item.retrieved_article_ids, item.model_verdict, verdict.verdict,
            item.citation_check_passed, verdict.cited_article_id,
            verdict.evidence_quote, verdict.explanation,
        ))
    return review_id

    