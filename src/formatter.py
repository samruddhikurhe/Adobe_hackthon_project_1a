import json

def build_outline(headings, title=None):
    obj = {
        'title': title or '',
        'outline': [
            {'level': h['level'], 'text': h['text'], 'page': h['page']} for h in headings
        ]
    }
    return json.dumps(obj, indent=2)