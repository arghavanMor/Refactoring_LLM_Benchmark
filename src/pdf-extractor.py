# pdfminer.six could NOT read the PDF. Was throwing an error
# PyPDF2 was printing one character per line

import pymupdf 
import json
import unicodedata
import constants


def clean_text(text):
    return unicodedata.normalize("NFKD", text)
    
### MAIN ###

doc = pymupdf.open(constants.FOWLER_PDF_FILE)

json_data = {}
ignore_next_title = False
record_title_descr = False
current_method = ""
title_descr = ""

for page in doc.pages(constants.CHAP6_INDEX, constants.LAST_PAGE_INDEX, 1):
    blocks = page.get_text("dict", flags=11)["blocks"]
    for b in blocks:  # iterate through the text blocks
        for l in b["lines"]:  # iterate through the text lines
            for s in l["spans"]:  # iterate through the text spans

                text = s["text"]
                font = s["font"]
                color = str(s["color"])

                if color == constants.TITLES_CONST["color"] and font == constants.TITLES_CONST["font"]: # Found a title
                    if ignore_next_title: # What comes after "Chapter"
                        ignore_next_title = False
                        break

                    if text.startswith("Chapter"):
                        ignore_next_title = True
                        break

                    if text == "Motivation":
                        record_title_descr = False
                        break

                    if text.isupper(): # Text in full upper case is a refactoring method
                        if current_method and current_title:
                            json_data[current_method][current_title] = clean_text(title_descr)
                            title_descr = ""
                        current_title = ""
                        current_method = text
                        record_title_descr = False
                        json_data[current_method] = {}
                    
                    elif not record_title_descr:
                        current_title = text
                        record_title_descr = True
                    
                    else:
                        json_data[current_method][current_title] = clean_text(title_descr)
                        current_title = text
                        title_descr = ""

                
                elif record_title_descr: # Not a title and recording is on
                    if text.startswith("Click") or text.startswith("www"):
                        break
                    title_descr += text


with open(constants.FOWLER_JSON_FILE, "w") as export:
    json.dump(json_data, export, indent=4)
                