import os
import sys
from src.loader import list_pdfs
from src.analyzer import extract_spans
from src.formatter import build_outline
import pdfplumber

def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else 'app/input'
    out = sys.argv[2] if len(sys.argv) > 2 else 'app/output'
    os.makedirs(out, exist_ok=True)

    for fname in list_pdfs(inp):
        pdf_path = os.path.join(inp, fname)
        # For title, extract the first non-empty line of text from page 1
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text() or ''
            # Split into lines and pick first non-empty
            lines = [line.strip() for line in text.splitlines()]
            title = next((line for line in lines if line), '')
        # outline remains empty for Stage 1A
        outline = []
        js = build_outline(outline, title)
        out_path = os.path.join(out, fname.replace('.pdf', '.json'))
        with open(out_path, 'w') as f:
            f.write(js)

if __name__ == '__main__':
    main()