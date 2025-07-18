# 📄 Adobe India Hackathon – Round 1A: PDF Outline Extractor

This project extracts the document title and hierarchical outline (H1, H2, H3...) from digital PDF files. Built for the Adobe India Hackathon 2025, it processes input files and outputs structured JSON summaries.

---

## 🏗️ Project Structure

Adobe_hackthon_project/
├── app/
│ ├── input/ # Place your test PDF files here
│ └── output/ # Output JSON files are saved here
├── notebooks/
│ └── prototype.ipynb # Jupyter notebook for font analysis prototype
├── src/ # Core modules
│ ├── loader.py # List PDFs
│ ├── analyzer.py # Extract spans with font + position
│ ├── classifier.py # Assign heading levels
│ ├── formatter.py # Output JSON
│ └── cli.py # CLI driver script
├── tests/ # Unit tests
├── .venv/ # Python virtual environment (excluded from Git)
├── requirements.txt # pip dependencies
├── .gitignore
└── README.md

## 🔧 Installation

```bash
# Clone your repo
git clone git@github.com:youruser/round1a-outline-extractor.git
cd round1a-outline-extractor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate     # or use .venv\Scripts\activate.bat on Windows

# Install requirements
pip install -r requirements.txt

🚀 Usage
Place all input PDFs inside app/input/

Run the CLI: python -m src.cli app/input app/output
You will get one .json file per PDF in app/output/.


🧪 Example Output
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


🛠️ Dependencies
Python 3.9+

pdfplumber

pytest (for tests)

black, flake8 (optional linting)


✅ Checklist for Round 1A Submission
 Works for multiple PDFs

 Correctly extracts title from page 1

 Builds nested outline from heading font sizes

 Outputs valid JSON per file

 Private GitHub repo with code and docs


