
import anthropic
from pydantic import BaseModel, Field

from app.llm import LLM_MODEL, estimate_cost_usd
from app.grounding import  text_is_in_source

class ExtractedClaim(BaseModel):
    statement: str = Field(
        description="One short standalone sentence stating the design fact, "
                    "e.g. 'Balcony guards are 900 mm high.'"
    )
    source_quote: str = Field(
        description="The full sentence from the spec this claim comes from, "
                    "copied exactly, word for word."
    )


class ClaimList(BaseModel):
    # Structured outputs need an object at the top level, so the list is wrapped.
    claims: list[ExtractedClaim]


SYSTEM_PROMPT = (
    "You read a building specification and list every claim it makes. "
    "A claim is a specific statement about the design that a building code "
    "requirement could confirm or contradict, such as a dimension, a rating, "
    "or where a safety device is placed. "
    "For each claim, write a short standalone statement that keeps every number "
    "and unit, and copy the full spec sentence it comes from into source_quote, "
    "word for word. Each claim must make sense on its own: include the conditions it depends on, "
    "such as location or height, instead of listing them as separate claims. Only list claims the spec actually states. "
    "If the spec makes no claims, return an empty list."
)


def extract_claims(client: anthropic.Anthropic, spec_text: str) -> tuple[ClaimList, float]:
    response = client.messages.parse(
        model=LLM_MODEL,
        max_tokens=2000,
        thinking={"type": "disabled"},
        system=SYSTEM_PROMPT,
        # Tags mark where the spec starts and ends, so its text is read as data, not instructions.
        messages=[{"role": "user", "content": f"<spec>\n{spec_text}\n</spec>"}],
        output_format=ClaimList,
    )
    cost = estimate_cost_usd(response.usage.input_tokens, response.usage.output_tokens)
    return response.parsed_output, cost

def keep_grounded_claims(claims: list[ExtractedClaim], spec_text: str) -> list[ExtractedClaim]:
    # A claim whose quote is not in the spec was invented or altered: drop it.
    grounded = []
    for claim in claims:
        if text_is_in_source(claim.source_quote, spec_text):
            grounded.append(claim)
    return grounded