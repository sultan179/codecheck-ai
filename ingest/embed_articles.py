from sentence_transformers import SentenceTransformer

from app.config import Settings
from app.database import open_connection
from app.retrieval import to_vector_literal

MODEL_NAME = "BAAI/bge-small-en-v1.5"

UPSERT_EMBEDDING_SQL = """
    INSERT INTO article_embeddings (article_row_id, model_name, embedding)
    VALUES (%s, %s, %s::vector)
    ON CONFLICT (article_row_id, model_name) DO UPDATE SET
        embedding = EXCLUDED.embedding,
        created_at = now()
"""



def embed_all_articles() -> int:
    settings = Settings()
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    with open_connection(settings) as connection:
        rows = connection.execute("SELECT id, title, body FROM articles ORDER BY id").fetchall()
        for row_id, title, body in rows:
            # Must match the text format used in the eval, or the vectors differ.
            vector = model.encode(f"{title}. {body}")
            connection.execute(UPSERT_EMBEDDING_SQL, (row_id, MODEL_NAME, to_vector_literal(vector)))
    return len(rows)


if __name__ == "__main__":
    count = embed_all_articles()
    print(f"embedded {count} articles with {MODEL_NAME}")