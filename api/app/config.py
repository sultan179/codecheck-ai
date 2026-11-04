from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #reads the values from .env file to setup the postgres database in docker
    #ignores any extra key this class doesnt use from .env like Anthropic key etc
    model_config= SettingsConfigDict(env_file= ".env",extra= "ignore")
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str= "127.0.0.1"
    postgres_port: int= 5432
    anthropic_api_key: str
