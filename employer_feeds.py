"""Free public employer feed adapters. No paid API, no authentication, no scraping bypass.
Configured sources must allow reuse. Unknown or restricted sites remain manual links.
"""
import json, re, time, hashlib, html
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode, urlparse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

ROOT = Path(__file__).parent
TOKEN = re.compile(r'^[A-Za-z0-9_-]{1,100}$')
APP = re.compile(r'\bapprentice(?:ship)?s?\b', re.I)
BLOCK = re.compile(r'\b(?:weapons?|munitions?|missiles?|firearms?|explosives?|gambling|casino|sports betting|pornograph\w*)\b', re.I)
NOT_VACANCY = re.compile(r'\b(?:register (?:your )?interest|talent community|coming soon)\b', re.I)
CLOSED = re.compile(r'\b(?:applications (?:are |now )?closed|no longer accepting applications|vacancy (?:is )?closed)\b', re.I)
UK = re.compile(r'\b(?:UK|GB|GBR|United Kingdom|England|Scotland|Wales|Northern Ireland|London|Manchester|Birmingham|Bristol|Leeds|Liverpool|Edinburgh|Glasgow|Cardiff|Belfast|Newport|Nottingham|Sheffield|Cambridge|Oxford|Reading|Southampton|Newcastle|York|Derby|Coventry|Wolverhampton|Telford|Stoke|Exeter|Plymouth|Aberdeen|Dundee|Swindon|Milton Keynes|Bath|Cheltenham|Gloucester|Peterborough|Portsmouth|Brighton|Bournemouth|Leicester|Ipswich|Norwich|Hull|Swansea|Lancaster|Preston|Warrington|Basingstoke|Guildford|Slough|St Albans|Stockport|Maidstone|Chester|Doncaster|Horsham|Stevenage|Blackpool|Huddersfield|Wrexham|UK-wide)\b', re.I)
DEG = re.compile(r'\b(?:degree apprenticeship|degree apprentice|graduate apprenticeship|level\s*[67]|L[67]|SCQF\s*(?:10|11))\b', re.I)
LOW = re.compile(r'\b(?:level\s*[2-5]|L[2-5])\b', re.I)

def text(x):
    if isinstance(x,dict): return ' '.join(text(v) for v in x.values())
    if isinstance(x,list): return ' '.join(text(v) for v in x)
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',str(x or '')))).strip()

def date(x):
    m=re.match(r'^(\d{4}-\d{2}-\d{2})',str(x or ''))
    if not m:return ''
    try:return datetime.strptime(m[1],'%Y-%m-%d').date().isoformat()
    except ValueError:return ''

def request(url, xml=False):
    req=Request(url,headers={'User-Agent':'CareerHub/4.0 public vacancy links','Accept':'application/xml,text/xml' if xml else 'application/json'})
    with urlopen(req,timeout=12) as r:
        raw=r.read(12_000_001)
    if len(raw)>12_000_000:raise ValueError('Feed exceeds safety size limit')
    return ET.fromstring(raw) if xml else json.loads(raw)

