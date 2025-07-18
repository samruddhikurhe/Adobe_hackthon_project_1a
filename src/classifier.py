from collections import Counter

def assign_levels(spans, top_n=3):
    size_counts = Counter([s['size'] for s in spans])
    common_sizes = sorted(size_counts, reverse=True)[:top_n]

    levels = {}
    for i, sz in enumerate(common_sizes):
        levels[sz] = f"H{i+1}"

    outline = []
    for span in spans:
        sz = span['size']
        if sz in levels:
            outline.append({
                'level': levels[sz],
                'text': span['text'],
                'page': span['page']
            })
    return outline
