#!/usr/bin/env python3
import json
import statistics
import sys
from pathlib import Path
from time import perf_counter
from concurrent.futures import ProcessPoolExecutor

import fitz  # PyMuPDF
from jsonschema import Draft4Validator

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_DIR   = Path("sample_dataset/pdfs")
OUTPUT_DIR  = Path("sample_dataset/outputs")
SCHEMA_PATH = Path("sample_dataset/schema/output_schema.json")
MAX_WORKERS = 8
# ────────────────────────────────────────────────────────────────────────────────

# load & cache the schema validator
_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
_validator = Draft4Validator(_schema)

def open_document(path: Path):
    return fitz.open(str(path))

def _infer_title(page):
    best = {"size": 0, "text": ""}
    for b in page.get_text("dict")["blocks"]:
        if "lines" not in b:
            continue
        for line in b["lines"]:
            for span in line["spans"]:
                txt = span["text"].strip()
                size = span.get("size", 0)
                if txt and size > best["size"]:
                    best = {"size": size, "text": txt}
    return best["text"]

def extract_metadata(pdf):
    m = pdf.metadata or {}
    title = (m.get("title") or "").strip()
    if not title:
        # fallback: infer from the largest‐font span on page 1
        title = _infer_title(pdf.load_page(0)) or Path(pdf.name).stem
    return {"title": title}

def extract_blocks(pdf):
    """
    Returns a list of dicts: {page, block, text, font_size}
    """
    blocks = []
    for pg in range(pdf.page_count):
        page = pdf.load_page(pg)
        for b in page.get_text("dict")["blocks"]:
            if "lines" not in b:
                continue
            # flatten text
            text = " ".join(
                span["text"]
                for line in b["lines"]
                for span in line["spans"]
            ).strip()
            # compute weighted mean font size
            total_sz = 0.0
            total_ch = 0
            for line in b["lines"]:
                for span in line["spans"]:
                    cnt = len(span["text"])
                    total_ch += cnt
                    total_sz += span.get("size", 0) * cnt
            mean_sz = (total_sz / total_ch) if total_ch else 0
            blocks.append({
                "page":      pg + 1,
                "block":     b["number"],
                "text":      text,
                "font_size": mean_sz,
            })
    return blocks

def build_outline(blocks):
    """
    1. Pick blocks ≥ mean + 0.5*stddev font size.
    2. Rank distinct sizes → H1, H2, …
    3. Emit in page/block order.
    """
    sizes = [b["font_size"] for b in blocks]
    if not sizes:
        return []
    mu = statistics.mean(sizes)
    sd = statistics.pstdev(sizes)
    threshold = mu + 0.5 * sd

    heads = [b for b in blocks if b["font_size"] >= threshold]
    if not heads:
        return []

    distinct = sorted({b["font_size"] for b in heads}, reverse=True)
    size_to_level = {size: f"H{idx+1}" for idx, size in enumerate(distinct)}

    outline = []
    for b in sorted(heads, key=lambda x: (x["page"], x["block"])):
        outline.append({
            "level": size_to_level[b["font_size"]],
            "text":  b["text"],
            "page":  b["page"],
        })
    return outline

def build_document(meta, blocks):
    """
    Creates exactly the two top‐level keys your schema mandates:
      - title: string
      - outline: [ {level,text,page}, … ]
    """
    return {
        "title":   meta["title"],
        "outline": build_outline(blocks),
    }

def process(path: Path):
    t0 = perf_counter()
    pdf    = open_document(path)
    meta   = extract_metadata(pdf)
    blocks = extract_blocks(pdf)
    doc    = build_document(meta, blocks)

    # validate
    _validator.validate(doc)

    out = OUTPUT_DIR / f"{path.stem}.json"
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✔ {path.name:30} → {out.name}  ({perf_counter()-t0:.2f}s)")

def main():
    if not INPUT_DIR.exists():
        print(f"❌ Input folder missing: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"⚠️  No PDFs found in {INPUT_DIR}")
        return

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        list(pool.map(process, pdfs))

if __name__ == "__main__":
    main()
