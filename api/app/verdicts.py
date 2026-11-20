from typing import Literal
import anthropic
from pydantic import BaseModel, Field
from app.claims import ExtractedClaim
from app.llm import LLM_MODEL, estimate_cost_usd
from app.retrieval import RetrievedArticle
from app.grounding import text_is_in_source


class Verdict(BaseModel):
    # Field order matters: the model writes fields top to bottom, so it finds
    # evidence and reasons about it before it commits to a verdict.
    cited_article_id: str = Field(
        description="Number of the article the verdict relies on, e.g. 9.8.8.3. "
                    "Empty if no provided article addresses the claim."
    )
    evidence_quote: str = Field(
        description="The requirement from the cited article, copied word for word. "
                    "Empty if no provided article addresses the claim."
    )
    explanation: str = Field(
        description="One or two sentences comparing the claim with the requirement, "
                    "including the numbers."
    )
    verdict: Literal["potential_issue", "no_issue_found", "needs_review"]


SYSTEM_PROMPT = (
    "You are an advisory reviewer. You check one design claim against the building "
    "code articles provided. Use only those articles, never your memory of the code. "
    "potential_issue: the claim does not meet the cited requirement. "
    "no_issue_found: the claim meets the cited requirement. "
    "needs_review: no provided article addresses the claim, or the claim lacks "
    "information the requirement depends on. "
    "Copy evidence_quote word for word from the cited article."
)


def build_review_message(claim: ExtractedClaim, articles: list[RetrievedArticle]) -> str:
    parts = [
        f"<claim>{claim.statement}</claim>",
        # The full spec sentence can hold context the short statement lost.
        f"<spec_sentence>{claim.source_quote}</spec_sentence>",
    ]
    for article in articles:
        parts.append(
            f'<article id="{article.article_id}" title="{article.title}">\n'
            f"{article.body}\n</article>"
        )
    return "\n\n".join(parts)


def judge_claim(client: anthropic.Anthropic, claim: ExtractedClaim,
                articles: list[RetrievedArticle]) -> tuple[Verdict, float]:
    response = client.messages.parse(
        model=LLM_MODEL,
        max_tokens=1000,
        thinking={"type": "disabled"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_review_message(claim, articles)}],
        output_format=Verdict,
    )
    cost = estimate_cost_usd(response.usage.input_tokens, response.usage.output_tokens)
    return response.parsed_output, cost


def citation_is_valid(verdict: Verdict, articles: list[RetrievedArticle]) -> bool:
    # needs_review may honestly cite nothing.
    if verdict.verdict == "needs_review" and verdict.cited_article_id == "":
        return True
    # An empty quote would pass the check below, because "" is inside every string.
    if verdict.evidence_quote == "":
        return False
    cited_id = verdict.cited_article_id.rstrip(".")
    for article in articles:
        if article.article_id == cited_id:
            return text_is_in_source(verdict.evidence_quote, article.body)
    # The cited article was not among the ones we retrieved.
    return False