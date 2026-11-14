import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import Settings
from app.database import open_connection

MODEL_NAME = "BAAI/bge-small-en-v1.5"


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    return float(np.dot(vector_a, vector_b) / (np.linalg.norm(vector_a) * np.linalg.norm(vector_b)))


settings = Settings()
model = SentenceTransformer(MODEL_NAME, device="cpu")

with open_connection(settings) as connection:
    articles = connection.execute("SELECT article_id, title, body FROM articles").fetchall()

# We embed title + body together, so the title's words help the match.
article_texts = []
for article_id, title, body in articles:
    article_texts.append(f"{title}. {body}")
article_vectors = model.encode(article_texts)

question = "How tall must a guard be?"
question_vector = model.encode(question)

scores = []
for article, article_vector in zip(articles, article_vectors):
    scores.append((cosine_similarity(question_vector, article_vector), article[0], article[1]))
scores.sort(reverse=True)

for score, article_id, title in scores[:3]:
    print(round(score, 3), article_id, title)