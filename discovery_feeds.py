"""Discover supported public board identifiers from already collected employer URLs.
No arbitrary URL fetching, search scraping, or bypassing access controls.
"""
import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).parent
FILE=ROOT/'discovered_boards.json'
TOKEN=re.compile(r'^[A-Za-z0-9_-]{1,80}$')
HOSTS={'jobs.smartrecruiters.com':'smart','jobs.lever.co':'lever','jobs.eu.lever.co':'lever-eu','boards.greenhouse.io':'greenhouse','job-boards.greenhouse.io':'greenhouse','job-boards.eu.greenhouse.io':'greenhouse-eu','jobs.ashbyhq.com':'ashby'}
def board(url,name):
    try:
        p=urlsplit(url);host=p.hostname;parts=p.path.strip('/').split('/')
        if p.scheme!='https' or p.username or p.password or p.port not in (None,443) or len(parts)<2 or not TOKEN.fullmatch(parts[0]) or host not in HOSTS:return None
        if not name or not str(name).strip():return None
        return dict(type=HOSTS[host],slug=parts[0],name=str(name).strip()[:120])
    except (ValueError,TypeError):return None
def discover(records):
    try:old=json.loads(FILE.read_text())
    except (ValueError,OSError):old=[]
    seeds={(x['type'],x['slug'].lower()) for x in json.loads((ROOT/'employer_sources.json').read_text()).get('feeds',[])}
    out={(x['type'],x['slug'].lower()):x for x in old if isinstance(x,dict) and x.get('type') in HOSTS.values() and TOKEN.fullmatch(str(x.get('slug','')))}
    for j in records:
        if not j.get('live') or j.get('cached') or j.get('vacancyStatus')=='closed':continue
        for url in (j.get('applyUrl'),j.get('url')):
            x=board(url,j.get('company'));k=(x['type'],x['slug'].lower()) if x else None
            if k and k not in seeds and len(out)<30:out.setdefault(k,x)
    rows=list(out.values())[:30];FILE.write_text(json.dumps(rows,indent=2));return rows
