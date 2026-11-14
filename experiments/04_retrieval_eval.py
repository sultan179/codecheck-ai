import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import Settings
from app.database import open_connection

MODEL_NAME = "BAAI/bge-small-en-v1.5"

# One question per stored article, worded to avoid the article's title.
EVAL_QUESTIONS = [
    ("Do apartments in one building need a fire-rated wall between them?", "9.10.9.16"),
    ("Does every apartment need a smoke detector?", "9.10.19.1"),
    ("Where in a unit should the detectors go, for example near bedrooms?", "9.10.19.3"),
    ("How much noise insulation is needed between neighbouring units?", "9.11.1.1"),
    ("How many ways out does each floor need?", "9.9.8.2"),
    ("How far can someone have to walk to reach an exit?", "9.9.9.1"),
    ("How wide do the stairs have to be?", "9.8.2.1"),
    ("What is the maximum height of a single step?", "9.8.4.1"),
    ("At what height should a stair rail be mounted?", "9.8.7.4"),
    ("How high does a balcony railing need to be?", "9.8.8.3"),
]


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    return float(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)))


def rank_article_ids(question_vector: np.ndarray, article_ids: list[str],
                     article_vectors: np.ndarray) -> list[str]:
    # Returns article ids from most to least similar to the question.
    scored = []
    for article_id, article_vector in zip(article_ids, article_vectors):
        scored.append((cosine_similarity(question_vector, article_vector), article_id))
    scored.sort(reverse=True)
    ranked_ids = []
    for score, article_id in scored:
        ranked_ids.append(article_id)
    return ranked_ids

settings = Settings()
model = SentenceTransformer(MODEL_NAME, device="cpu")
with open_connection(settings) as connection:
    rows = connection.execute("SELECT article_id, title, body FROM articles").fetchall()

article_ids = []
article_texts = []
for article_id, title, body in rows:
    article_ids.append(article_id)
    article_texts.append(f"{title}. {body}")
article_vectors = model.encode(article_texts)

hits_at_1 = 0
hits_at_3 = 0
for question, expected_id in EVAL_QUESTIONS:
    ranked_ids = rank_article_ids(model.encode(question), article_ids, article_vectors)
    rank = ranked_ids.index(expected_id) + 1
    if rank == 1:
        hits_at_1 += 1
    if rank <= 3:
        hits_at_3 += 1
    print(f"rank {rank} | expected {expected_id} | top {ranked_ids[0]} | {question}")

print(f"hit@1: {hits_at_1}/{len(EVAL_QUESTIONS)}   hit@3: {hits_at_3}/{len(EVAL_QUESTIONS)}")