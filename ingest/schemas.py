from pydantic import BaseModel, Field

# e.g. 9.10.19.1 (four dotted numbers, no trailing dot)
ARTICLE_ID_REGEX = r"^\d+\.\d+\.\d+\.\d+$"

class ExtractedArticle(BaseModel):
    article_id: str = Field(
    pattern=ARTICLE_ID_REGEX,
    description="Article number without a trailing dot, e.g. 9.10.19.1",
)
    title: str =Field(min_length=3)
    text:str =Field(min_length=20)
    cross_references: list[str]

