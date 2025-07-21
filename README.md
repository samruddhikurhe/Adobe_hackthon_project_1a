# Challenge 1a PDF Processor

A lightweight, containerized Python pipeline that scans a folder of PDF files, extracts document title and hierarchical outline (headings), and emits JSON conforming to the official `output_schema.json`. Designed for CPU‑only execution (no internet), ≤ 10 s per 50‑page PDF on 8 vCPUs, < 200 MB install size.

---

## 📁 Repository Layout

```text
Challenge_1a/
├── sample_dataset/
│   ├── pdfs/                 # ← place your input PDFs here
│   ├── outputs/              # ← JSON outputs will be written here
│   └── schema/
│       └── output_schema.json  # official JSON Schema (draft‑04)
├── Dockerfile                # Docker build / runtime configuration
├── process_pdfs.py           # Main processing script
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation
```

---

## 🚀 Solution Overview

1. **Metadata & Title Extraction**  
   - Reads `Title` from PDF metadata (if present).  
   - If empty, scans page 1 for the largest‑font text span as the inferred title.

2. **Text Block Segmentation**  
   - Uses **PyMuPDF (fitz)** to stream‑read each page.  
   - Splits content into “blocks” of contiguous text, computing a weighted mean font size per block.

3. **Outline Detection**  
   - Computes the document’s mean (μ) and population std (σ) of block font sizes.  
   - Marks any block with font‑size ≥ μ + 0.5·σ as a heading candidate.  
   - Ranks distinct heading sizes descending → maps largest→`H1`, next→`H2`, etc.  
   - Emits an `"outline"` array in natural page/block order.

4. **JSON Assembly & Validation**  
   - Builds a Python dict with exactly two top‑level keys:  
     - `"title"`: _string_  
     - `"outline"`: _array_ of `{ level: "Hn", text: "...", page: int }`  
   - Validates against the provided **draft‑04 JSON‑Schema** using **jsonschema**.

5. **Parallel Processing**  
   - Uses `concurrent.futures.ProcessPoolExecutor` with 8 workers.  
   - Ensures each PDF is processed in its own Python process (avoids GIL).

---

## 🧩 Libraries & Tools

- **[PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)** (v1.25.1)  
  Ultra‑fast PDF parser for text, fonts, and layout.  
- **[jsonschema](https://python-jsonschema.readthedocs.io/)** (v4.22.0)  
  Draft‑04 validator for enforcing JSON output format.  
- **Python 3.10+** (tested on 3.10)  
- **Docker** for reproducible, network‑restricted execution.

_No machine‑learning models are used — all “intelligence” is simple font‑size heuristics._

---

## 🏁 Local Installation & Usage

1. **Clone the repo** and navigate into it:
   ```bash
   git clone https://github.com/samruddhikurhe/Adobe_hackthon_project_1a.git
   cd Challenge_1a
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Place your PDFs** in:
   ```
   sample_dataset/pdfs/
   ```

4. **Run the processor**:
   ```bash
   python process_pdfs.py
   ```

5. **Inspect JSON outputs**:
   ```bash
   sample_dataset/outputs/*.json
   ```

6. **Validate outputs**:
   ```bash
   python - <<'PYCODE'
   import json, glob
   from jsonschema import validate
   schema = json.load(open("sample_dataset/schema/output_schema.json"))
   for f in glob.glob("sample_dataset/outputs/*.json"):
       validate(json.load(open(f)), schema)
       print(f"{f} ✅")
   PYCODE
   ```

---

## 🐳 Docker Usage

1. **Build the image** (amd64):
   ```bash
   docker build --platform linux/amd64 -t pdf-processor .
   ```

2. **Run with mounted folders**:
   ```bash
   docker run --rm -v "$(pwd)/sample_dataset/pdfs:/app/sample_dataset/pdfs:ro" -v "$(pwd)/sample_dataset/outputs:/app/sample_dataset/outputs" --network none pdf-processor
   ```

3. **Check outputs** on host:
   ```bash
   ls sample_dataset/outputs/*.json
   ```

---

## 📊 Performance & Constraints

- **Execution time**: ~0.08 s per 1‑page PDF; ~8 s for a 50‑page document on 8 vCPUs.  
- **Memory**: < 200 MB total for all dependencies.  
- **Network**: Completely offline at runtime (`--network none`).  
- **CPU**: Scales to 8 workers; easily adjustable in `process_pdfs.py`.

---

