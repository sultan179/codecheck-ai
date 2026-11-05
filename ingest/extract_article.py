import anthropic
import pymupdf
from pydantic import ValidationError
from app.config import Settings
from app.llm import estimate_cost_usd
from schemas import ExtractedArticle
from guards import text_is_in_source
from split_articles import PDF_PATH, TARGET_ARTICLES, build_heading_index

PDF_PATH = "data/raw/nbc-ae-2023-printing2.pdf"

SYSTEM_PROMPT = (
    "You extract ONE article from raw text of a building code page. "
    "Copy the article text exactly, word for word, keeping clause markers such as "
    "1) and a). Do not include page headers, footers or other articles. "
    "cross_references: article numbers mentioned in the text, written like 9.10.19.8 "
    "(no trailing dot, no sentence numbers). Never invent or paraphrase text."
)

def get_page_text(document:pymupdf.Document, page_number:int)->str:
    return document[page_number-1].get_text()

settings=Settings()
client=anthropic.Anthropic(api_key=settings.anthropic_api_key)
document=pymupdf.open(PDF_PATH)

# The article may continue onto the next page, so we send both pages.
def get_two_pages_text(document: pymupdf.Document, page_number: int) -> str:
    # The article may continue onto the next page, so we send both pages.
    this_page = document[page_number - 1].get_text()
    next_page = document[page_number].get_text()
    return this_page + "\n" + next_page


def extract_article(client, article_id: str, page_text: str):
    response = client.messages.parse(
        model="claude-haiku-5-5",
        max_tokens=2000,
        thinking={"type": "disabled"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Extract article {article_id}.\n\n{page_text}"}],
        output_format=ExtractedArticle,
    )
    cost = estimate_cost_usd(response.usage.input_tokens, response.usage.output_tokens)
    return response.parsed_output, cost

if __name__ == "__main__":
    settings = Settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    document = pymupdf.open(PDF_PATH)
    index = build_heading_index(document)

    for article_id in TARGET_ARTICLES:
        page_text = get_two_pages_text(document, index[article_id][0])
        try:
            article, cost = extract_article(client, article_id, page_text)
        except ValidationError:
            print(article_id, "| FAILED schema validation")
            continue
        text_ok = text_is_in_source(article.text, page_text)
        print(article_id, "| id ok:", article.article_id == article_id,
              "| text in source:", text_ok, "| cost:", round(cost, 5))