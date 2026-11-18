def collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def text_is_in_source(text: str, source_text: str) -> bool:
    # Grounding check: the text must appear word for word in the source,
    # so the model cannot have invented or changed it.
    return collapse_whitespace(text) in collapse_whitespace(source_text)