import re

import pymupdf

PDF_PATH = "data/raw/nbc-ae-2023-printing2.pdf"

# A line that is exactly an article number such as "9.10.19.3."
ARTICLE_NUMBER_LINE = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\.$")
# Page headers like "Division B" are not article titles.
NOT_A_TITLE = {"Division A", "Division B", "Division C"}

def find_article_headings(page_text: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in page_text.splitlines()]
    headings = []
    for index in range(len(lines) - 1):
        match = ARTICLE_NUMBER_LINE.match(lines[index])
        next_line = lines[index + 1]
        # A real title starts with a capital letter. The page's running header
        # puts two article numbers back to back, so those are skipped.
        if match and next_line[:1].isupper() and next_line not in NOT_A_TITLE:
            headings.append((match.group(1), next_line))
    return headings

def build_heading_index(document:pymupdf.Document)->dict[str,list[int]]:

    index:[str,list[int]]={}

    for page_number in range(1,len(document)+1):
        page_text=document[page_number-1].get_text()
        for article_id, title in find_article_headings(page_text):
            if article_id not in index:
                index[article_id]=[]
            index[article_id].append(page_number)
    return index

TARGET_ARTICLES = [
    "9.10.9.16", "9.10.19.1", "9.10.19.3", "9.11.1.1", "9.9.8.2",
    "9.9.9.1", "9.8.2.1", "9.8.4.1", "9.8.7.4", "9.8.8.3",
]

if __name__ == "__main__":
    document = pymupdf.open(PDF_PATH)
    index=build_heading_index(document)
    for article_id in TARGET_ARTICLES:
        print(article_id,index.get(article_id))