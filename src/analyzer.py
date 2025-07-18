import pdfplumber

def extract_spans(pdf_path: str):
    spans = []  # list of dicts: {text, size, font, x0, page}
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=['fontname','size','x0'])
            for w in words:
                spans.append({
                    'text': w['text'],
                    'size': w['size'],
                    'font': w['fontname'],
                    'x0': w.get('x0', 0),
                    'page': page_num,
                })
    return spans