def normalized(f, ident, title, loc, url, description='', posted='', closing='', salary='', apply_url=''):
    title=text(title); loc=text(loc); desc=text(description); url=str(url or '')
    if not ident or not APP.search(title) or BLOCK.search(title+' '+desc) or NOT_VACANCY.search(title):return None
    if re.search(r'\b(?:apprentice(?:ship)? (?:trainer|assessor|coordinator|manager|coach)|(?:trainer|assessor|coordinator|manager|coach) (?:for|of) apprentice)',title,re.I):return None
    if not UK.search(loc) or (re.search(r'\b(?:New York|United States|USA|Canada|Australia|India|Germany|France|Ireland|Singapore)\b',loc,re.I) and not re.search(r'\b(?:UK|GB|GBR|United Kingdom|England|Scotland|Wales|Northern Ireland)\b',loc,re.I)):return None
    p=urlparse(url)
    if p.scheme!='https' or not p.hostname:return None
    closing=date(closing)
    # An explicit lower level in the title must not be promoted to a degree vacancy.
    if LOW.search(title) and not DEG.search(title):return None
    if LOW.search(desc) and not DEG.search(title+' '+desc):return None
    # Extract only explicit labelled facts; unknown fields remain blank.
    if not salary:
        m=re.search(r'\b(?:starting salary|annual salary|salary)\s*(?:[:–-]|of|is)\s*(£\s*[\d,]+(?:\.\d{1,2})?)(?:\s*(per annum|p\.a\.|a year|per year|per hour|per month|per week))?',desc,re.I)
        if m:salary=' '.join(x for x in m.groups() if x)
    start_match=re.search(r'\b(?:start date|commencing(?: in)?|starting(?: in)?|starts in|will start in)\s*[:–-]?\s*((?:January|February|March|April|May|June|July|August|September|October|November|December|Spring|Summer|Autumn|Winter)\s+20\d{2})\b',desc,re.I)
    start=start_match[1] if start_match else ''
    if not closing:
        m=re.search(r'\b(?:closing date(?: for applications)?|application deadline|apply by)\s*[:–-]?\s*(?:(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[, ]+)?(\d{1,2}\s+[A-Za-z]+\s+20\d{2})',desc,re.I)
        if m:
            try:closing=datetime.strptime(m[1],'%d %B %Y').date().isoformat()
            except ValueError:pass
    closed=bool(CLOSED.search(title+' '+desc) or (closing and closing<datetime.now(timezone.utc).date().isoformat()))
    lev=re.search(r'\b(?:level\s*|L)([67])\b',title,re.I) or re.search(r'\b(?:level\s*|L)([67])\b',desc,re.I)
    level=lev[1] if lev else 'Degree' if DEG.search(title+' '+desc) else 'Unconfirmed'
    # Keep unconfirmed-level openings separate from confirmed degree-level adverts.
    from vacancy_search import sector
    from direct_links import direct_url
    return dict(applyUrl=direct_url(apply_url) or direct_url(url),id='ats:'+f['type']+':'+f['slug'].lower()+':'+str(ident),company=f['name'],title=title,location=loc,level=level,sector=sector(title),salary=text(salary),posted=date(posted),deadline=closing,start=start,duration='',university='',requirements='Check the employer advert.',description='Published on the employer’s public careers feed. Check degree level, closing date and eligibility on the original listing.',url=url,live=not closed,vacancyStatus='closed' if closed else 'listed',discovery=level=='Unconfirmed',source=f['name']+' careers feed')

