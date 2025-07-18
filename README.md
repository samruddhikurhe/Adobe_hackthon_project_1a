# 📄 Adobe India Hackathon – Round 1A: PDF Outline Extractor

**Extract the document title and hierarchical outline (H1, H2, H3...) from digital PDF files.** Built for the Adobe India Hackathon 2025, this tool processes input PDF files and outputs structured JSON summaries.

---

## 🏗️ Project Structure

```
Adobe_hackathon_project/
├── app/
│   ├── input/       # Place your test PDF files here
│   └── output/      # Output JSON files are saved here
├── notebooks/
│   └── prototype.ipynb  # Jupyter notebook for font analysis prototype
├── src/            # Core modules
│   ├── loader.py       # List PDFs
│   ├── analyzer.py     # Extract spans with font & position
│   ├── classifier.py   # Assign heading levels
│   ├── formatter.py    # Output JSON
│   └── cli.py          # CLI driver script
├── tests/          # Unit tests
├── .venv/          # Python virtual environment (excluded)
├── requirements.txt  # pip dependencies
├── .gitignore
└── README.md       # Project documentation
```

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone git@github.com:youruser/round1a-outline-extractor.git
   cd round1a-outline-extractor
   ```

2. **Create and activate virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate     # Linux/macOS
   .\.venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## 🎬 Usage

1. **Add input PDFs**

   * Place all PDF files you want to process into `app/input/`.

2. **Run the CLI**

   ```bash
   python -m src.cli app/input app/output
   ```

3. **Check the results**

   * For each PDF in `app/input/`, a corresponding `.json` file will be created in `app/output/`.

## 🧪 Example Output

```json
{
  "title": "Overview Foundation Level Extensions",
  "outline": [
    {
      "level": "H1",
      "text": "Revision History",
      "page": 2
    },
    {
      "level": "H2",
      "text": "2.1 Intended Audience",
      "page": 6
    }
  ]
}
```

## 🛠️ Dependencies

* **Python**: 3.9+
* **pdfplumber**: PDF parsing and layout analysis
* **pytest**: For running unit tests
* **black**, **flake8**: (Optional) Code formatting and linting

> Install all dependencies via:
>
> ```bash
> pip install -r requirements.txt
> ```

---

## ✅ Round 1A Submission Checklist

* [ ] Handles multiple PDFs in a single run
* [ ] Correctly extracts the document title from the first page
* [ ] Builds a nested outline based on heading font sizes
* [ ] Outputs valid JSON files, one per input PDF
* [ ] Private GitHub repository with code and documentation

---

