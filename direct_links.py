"""Resolve public application links; never sign in or follow arbitrary external pages."""
import re, time, ipaddress
from urllib.parse import urlsplit, urljoin, parse_qs
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

DIRECTORIES = ('gov.uk','ucas.com','openapprenticeships.org','higherin.com','gradcracker.com','indeed.com','indeed.co.uk','reed.co.uk','linkedin.com','the-trackr.com','notgoingtouni.co.uk','getmyfirstjob.co.uk','findapprenticeships.co.uk','totaljobs.com')

def direct_url(value):
    if not isinstance(value,str): return ''
    try:
        p=urlsplit(value.strip()); host=(p.hostname or '').lower().rstrip('.')
        if p.scheme!='https' or not host or '.' not in host or p.username or p.password or p.port not in (None,443):return ''
        try: ipaddress.ip_address(host); return ''
        except ValueError: pass
        if host.endswith(('.local','.internal','.localhost')) or any(host==d or host.endswith('.'+d) for d in DIRECTORIES):return ''
        if not p.path.strip('/') and not p.query:return ''
        return value.strip()
    except ValueError:return ''

def specific_job(url):
    """Recognise role-specific URLs, not generic employer careers landing pages."""
    if not direct_url(url):return False
    p=urlsplit(url); path=p.path.lower().rstrip('/'); q={k.lower():v for k,v in parse_qs(p.query).items()}
    if any(k in q and any(v.strip() for v in q[k]) for k in ('jobid','job_id','jobreqid','folderid','vacancyid','vacancy_id','gh_jid','postingid','requisitionid','reqid')):return True
    if re.search(r'/(?:job|jobs|jobdetail|job-details|job-detail|posting|postings|vacancy|vacancies|requisition|apply)/[^/]+',path):
        last=path.rsplit('/',1)[-1]
        if last in ('search','all','list','index','careers','apprenticeships','early-careers','graduate','graduates','apply','jobs','vacancies','opportunities'):return False
        return bool(re.search(r'\d|[a-z]{3,}[-_][a-z]{3,}',last))
    if re.search(r'/(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})(?:/apply)?$',path):return True
    if (p.hostname or '').endswith('smartrecruiters.com') and re.search(r'/[^/]+/\d{6,}(?:-[^/]+)?$',path):return True
    return False

def extract_public_apply(markup, source_url):
    from vacancy_search import Tree
    candidates={}
    for a in Tree(markup).root.walk():
        if a.tag!='a':continue
        label=' '.join((a.text(),a.attrs.get('aria-label','') or '',a.attrs.get('title','') or ''))
        href=direct_url(urljoin(source_url,a.attrs.get('href','') or ''))
        if not href:continue
        # Only role-specific links from the actual public listing; no generic homepages,
        # unrelated benefit links, sign-in links, or directory redirects.
        if re.search(r'\b(?:benefits?|privacy|accessibility|terms|sign in|log in|register interest|contact|feedback|disability confident)\b',label,re.I):continue
        explicit=bool(re.search(r'\b(?:apply(?: now| here| online| for (?:this|the) (?:role|vacancy|job|apprenticeship))?|application form|start (?:your|an) application)\b',label,re.I))
        if specific_job(href):candidates[href]=max(candidates.get(href,0),2 if explicit else 1)
        elif explicit and re.search(r'/(?:apply|application)(?:/|$)',urlsplit(href).path,re.I) and not re.search(r'/(?:apply|application)/?$',urlsplit(href).path,re.I):candidates[href]=2
    if not candidates:return ''
    score=max(candidates.values()); best=[u for u,s in candidates.items() if s==score]
    return best[0] if len(best)==1 else ''

def norm(s):return re.sub(r'[^a-z0-9]+',' ',str(s or '').lower()).strip()
def company(s):return re.sub(r'\b(?:limited|ltd|plc|llp|public limited company|uk)\b','',norm(s)).strip()
def match_key(j):
    # Conservative cross-feed match: same employer, role and location (not fuzzy).
    return (company(j.get('company')),norm(j.get('title')),norm(j.get('location')))

def enrich(records, previous, fetch, limit=80):
    now=time.time(); jobs=[j for items in records.values() for j in items]
    old={j.get('id'):j for items in previous.values() if isinstance(items,list) for j in items if isinstance(j,dict)}
    ats={}
    for j in jobs:
        if str(j.get('id','')).startswith('ats:') and not j.get('cached'):
            u=direct_url(j.get('applyUrl') or j.get('url'))
            if u:
                j['applyUrl']=u; k=match_key(j)
                if all(k):ats.setdefault(k,set()).add(u)
    pending=[]
    for j in jobs:
        if direct_url(j.get('applyUrl')):continue
        matches=ats.get(match_key(j),set())
        if len(matches)==1 and all(match_key(j)):
            j['applyUrl']=next(iter(matches));continue
        # The GOV.UK listing is public. Never request sign-in-only pages or scrape
        # external employers in this resolver. Other boards retain their own links.
        if not str(j.get('id','')).startswith('gov-') or j.get('cached'):continue
        p=old.get(j.get('id'),{}); checked=p.get('applyChecked',0)
        try:checked=float(checked)
        except (ValueError,TypeError):checked=0
        if p.get('url')!=j.get('url'):checked=0
        age=now-checked
        if 0<=age<86400:
            j['applyChecked']=checked
            if direct_url(p.get('applyUrl')):j['applyUrl']=p['applyUrl']
        else:pending.append((checked,j))
    pending.sort(key=lambda pair:pair[0])
    def resolve(item):
        _,j=item; url=j.get('url','')
        try:
            p=urlsplit(url)
            if p.hostname!='www.findapprenticeship.service.gov.uk' or p.scheme!='https' or not re.fullmatch(r'/apprenticeship/(?:reference/|VAC)?\d+/?',p.path,re.I):return
            u=extract_public_apply(fetch(url),url)
            j['applyChecked']=now
            if u:j['applyUrl']=u
        except Exception:
            # Do not mark a failed request as successfully checked.
            pass
        finally:time.sleep(.35)
    with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(resolve,pending[:limit]))
    return sum(bool(direct_url(j.get('applyUrl'))) for j in jobs)
