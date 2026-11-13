import psycopg

from schemas import ExtractedArticle

EDITION = "NBC 2023 Alberta Edition, 2nd printing"

# Insert the article, or update it if this edition already has it,
# so running the loader twice never creates duplicates.
UPSERT_ARTICLE_SQL = """
    INSERT INTO articles (edition, article_id, title, body, cross_references, source_page)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (edition, article_id) DO UPDATE SET
        title = EXCLUDED.title,
        body = EXCLUDED.body,
        cross_references = EXCLUDED.cross_references,
        source_page = EXCLUDED.source_page
"""


def save_article(connection: psycopg.Connection, article: ExtractedArticle,
                 article_id: str, source_page: int) -> None:
    values = (EDITION, article_id, article.title, article.text,
              article.cross_references, source_page)
    connection.execute(UPSERT_ARTICLE_SQL, values)