"""Generate the public vacancy feed; no personal application data is read."""
from pathlib import Path
import json
from vacancy_search import nationwide

if __name__ == '__main__':
    result = nationwide()
    target = Path(__file__).parent / 'site' / 'vacancies.json'
    target.write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    for source in result['sources']:
        print(source['name'], ':', source['message'])
    print(f"Published feed contains {len(result['jobs'])} listings and leads.")
    if not any(source.get('ok') for source in result['sources']):
        print('::warning::All sources unavailable. Any retained records are cached.')
