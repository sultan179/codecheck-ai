def collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def text_is_in_source(article_text: str, source_text: str) -> bool:
    # The page puts clause markers on their own lines, while Claude returns one line,
    # so we compare with all runs of whitespace collapsed to a single space.
    return collapse_whitespace(article_text) in collapse_whitespace(source_text)