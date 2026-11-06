import re
#start of the next article e.g. "9.10.19.2. Sound Patterns..."
NEXT_HEADING = re.compile(r"^\d+\.\d+\.\d+\.\d+\. [A-Z]")
# Some articles have a line like "(See Note A-9.8.7.4.)" between the title and clause 1.
NOTE_REFERENCE = re.compile(r" \(See Notes? [^)]*\)$")

def collapse_whitespace(text: str) -> str:
    return " ".join(text.split())


def text_is_in_source(article_text: str, source_text: str) -> bool:
    #guard to check if claude's text is present word to word in source text
    return collapse_whitespace(article_text) in collapse_whitespace(source_text)

def article_boundaries_ok(article_id:str, title: str, article_text:str, source_text:str)->bool:
    #guard 2:checking if claude left anything out, text should be between a starting article id ,title and the next article id, title
    source=collapse_whitespace(source_text)
    text=collapse_whitespace(article_text)
    #find the index where text starts in source
    start=source.find(text)
    if start==-1:
        return False

    before=NOTE_REFERENCE.sub("",source[:start].rstrip())
    after=source[start+len(text):].lstrip()
    starts_after_heading=before.endswith(f"{article_id}. {collapse_whitespace(title)}")
    ends_before_next_heading=after=="" or NEXT_HEADING.match(after) is not None

    return starts_after_heading and ends_before_next_heading