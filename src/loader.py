import os

def list_pdfs(input_dir: str):
    """Return sorted list of .pdf files."""
    files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    return sorted(files)

if __name__ == '__main__':
    print(list_pdfs('app/input'))