import sys
import pymupdf

PDF_PATH = "data/raw/nbc-ae-2023-printing2.pdf"

def find_pages_containing(document:pymupdf.Document,text:str)->list[int]:
    matching_pages=[]

    for page_index in range(len(document)):
        if text in document[page_index].get_text():
            matching_pages.append(page_index+1)
    return matching_pages

article_id=sys.argv[1]
document=pymupdf.open(PDF_PATH)
print("pages containing",article_id,"->",
      find_pages_containing(document,article_id))
if len(sys.argv)>2:
    page_number=int(sys.argv[2])
    print(document[page_number-1].get_text())
