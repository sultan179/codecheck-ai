import psycopg
from app.config import Settings

def is_database_reachable(settings:Settings)->bool:

    try:
        with psycopg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            connect_timeout=2,
        ) as connection:
            connection.execute("SELECT 1")
        return True
    except psycopg.OperationalError:
        return False
