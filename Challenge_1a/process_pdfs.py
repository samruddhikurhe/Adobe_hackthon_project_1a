#!/usr/bin/env python3
import json
import statistics
import sys
import re
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

# Load JSON schema validator once
_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
_validator = Draft4Validator(_schema)


def open_document(path: Path):
    return fitz.open(str(path))


def _join_spans(spans: list[str]) -> str:
    """
    Join spans into a line:
    - Collapse runs of whitespace.
    - If ≥30% CJK characters, concatenate without spaces.
    - Otherwise, join with single spaces.
    """
    joined = "".join(spans)
    joined = re.sub(r"\s+", " ", joined)
    cjk_count = len(re.findall(r"[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]", joined))
    if cjk_count / max(len(joined), 1) > 0.3:
        return joined
    return " ".join(spans)


def _infer_title(page):
    best = {"size": 0, "text": ""}
    for b in page.get_text("dict")["blocks"]:
        if "lines" not in b:
            continue
        spans = [s["text"] for line in b["lines"] for s in line["spans"]]
        text = _join_spans(spans).strip()
        size = max((s.get("size", 0) for line in b["lines"] for s in line["spans"]), default=0)
        if text and size > best["size"]:
            best = {"size": size, "text": text}
    return best["text"]


def extract_metadata(pdf):
    # Always infer title from page 1
    title = _infer_title(pdf.load_page(0)).strip() or Path(pdf.name).stem
    return {"title": title}


def extract_blocks(pdf):
    blocks = []
    for pg in range(pdf.page_count):
        page = pdf.load_page(pg)
        for b in page.get_text("dict")["blocks"]:
            if "lines" not in b:
                continue
            spans = [s["text"] for line in b["lines"] for s in line["spans"]]
            text = _join_spans(spans).strip()

            total_sz = total_ch = 0
            for line in b["lines"]:
                for s in line["spans"]:
                    cnt = len(s["text"])
                    total_ch += cnt
                    total_sz += s.get("size", 0) * cnt
            mean_sz = (total_sz / total_ch) if total_ch else 0

            blocks.append({
                "page":      pg + 1,
                "block":     b.get("number", 0),
                "text":      text,
                "font_size": mean_sz,
            })
    return blocks


def override_level(text: str) -> str | None:
    """
    Regex-based overrides:
      - 'Part X.' or '부록X.' → H1
      - '1.' or '2．' → H1
      - '（1）'        → H2
      - '(계속)'       → H2
    """
    if re.match(r"^Part\s*\d+\.", text, re.IGNORECASE) or re.match(r"^부록\d+", text):
        return "H1"
    if re.match(r"^[0-9]+[\.．]", text):
        return "H1"
    if re.match(r"^（\d+）", text):
        return "H2"
    if text.endswith("(계속)"):
        return "H2"
    return None


def build_outline(blocks):
    """
    1. Filter out empty or too-short blocks.
    2. Compute mean + 1.0*stddev threshold.
    3. Select candidates by size or override H2.
    4. Noise-filter (institutional headers) + dedupe + drop bottom 20% fonts.
    5. Assign final level via override or size clustering.
    """
    # 1. Filter out tiny text
    blocks = [b for b in blocks if len(b["text"]) > 2]

    if not blocks:
        return []

    sizes = [b["font_size"] for b in blocks]
    mu = statistics.mean(sizes)
    sd = statistics.pstdev(sizes)
    min_sz = min(sizes)
    threshold = mu + 1.0 * sd  # tighter threshold for top headings

    # 2. Select headings or H2 overrides
    heads = []
    for b in blocks:
        ol = override_level(b["text"])
        # Drop bottom 20% font sizes
        if b["font_size"] <= min_sz + 0.2 * (mu - min_sz):
            continue
        if b["font_size"] >= threshold or ol == "H2":
            heads.append(b)
    if not heads:
        return []

    # 3. Map sizes → levels
    distinct = sorted({b["font_size"] for b in heads}, reverse=True)
    size_map = {s: f"H{i+1}" for i, s in enumerate(distinct)}

    # 4. Noise filtering and dedupe
    seen = set()
    unique = []
    for b in sorted(heads, key=lambda x: (x["page"], x["block"])):
        text = re.sub(r"\s+", " ", b["text"]).strip()
        # institutional headers
        if re.search(r"국토 안보부|시민권 및 이민 서비스", text):
            continue
        # footers
        if re.match(r"^페이지\s*\d+/\d+", text):
            continue
        # single letters
        if re.match(r"^[A-Za-z]\.?$", text):
            continue
        key = (text, b["page"])
        if key in seen:
            continue
        seen.add(key)
        b["text"] = text
        unique.append(b)

    # 5. Assign levels
    outline = []
    for b in unique:
        lvl = override_level(b["text"]) or size_map[b["font_size"]]
        outline.append({"level": lvl, "text": b["text"], "page": b["page"]})

    return outline


def build_document(meta, blocks):
    return {"title": meta["title"], "outline": build_outline(blocks)}


def process(path: Path):
    t0 = perf_counter()
    pdf = open_document(path)
    meta = extract_metadata(pdf)
    blocks = extract_blocks(pdf)
    doc = build_document(meta, blocks)

    # Validate schema
    _validator.validate(doc)

    out = OUTPUT_DIR / f"{path.stem}.json"
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✔ {path.name:30} → {out.name} ({perf_counter()-t0:.2f}s)")


def main():
    if not INPUT_DIR.exists():
        print(f"❌ Missing input folder: {INPUT_DIR}", file=sys.stderr)
        sys.exit(1)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"⚠️ No PDFs found in {INPUT_DIR}")
        return

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        list(pool.map(process, pdfs))


if __name__ == "__main__":
    main()
