"""Conservative public application link checks. No scraping, no sign-in, no automatic deletion."""
import json,time,re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).parent
CACHE=ROOT/'link_health_cache.json'
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kw):return None
SUFFIXES=('smartrecruiters.com','greenhouse.io','lever.co','ashbyhq.com','personio.de','personio.com','recruitee.com','myworkdayjobs.com','workable.com','findapprenticeship.service.gov.uk')
def allowed(value):
    try:
        u=urlsplit(value);h=u.hostname or ''
        return u.scheme=='https' and u.port in (None,443) and not u.username and not u.password and any(h==d or h.endswith('.'+d) for d in SUFFIXES)
    except (TypeError,ValueError):return False

def check(url):
    try:
        with build_opener(NoRedirect()).open(Request(url,method='HEAD',headers={'User-Agent':'CareerHub/1.0 (public link validation)'}),timeout=5) as r:status=r.status
    except HTTPError as e:status=e.code
    except Exception:return 'unverified'
    if status in (404,410):return 'missing'
    if 200<=status<300:return 'reachable'
    return 'unverified'

def main():
    file=ROOT/'site/vacancies.json';d=json.loads(file.read_text()); now=time.time()
    try:cache=json.loads(CACHE.read_text())
    except (OSError,ValueError):cache={}
    urls={j.get('applyUrl') or j.get('url') for j in d['jobs']};urls={u for u in urls if u and allowed(u)}
    pending=sorted((u for u in urls if now-cache.get(u,{}).get('at',0)>86400),key=lambda u:cache.get(u,{}).get('at',0))[:60]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for u,s in zip(pending,ex.map(check,pending)):cache[u]={'status':s,'at':now}
    for j in d['jobs']:
        u=j.get('applyUrl') or j.get('url');v=cache.get(u,{})
        if now-v.get('at',0)<172800 and v.get('status')=='missing':j['linkStatus']='may-be-unavailable'
    cache={u:v for u,v in cache.items() if u in urls and now-v.get('at',0)<7*86400}
    CACHE.write_text(json.dumps(cache));file.write_text(json.dumps(d,ensure_ascii=False));print('Checked',len(pending),'eligible links; possible missing links:',sum(j.get('linkStatus')=='may-be-unavailable' for j in d['jobs']))
if __name__=='__main__':main()
