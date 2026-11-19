import anthropic
from sentence_transformers import SentenceTransformer

from app.claims import extract_claims, keep_grounded_claims
from app.config import Settings
from app.database import open_connection
from app.retrieval import search_articles
from app.verdicts import citation_is_valid, judge_claim

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
with open_connection(settings) as connection:
    for claim in claims:
        articles = search_articles(connection, embedder.encode(claim.statement), EMBEDDING_MODEL, TOP_K)
        verdict, cost = judge_claim(client, claim, articles)
        total_cost += cost
        if not citation_is_valid(verdict, articles):
            # Untraceable evidence must never reach the user as a definitive verdict.
            verdict = verdict.model_copy(update={"verdict": "needs_review"})
            downgraded += 1
        print(f"{verdict.verdict:15} | {verdict.cited_article_id:9} | {claim.statement}")
        print(f"    {verdict.explanation}")

print(f"{len(claims)} claims | downgraded: {downgraded} | cost ${total_cost:.5f}")