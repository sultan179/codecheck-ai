from sentence_transformers import SentenceTransformer

from app.config import Settings
from app.database import open_connection
from app.retrieval import search_articles
from eval_questions import EVAL_QUESTIONS

MODEL_NAME = "BAAI/bge-small-en-v1.5"
# Ask for every article, so we learn the expected one's rank, not just the top 3.
RANK_ALL = 100

settings = Settings()
model = SentenceTransformer(MODEL_NAME, device="cpu")
hits_at_1 = 0
hits_at_3 = 0
with open_connection(settings) as connection:
    for question, expected_id in EVAL_QUESTIONS:
        results = search_articles(connection, model.encode(question), MODEL_NAME, RANK_ALL)
        ranked_ids = []
        for article_id, similarity in results:
            ranked_ids.append(article_id)
        rank = ranked_ids.index(expected_id) + 1
        if rank == 1:
            hits_at_1 += 1
        if rank <= 3:
            hits_at_3 += 1
        top_id, top_similarity = results[0]
        print(f"rank {rank} | expected {expected_id} | top {top_id} ({top_similarity:.3f}) | {question}")

print(f"hit@1: {hits_at_1}/{len(EVAL_QUESTIONS)}   hit@3: {hits_at_3}/{len(EVAL_QUESTIONS)}")