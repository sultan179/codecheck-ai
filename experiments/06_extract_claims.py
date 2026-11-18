import json

import anthropic

from app.claims import extract_claims, keep_grounded_claims
from app.config import Settings
from app.grounding import collapse_whitespace

SPEC_PATH = "data/specs/spec_001.md"
ANSWER_KEY_PATH = "data/specs/spec_001_answer_key.json"

settings = Settings()
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
with open(SPEC_PATH) as spec_file:
    spec_text = spec_file.read()
with open(ANSWER_KEY_PATH) as key_file:
    answer_key = json.load(key_file)

planted_quotes = set()
for entry in answer_key:
    planted_quotes.add(collapse_whitespace(entry["source_quote"]))

claim_list, cost = extract_claims(client, spec_text)
grounded = keep_grounded_claims(claim_list.claims, spec_text)
found_quotes = set()
for claim in grounded:
    print(f"- {claim.statement}")
    found_quotes.add(collapse_whitespace(claim.source_quote))

missed = planted_quotes - found_quotes
extra = found_quotes - planted_quotes
print(f"claims: {len(claim_list.claims)} | rejected by quote guard: {len(claim_list.claims) - len(grounded)}")
print(f"planted sentences found: {len(planted_quotes) - len(missed)}/{len(planted_quotes)}")
for quote in missed:
    print(f"  MISSED: {quote}")
for quote in extra:
    print(f"  EXTRA: {quote}")
print(f"cost ${cost:.5f}")