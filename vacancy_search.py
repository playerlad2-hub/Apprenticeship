"""Local Career Hub launcher. Python 3.9+, no extra packages."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime, timezone
import json, re, time, threading, webbrowser, os, hashlib, html, getpass
from urllib.parse import urlencode, parse_qsl, urlunparse
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://www.findapprenticeship.service.gov.uk'
PORT = 8765
HTML = Path(__file__).with_name('Career_Hub.html')
LOCK = threading.Lock()
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag=tag; self.attrs=dict(attrs); self.parent=parent; self.children=[]
    def text(self):
        return ' '.join(' '.join(x.text() if isinstance(x,Node) else x for x in self.children).split())
    def walk(self):
        yield self
        for x in self.children:
            if isinstance(x,Node): yield from x.walk()
class Tree(HTMLParser):
    def __init__(self,markup):
        super().__init__(convert_charrefs=True); self.root=Node(); self.current=self.root; self.feed(markup)
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs,self.current); self.current.children.append(n)
        if tag not in VOID: self.current=n
    def handle_startendtag(self,tag,attrs):
        self.current.children.append(Node(tag,attrs,self.current))
    def handle_endtag(self,tag):
        n=self.current
        while n.parent:
            if n.tag==tag: self.current=n.parent; return
            n=n.parent
    def handle_data(self,data): self.current.children.append(data)

def get_page(page,level=6):
    url=BASE+'/apprenticeships?levelIds='+str(level)+'&pageNumber='+str(page)
    req=Request(url, headers={'User-Agent':'CareerHubPersonal/1.0 (personal apprenticeship search)','Accept':'text/html'})
    with urlopen(req,timeout=12) as r:
        return r.read(4_000_000).decode('utf-8',errors='replace')

def iso_date(text):
    m=re.search(r'\b(\d{1,2}\s+[A-Za-z]+\s+\d{4})\b',text)
    if not m:return ''
    try:return datetime.strptime(m[1],'%d %B %Y').date().isoformat()
    except ValueError:return ''

def sector(course):
    t=course.lower()
    for label, words in [('Technology',['digital','software','cyber','machine learning','data','computing','artificial intelligence']),('Finance',['account','finance','bank','investment','actuar']),('Engineering',['engineer','manufactur','electrical','construction','survey']),('Health',['nurs','health','physio','medical','pharmacy']),('Business',['management','business','marketing','project','chartered manager'])]:
        if any(w in t for w in words):return label
    return 'Other'

def parse(markup,level=6):
    tree=Tree(markup).root; full=tree.text()
    total_match=re.search(r'([\d,]+)\s+results?\s+found',full,re.I)
    total=int(total_match[1].replace(',','')) if total_match else None
    if total is None and re.search(r'no (?:matching |apprenticeship )?results|no apprenticeships found',full,re.I):total=0
    jobs=[]
    for a in tree.walk():
        if a.tag!='a':continue
        href=a.attrs.get('href',''); match=re.search(r'/apprenticeship/(?:reference/|VAC)?(\d+)(?:[/?#]|$)',href,re.I)
        if not match:continue
        title=a.text()
        if not title:continue
        n=a.parent; card=None
        while n and n.parent:
            val=n.text()
            if 'Training course' in val and 'Start date' in val and 'Wage' in val and 'Closes' in val:
                card=n;break
            n=n.parent
        if card is None:continue
        txt=card.text(); after=txt.split(title,1)[-1]
        m=re.search(r'Start date\s*(.*?)\s*Training course\s*(.*?)\s*Wage\s*(.*?)\s*(Closes.*?)(?:\s*Posted|$)',after,re.I)
        if not m:continue
        start,course,wage,closing=(x.strip() for x in m.groups())
        if not re.search(r'level\s*'+str(level)+r'\b',course,re.I):continue
        deadline=iso_date(closing)
        posted_match=re.search(r'\bPosted(?: on)?\s*:?\s*(.*)',txt,re.I)
        posted=iso_date(posted_match[1]) if posted_match else ''
        if deadline and deadline<datetime.now().date().isoformat():continue
        prefix=after.split('Start date',1)[0].strip()
        # Use semantic paragraph boundaries to separate company and location.
        parts=[]
        for q in card.walk():
            if q.tag in ('p','dd'):
                t=q.text()
                if t and t in prefix and t not in parts:parts.append(t)
        if len(parts)>=2: company,location=parts[0],parts[1]
        elif len(parts)==1 and prefix.startswith(parts[0]) and prefix!=parts[0]: company,location=parts[0],prefix[len(parts[0]):].strip()
        else:
            # Some layouts use spans rather than paragraphs; keep the original label intact.
            company=prefix or 'See advert';location='See official advert'
        # Public general career search; omit explicitly weapons-related roles.
        if re.search(r'\b(weapons?|munition[s]?|missiles?|firearms?|explosives?)\b',title+' '+course,re.I):continue
        url=urljoin(BASE,href)
        jobs.append(dict(id='gov-'+match[1],company=company,title=title,location=location,sector=sector(course+' '+title),level=str(level),salary=wage,posted=posted,deadline=deadline,start=start,duration='See official advert',university='See official advert',requirements='See the official advert for qualifications and eligibility.',description='Training course: '+course,url=url,live=True,source='GOV.UK Level '+str(level)))
    return total,jobs

def search(level=6):
    found={}; seen=set(); partial=False
    for page in range(1,151):
        try:
            total,jobs=parse(get_page(page,level),level)
            if total is None:raise ValueError('The official search page format was not recognised.')
            if total==0 and page==1:break
            if not jobs:raise ValueError('No eligible records were extracted; check the page format or filters.')
            signature=tuple(j['id']+'|'+j['location'] for j in jobs)
            if signature in seen:raise ValueError('Repeated search page detected.')
            seen.add(signature)
            for j in jobs:
                if j['id'] in found:
                    if j['location'] not in found[j['id']]['location']:
                        found[j['id']]['location']+=' / '+j['location']
                else:found[j['id']]=j
            if page*10>=total:break
            time.sleep(.35)
        except Exception as exc:
            if not found:raise RuntimeError('GOV.UK search unavailable: '+str(exc)) from exc
            partial=True;break
    else:partial=True
    return dict(jobs=list(found.values()),partial=partial,checked=datetime.now(timezone.utc).isoformat())


# General web discovery searches by discipline and region, not employer name.
# A Brave Search API key is optional and stays in this local process.
SECTORS=['digital technology cyber security software data','engineering manufacturing','finance accounting actuarial banking','business consulting management','construction surveying property','healthcare life sciences nursing','law legal solicitor','energy utilities transport','retail logistics supply chain','marketing communications media','education public services','agriculture environment hospitality']
REGIONS=['London','South East England','West Midlands','East Midlands','North West England','North East England','Yorkshire and the Humber','South West England','East of England','Scotland','Wales','Northern Ireland']
YEAR=datetime.now().year+1 if datetime.now().month>=8 else datetime.now().year
QUERIES=[f'UK degree apprenticeship {YEAR} applications open',f'UK level 6 apprenticeship {YEAR} vacancies careers',f'UK degree apprentice vacancies apply now']+[f'UK degree apprenticeship {YEAR} {x} apply' for x in SECTORS]+[f'{x} degree apprenticeship {YEAR} vacancies apply' for x in REGIONS]+[f'UK {x} degree apprentice vacancies apply' for x in ['technology solutions','cyber security','software developer','data science','business management','chartered manager','financial services','quantity surveyor','graduate apprenticeship Scotland','degree apprenticeships Wales','higher level apprenticeship degree Northern Ireland']]
QUERIES=list(dict.fromkeys(QUERIES+[f'UK {YEAR} apprenticeship {x} careers vacancy degree programme' for x in ['digital technology solutions','software engineering','cyber security analyst','data analyst','business analyst','professional services','chartered accountant','project management','quantity surveying','civil engineering','solicitor','insurance','actuarial']]))
BRAVE_KEY=os.environ.get('BRAVE_SEARCH_API_KEY','').strip()

def clean_text(value):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',str(value or '')))).strip()

def parse_web(payload):
    out=[]
    for row in payload.get('web',{}).get('results',[]):
        title=clean_text(row.get('title'));desc=clean_text(row.get('description'));url=str(row.get('url',''));p=urlparse(url)
        if p.scheme not in ('http','https') or not p.hostname or not title:continue
        text=title+' '+desc
        if not re.search(r'\b(?:apprentice|apprentices|apprenticeship|apprenticeships)\b',text,re.I):continue
        if re.search(r'\b(weapons?|munitions?|missiles?|firearms?|explosives?)\b',text,re.I):continue
        if CLOSED.search(text) or BLOCK.search(text):continue
        if re.search(r'\b(how to (?:find|apply)|what is (?:a|an)|guide to|salary guide|interview tips|practice tests)\b',title,re.I):continue
        # Search engine excerpts can be stale or generic. Never assert a lead is open.
        match=re.search(r'\b(?:level\s*|L)([2-7])\b',text,re.I)
        level=match[1] if match else ('Degree' if re.search(r'degree apprentice|graduate apprentice',text,re.I) else 'Unconfirmed')
        if level not in ('6','7','Degree','Unconfirmed'):continue
        salary=re.search(r'£\s?\d{2,3},\d{3}(?:\s*[-–]\s*£?\d{2,3},\d{3})?',desc)
        out.append(dict(id='web:'+hashlib.sha256(url.split('#')[0].encode()).hexdigest()[:24],company=p.hostname.removeprefix('www.'),title=title,location='UK search · confirm location',sector=sector(text),level=level,salary=salary.group() if salary else '',deadline='',start='',duration='',university='',requirements='',description=desc+' — Search result excerpt. Verify current vacancy status, location and entry requirements on the original advert.',url=url,live=False,discovery=True,source='Wider web (Brave Search)'))
    return out

def search_web(key):
    if not key:return [],dict(name='Wider web (Brave Search)',ok=False,message='Not configured. Set a Brave Search API key in the launcher for automatic discovery.')
    out={};success=0;errors=0
    for q in QUERIES:
        try:
            params=urlencode(dict(q=q,count=20,country='GB',search_lang='en',safesearch='strict'))
            req=Request('https://api.search.brave.com/res/v1/web/search?'+params,headers={'Accept':'application/json','X-Subscription-Token':key,'User-Agent':'CareerHubPersonal/2.0'})
            with urlopen(req,timeout=5) as r: payload=json.loads(r.read(2_000_000))
            for job in parse_web(payload):out[job['id']]=job
            success+=1
        except Exception as e:
            errors+=1
            if getattr(e,'code',0) in (401,403,429):break
            if errors>=8:break
        time.sleep(.3)
    return list(out.values()),dict(name='Wider web (Brave Search)',ok=success>0,partial=success<len(QUERIES),message=f'{success}/{len(QUERIES)} queries completed; {len(out)} unverified leads. '+('Some queries failed or were not attempted.' if success<len(QUERIES) else 'Check each advert before applying.'))

def national_gov(level=6):
    name='GOV.UK Level '+str(level)
    try:
        d=search(level);return d['jobs'],dict(name=name,ok=True,partial=d['partial'],message=f"{len(d['jobs'])} official adverts retrieved"+(' (partial search)' if d['partial'] else ''))
    except Exception as e:return [],dict(name=name,ok=False,partial=True,message='Official search failed: '+str(e))


# Public multi-employer directories, no search API key needed for these sources.
UCAS='https://www.ucas.com/explore/search/apprenticeships'
OPEN='https://www.openapprenticeships.org/search?lvl=6&lvl=7'
SOURCE_CACHE=Path(__file__).with_name('vacancy_cache.json')
BLOCK=re.compile(r'\b(weapons?|munitions?|missiles?|firearms?|explosives?|gambling|sports betting|casino|pornograph\w*)\b',re.I)
CLOSED=re.compile(r'\b(register (?:your )?interest|talent community|applications (?:are |now )?closed|no longer accepting|vacancy (?:is )?closed|coming soon)\b',re.I)

def fetch_html(url):
    req=Request(url,headers={'User-Agent':'CareerHubPersonal/3.0 (personal vacancy search)','Accept':'text/html'})
    with urlopen(req,timeout=10) as r:return r.read(5_000_000).decode('utf-8','replace')

def parts_after(card,anchor):
    # Collect text after the vacancy title without flattening company/location boundaries.
    fragments=[]; active=False
    def visit(n):
        nonlocal active
        if n is anchor:active=True;return
        if isinstance(n,Node):
            if n.tag in ('script','style','svg'):return
            for item in n.children:visit(item)
        elif active:
            t=' '.join(n.split())
            if t:fragments.append(t)
    visit(card)
    return fragments

def date_numeric(s):
    try:return datetime.strptime(s,'%d/%m/%Y').date().isoformat()
    except ValueError:return ''

def board_job(source,url,title,company,location,level,salary='',deadline='',start='',description='',lead=False):
    if BLOCK.search(title+' '+description) or CLOSED.search(title):return None
    if deadline and deadline<datetime.now().date().isoformat():return None
    if start and re.fullmatch(r'\d{4}-\d\d-\d\d',start) and start<datetime.now().date().isoformat():return None
    return dict(id='board:'+hashlib.sha256(url.encode()).hexdigest()[:24],company=company or 'See advert',title=title,location=location or 'See advert',level=level,sector=sector(title+' '+description),salary=salary,deadline=deadline,start=start,university='See advert',duration='See advert',requirements='Check the original advert for entry requirements.',description=description or 'Published in '+source+'. Check the original advert for current availability.',url=url,live=not lead,discovery=lead,source=source)

def parse_ucas(markup):
    tree=Tree(markup).root; out={}; seen=set(); full=tree.text()
    total=re.search(r'\b([\d,]+)\s+results\b',full,re.I)
    pages=re.search(r'Page\s+\d+\s+of\s+(\d+)',full,re.I)
    for a in tree.walk():
        if a.tag!='a':continue
        url=urljoin(UCAS,a.attrs.get('href','')); up=urlparse(url)
        if up.hostname!='services.ucas.com' or '/careerfinder/vacancy/' not in up.path:continue
        title=a.text()
        if not title or url in seen:continue
        n=a.parent
        while n and n.parent:
            txt=n.text()
            if 'Apprenticeship level' in txt and 'Apply by' in txt and 'Salary' in txt:break
            n=n.parent
        if not n or not n.parent:continue
        fields=parts_after(n,a); tail=' '.join(fields)
        m=re.search(r'^(.*?)\s*Apprenticeship level\s*(.*?)\s*Salary\s*(.*?)\s*Industry\s*(.*?)\s*Apply by\s*\|\s*Start date\s*(\d{1,2}/\d{1,2}/\d{4})\s*\|\s*(\d{1,2}/\d{1,2}/\d{4})',tail,re.I)
        if not m:continue
        prefix,lev,salary,industry,close,start=m.groups(); seen.add(url)
        if not re.search(r'Degree Apprenticeship|Graduate Apprenticeship|Level 6\b',lev,re.I):continue
        # Scotland SCQF 10 is degree level, not English Level 10.
        level='7' if re.search(r'Level 7\b',lev) else '6' if re.search(r'Level 6\b',lev) else 'Degree'
        pre=[]
        for f in fields:
            if 'Apprenticeship level' in f:break
            pre.append(f)
        company=pre[0] if pre else prefix; location=' '.join(pre[1:])
        job=board_job('UCAS',url,title,company,location,level,salary,date_numeric(close),date_numeric(start),industry)
        if job:out[url]=job
    return (int(total[1].replace(',','')) if total else None,int(pages[1]) if pages else None,len(seen),list(out.values()),tuple(sorted(seen)))

def ucas_search():
    found={}; pages_read=0; signatures=set(); expected=None; parsed=0; reason=''; zero_pages=0; variants=['Degree Apprenticeship','Graduate Apprenticeship']
    for variant in variants:
        variant_seen=set(); expected=None
        for page in range(1,41):
            try:
                url=UCAS+'?'+urlencode({'page':page,'query':'','refinementList[Level.ApprenticeshipType][0]':variant,'refinementList[VacancyType][0]':'Apprenticeship'})
                total,pages,n,jobs,sig=parse_ucas(fetch_html(url))
                if total==0:zero_pages+=1;break
                if not n:raise ValueError('No readable vacancy cards')
                if sig in variant_seen:raise ValueError('Repeated page')
                variant_seen.add(sig);pages_read+=1;parsed+=n
                for j in jobs:found[j['id']]=j
                if pages is not None and page>=pages:break
                if total is not None and page*20>=total:break
                if pages is None and total is None:reason='Page count unavailable';break
                time.sleep(.3)
            except Exception as e:reason=str(e);break
        else:reason='Page safety limit reached'
    return list(found.values()),dict(name='UCAS',ok=pages_read>0 or zero_pages==len(variants),partial=bool(reason),message=f'{pages_read} pages read; {len(found)} eligible adverts. '+(f'Partial: {reason}' if reason else 'Pagination completed.'))

def parse_open(markup):
    tree=Tree(markup).root; found={}; full=tree.text(); total=re.search(r'\b([\d,]+) roles\b',full)
    for a in tree.walk():
        if a.tag!='a':continue
        url=urljoin(OPEN,a.attrs.get('href','')); path=urlparse(url).path
        if not path.startswith('/apprenticeship/'):continue
        title=a.text(); n=a.parent
        if not title:continue
        while n and n.parent:
            txt=n.text()
            if 'Degree level' in txt and ('Live, checked' in txt or 'Closing soon' in txt or 'Pay not stated' in txt):break
            n=n.parent
        if not n or not n.parent:continue
        tail=' '.join(parts_after(n,a))
        m=re.search(r'^(.*?)\s*Degree level\s*·?\s*(.*?)(?:Live, checked|Closing soon|Save|$)',tail,re.I)
        if not m:continue
        pre,salary=m.groups(); company,sep,location=pre.partition('·')
        if re.search(r'closed|taken down|not been able to check',tail,re.I):continue
        j=board_job('Open Apprenticeships',url,title,company.strip(),location.strip(),'Degree',salary.strip(),description='Degree-level directory listing; check exact level and closing date on the advert.')
        if j:found[j['id']]=j
    return (int(total[1].replace(',','')) if total else None,list(found.values()))

def open_search():
    try:
        total,jobs=parse_open(fetch_html(OPEN))
        if total!=0 and not jobs:raise ValueError('No readable vacancy cards')
        # The public page uses a dynamic Show more control. Do not invent an API.
        partial=total is None or len(jobs)<total
        return jobs,dict(name='Open Apprenticeships',ok=True,partial=partial,message=f'{len(jobs)} eligible listings from initial public page'+(f' of {total} advertised roles' if total is not None else '')+('. More results require the source website.' if partial else '.'))
    except Exception as e:return [],dict(name='Open Apprenticeships',ok=False,partial=True,message='Unavailable: '+str(e))

def canonical(url):
    p=urlparse(url); query=urlencode([(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k.lower() not in ('source','ref','tracking')]);return urlunparse((p.scheme,p.netloc.lower(),p.path.rstrip('/'),'',query,''))

def nationwide():
    tasks=[national_gov,lambda:national_gov(7),ucas_search,open_search,lambda:search_web(BRAVE_KEY)]
    try:old=json.loads(SOURCE_CACHE.read_text(encoding='utf-8'))
    except Exception:old={}
    result={};statuses=[]
    today=datetime.now(timezone.utc).date().isoformat()
    old_by_url={canonical(j['url']):j for records in old.values() if isinstance(records,list) for j in records if isinstance(j,dict) and j.get('url')}
    with ThreadPoolExecutor(max_workers=5) as ex:
        for f in [ex.submit(t) for t in tasks]:
            try:jobs,status=f.result()
            except Exception as e:jobs=[];status=dict(name='Unknown source',ok=False,message=str(e))
            name=status['name'];previous=old.get(name,[])
            # Preserve missing records when a source was unavailable or only partially read.
            merged={j['id']:{**j,'cached':True} for j in previous if not j.get('deadline') or j['deadline']>=datetime.now().date().isoformat()} if not status.get('ok') or status.get('partial') else {}
            for j in jobs:
                prev=old_by_url.get(canonical(j['url']),{})
                if j.get('deadline') and j['deadline']<today:continue
                merged[j['id']]={**j,'source':name,'cached':False,'posted':j.get('posted') or prev.get('posted',''),'firstSeen':prev.get('firstSeen') or today}
            result[name]=list(merged.values());statuses.append(status)
    try:SOURCE_CACHE.write_text(json.dumps(result,ensure_ascii=False),encoding='utf-8')
    except OSError:pass
    best={}
    for records in result.values():
        for j in records:
            if j.get('deadline') and j['deadline']<today:continue
            k=canonical(j['url'])
            rank=lambda x:(bool(x.get('live') and not x.get('cached')),not x.get('discovery',False),not x.get('cached',False),bool(x.get('deadline')),bool(x.get('posted')))
            if k not in best or rank(j)>rank(best[k]):best[k]=j
    jobs=list(best.values())
    return dict(jobs=jobs,sources=statuses,checked=datetime.now(timezone.utc).isoformat())


class Handler(BaseHTTPRequestHandler):
    def send_data(self,data,content_type,status=200):
        self.send_response(status);self.send_header('Content-Type',content_type);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers()
        try:self.wfile.write(data)
        except (BrokenPipeError,ConnectionResetError):pass
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/','/Career_Hub.html'):
            self.send_data(HTML.read_bytes(),'text/html; charset=utf-8');return
        if path in ('/api/vacancies','/api/nationwide'):
            # Only requests from the local site; no cross-origin access.
            if self.headers.get('Sec-Fetch-Site')=='cross-site':self.send_error(403);return
            if not LOCK.acquire(False):
                self.send_data(json.dumps({'error':'A search is already running. Try refreshing shortly.'}).encode(),'application/json',409);return
            try: result=nationwide() if path=='/api/nationwide' else search();status=200
            except Exception as e:result={'error':str(e)};status=503
            finally:LOCK.release()
            self.send_data(json.dumps(result,ensure_ascii=False).encode(),'application/json; charset=utf-8',status);return
        self.send_error(404)
    def log_message(self,*args):pass

if __name__=='__main__':
    if not HTML.exists():raise SystemExit('Keep Career_Hub.html beside this launcher.')
    try:server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler)
    except OSError:raise SystemExit('Port 8765 is already in use. Close the other Career Hub window or server first.')
    if not BRAVE_KEY:
        print('Optional: set BRAVE_SEARCH_API_KEY before launching for wider-web searches. Each refresh uses up to '+str(len(QUERIES))+' API requests; provider limits and charges may apply.')
    print('Career Hub: http://127.0.0.1:8765/\nKeep this window open while using the site. Press Ctrl+C to stop.')
    webbrowser.open('http://127.0.0.1:8765/')
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
