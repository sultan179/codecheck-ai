import anthropic
from sentence_transformers import SentenceTransformer

from app.claims import extract_claims, keep_grounded_claims
from app.config import Settings
from app.database import open_connection
from app.retrieval import search_articles
from app.verdicts import citation_is_valid, judge_claim
from app.llm import LLM_MODEL
from app.review_store import ReviewItem, save_review

SPEC_NAME = "spec_001"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
SPEC_PATH = "data/specs/spec_001.md"
TOP_K = 3

settings = Settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
embedder = SentenceTransformer(EMBEDDING_MODEL, device="cpu")
with open(SPEC_PATH) as spec_file:
    spec_text = spec_file.read()

claim_list, total_cost = extract_claims(client, spec_text)
claims = keep_grounded_claims(claim_list.claims, spec_text)
downgraded = 0
items = []
with open_connection(settings) as connection:
    for claim in claims:
        articles = search_articles(connection, embedder.encode(claim.statement), EMBEDDING_MODEL, TOP_K)
        verdict, cost = judge_claim(client, claim, articles)
        total_cost += cost
        model_verdict = verdict.verdict
        citation_ok = citation_is_valid(verdict, articles)
        if not citation_ok:
            # Untraceable evidence must never reach the user as a definitive verdict.
            verdict = verdict.model_copy(update={"verdict": "needs_review"})
            downgraded += 1
        retrieved_ids = []
        for article in articles:
            retrieved_ids.append(article.article_id)
        items.append(ReviewItem(claim=claim, retrieved_article_ids=retrieved_ids,
                                model_verdict=model_verdict, final_verdict=verdict,
                                citation_check_passed=citation_ok))
        print(f"{verdict.verdict:15} | {verdict.cited_article_id:9} | {claim.statement}")
    review_id = save_review(connection, SPEC_NAME, spec_text, LLM_MODEL,
                            EMBEDDING_MODEL, total_cost, items)

print(f"saved review {review_id} | {len(claims)} claims | downgraded: {downgraded} | cost ${total_cost:.5f}")