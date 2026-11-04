# USD per million tokens for claude-haiku-5-5 (prompts up to 100K tokens).
HAIKU_INPUT_PRICE_PER_MILLION = 0.10
HAIKU_OUTPUT_PRICE_PER_MILLION = 0.50


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    input_cost = input_tokens * HAIKU_INPUT_PRICE_PER_MILLION / 1_000_000
    output_cost = output_tokens * HAIKU_OUTPUT_PRICE_PER_MILLION / 1_000_000
    return input_cost + output_cost