import numpy as np
import psycopg

# <=> is pgvector's cosine distance (1 - cosine similarity): smaller = closer.
SEARCH_ARTICLES_SQL = """
    SELECT a.article_id,
           1 - (e.embedding <=> %(question)s::vector) AS similarity
    FROM article_embeddings AS e
    JOIN articles AS a ON a.id = e.article_row_id
    WHERE e.model_name = %(model_name)s
    ORDER BY e.embedding <=> %(question)s::vector
    LIMIT %(limit)s
"""


def to_vector_literal(vector: np.ndarray) -> str:
    # pgvector reads vectors as text like "[0.1,0.2,0.3]"; the SQL casts it with ::vector.
    numbers = []
    for value in vector:
        numbers.append(str(float(value)))
    return "[" + ",".join(numbers) + "]"


def search_articles(connection: psycopg.Connection, question_vector: np.ndarray,
                    model_name: str, limit: int) -> list[tuple[str, float]]:
    # Returns (article_id, similarity) pairs, most similar first.
    parameters = {
        "question": to_vector_literal(question_vector),
        "model_name": model_name,
        "limit": limit,
    }
    return connection.execute(SEARCH_ARTICLES_SQL, parameters).fetchall()