def run_feed(f):
    kind=f['type']; slug=quote(f['slug'],safe=''); name=f['name']+' careers feed'; out=[]; partial=False
    def add(*args,**kwargs):
        j=normalized(f,*args,**kwargs)
        if j:out.append(j)
    try:
        if kind in ('greenhouse','greenhouse-eu'):
            host='boards-api.eu.greenhouse.io' if kind.endswith('-eu') else 'boards-api.greenhouse.io'
            rows=request(f'https://{host}/v1/boards/{slug}/jobs?content=true')['jobs']
            for j in rows:add(j['id'],j['title'],j.get('location',{}).get('name'),j.get('absolute_url'),j.get('content','')) # updated_at is not release date
        elif kind in ('lever','lever-eu'):
            host='api.eu.lever.co' if kind.endswith('-eu') else 'api.lever.co'; skip=0
            for page in range(20):
                rows=request(f'https://{host}/v0/postings/{slug}?mode=json&limit=100&skip={skip}')
                if not isinstance(rows,list):raise ValueError('Unexpected feed format')
                for j in rows:add(j['id'],j.get('text'),j.get('categories',{}).get('allLocations') or j.get('categories',{}).get('location'),j.get('hostedUrl'),j.get('descriptionPlain') or j.get('description'),apply_url=j.get('applyUrl',''))
                if len(rows)<100:break
                skip+=len(rows);time.sleep(.3)
            else:partial=True
        elif kind=='ashby':
            rows=request(f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true')['jobs']
            for j in rows:
                if j.get('isListed') is False:continue
                add(j.get('id') or hashlib.sha256(str(j.get('jobUrl')).encode()).hexdigest()[:20],j.get('title'),[j.get('location'),j.get('secondaryLocations')],j.get('jobUrl'),j.get('descriptionPlain') or j.get('descriptionHtml'),j.get('publishedAt'),apply_url=j.get('applyUrl',''))
        elif kind=='smart':
            base=f'https://api.smartrecruiters.com/v1/companies/{slug}/postings'; offset=0
            for page in range(20):
                params={'limit':100,'offset':offset}
                # Small boards can be checked in full, without relying on ATS keyword matching.
                if f['slug'].lower()!='ajbell1':params['q']='apprentice'
                payload=request(base+'?'+urlencode(params));rows=payload['content']
                for j in rows:
                    loc=j.get('location',{}); location=' '.join(str(loc.get(k) or '') for k in ('city','region','country'))
                    if not APP.search(j.get('name','')) or not UK.search(location) or BLOCK.search(j.get('name','')):continue
                    try:
                        detail=request(base+'/'+quote(str(j['id']),safe=''));time.sleep(.15)
                        desc=text(detail.get('jobAd',{}).get('sections',{}))
                    except Exception:partial=True;desc='';detail={}
                    add(j['id'],j.get('name'),location,f'https://jobs.smartrecruiters.com/{slug}/{quote(str(j["id"]),safe="")}',desc,j.get('releasedDate'),apply_url=detail.get('applyUrl') or j.get('applyUrl',''))
                offset+=len(rows)
                if not rows or offset>=int(payload.get('totalFound',offset)) or len(rows)<100:break
                time.sleep(.3)
            else:partial=True
        elif kind=='recruitee-xml':
            # Opt in only with the actual documented XML offer feed URL supplied by the employer.
            tree=request(f['url'],xml=True)
            nodes=tree.findall('.//offer')+tree.findall('.//job')
            if not nodes and tree.tag not in ('offers','jobs','source'):raise ValueError('Unrecognised XML feed')
            for j in nodes:
                fields={child.tag:text(child.text) for child in j};add(fields.get('id') or fields.get('url'),fields.get('title') or fields.get('name'),fields.get('location') or fields.get('city'),fields.get('careers_url') or fields.get('url'),fields.get('description'),fields.get('published_at'))
        elif kind in ('personio','personio-de'):
            host='jobs.personio.de' if kind.endswith('-de') else 'jobs.personio.com'
            tree=request(f'https://{slug}.{host}/xml?language=en',xml=True)
            if tree.tag!='workzag-jobs':raise ValueError('Unrecognised Personio feed')
            for j in tree.findall('position'):
                ident=j.findtext('id'); add(ident,j.findtext('name'),j.findtext('office'),f'https://{slug}.{host}/job/{ident}', ' '.join(x.text or '' for x in j.findall('.//value')))
        else:raise ValueError('Unsupported provider')
        return out,dict(name=name,ok=True,partial=partial,message=f'{len(out)} UK apprenticeship adverts; '+('partial feed; prior data retained' if partial else 'public feed checked'))
    except Exception as e:
        return out,dict(name=name,ok=bool(out),partial=True,message=f'Feed unavailable or incomplete: {type(e).__name__}: {str(e)[:150]}')


def registry():
    data=json.loads((ROOT/'employer_sources.json').read_text(encoding='utf-8'));out=[];seen=set()
    try:
        discovered=json.loads((ROOT/'discovered_boards.json').read_text(encoding='utf-8'))
        if isinstance(discovered,list):data['feeds']+=discovered[:30]
    except (OSError,ValueError,TypeError):pass
    allowed={'smart','greenhouse','greenhouse-eu','lever','lever-eu','ashby','personio','personio-de','recruitee-xml'}
    for f in data.get('feeds',[]):
        if f.get('type') not in allowed or not TOKEN.fullmatch(str(f.get('slug',''))) or not str(f.get('name','')).strip():continue
        if f['type']=='recruitee-xml':
            p=urlparse(f.get('url',''))
            if p.scheme!='https' or not p.hostname or not p.hostname.endswith('.recruitee.com'):continue
        k=(f['type'],f['slug'].lower())
        if k not in seen:out.append(f);seen.add(k)
    return out[:100]
