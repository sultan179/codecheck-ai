import anthropic
import pymupdf
from pydantic import ValidationError
from app.config import Settings
from app.llm import estimate_cost_usd
from schemas import ExtractedArticle
from guards import text_is_in_source, article_boundaries_ok
from split_articles import PDF_PATH, TARGET_ARTICLES, build_heading_index
from app.database import open_connection
from article_store import save_article


SYSTEM_PROMPT = (
    "You extract ONE article from raw text of a building code page. "
    "Copy the article text exactly, word for word, keeping clause markers such as "
    "1) and a). Do not include page headers, footers or other articles. "
    "cross_references: article numbers mentioned in the text, written like 9.10.19.8 "
    "(no trailing dot, no sentence numbers). Never invent or paraphrase text."
)


HEADER_BOTTOM_Y = 60   # blocks starting above this line are the page header
FOOTER_TOP_Y = 765     # blocks starting below this line are the page footer

def get_body_text(page:pymupdf.Page)->str:
    body_blocks=[]
    for block in page.get_text("blocks"):
        block_top_y=block[1]
        if HEADER_BOTTOM_Y<= block_top_y <= FOOTER_TOP_Y:
            body_blocks.append(block[4])
    return "".join(body_blocks)



# The article may continue onto the next page, so we send both pages.
def get_two_pages_text(document: pymupdf.Document, page_number: int) -> str:
    this_page = get_body_text(document[page_number-1])
    next_page = get_body_text(document[page_number])
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

MAX_ATTEMPTS = 3


def extract_verified_article(client, article_id: str, page_text: str):
    # The model's output varies between runs, so a guard failure on one attempt
    # often passes on the next. After MAX_ATTEMPTS we give up and report why;
    # an unverified article is never stored.
    total_cost = 0.0
    failure_reason = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            article, cost = extract_article(client, article_id, page_text)
        except ValidationError:
            failure_reason = "schema validation failed"
            continue
        total_cost += cost
        claimed_id = article.article_id.rstrip(".")
        if claimed_id != article_id:
            failure_reason = "wrong article id"
        elif not text_is_in_source(article.text, page_text):
            failure_reason = "text not found in source"
        elif not article_boundaries_ok(claimed_id, article.title, article.text, page_text):
            failure_reason = "text incomplete"
        else:
            return article, attempt, total_cost, ""
    return None, MAX_ATTEMPTS, total_cost, failure_reason

if __name__ == "__main__":
    settings = Settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    document = pymupdf.open(PDF_PATH)
    index = build_heading_index(document)

    with open_connection(settings) as connection:
        for article_id in TARGET_ARTICLES:
            source_page = index[article_id][0]
            page_text = get_two_pages_text(document, source_page)
            article, attempts, cost, reason = extract_verified_article(client, article_id, page_text)
            if article:
                save_article(connection, article, article_id, source_page)
            status = "VERIFIED, saved" if article else "REVIEW: " + reason
            print(article_id, "|", status, "| attempts:", attempts, "| cost:", round(cost, 5))