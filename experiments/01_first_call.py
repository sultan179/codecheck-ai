import anthropic

from app.config import Settings
from app.llm import estimate_cost_usd

settings=Settings()

client=anthropic.Anthropic(api_key=settings.anthropic_api_key)

question = (
    "In the National Building Code of Canada, what fire-resistance rating "
    "is typically required between dwelling units in a multifamily building?"
)

response=client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=600,
    messages=[{"role":"user","content":question}],
    thinking={"type":"disabled"},
    system=(
        "You are an advisory building-code reviewer for the National Building "
        "Code of Canada, Alberta edition, Part 9. You flag potential issues for "
        "human review and never certify compliance. Cite the article number for "
        "every claim. If you are not sure of the article, say 'unsure' instead "
        "of guessing."
    ),
)

for block in response.content:
    print(f"[{block.type}]")
    if block.type=="text":
        print (block.text)
print("---")
print("input tokens: ", response.usage.input_tokens)
print("output tokens:", response.usage.output_tokens)
print("stop reason:  ", response.stop_reason)
print("cost (USD):   ", estimate_cost_usd(response.usage.input_tokens, response.usage.output_tokens))
