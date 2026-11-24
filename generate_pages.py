"""Generate public SEO pages from vacancy data; never read applicant workspaces."""
from pathlib import Path
from collections import defaultdict
from html import escape
from urllib.parse import quote,urlsplit
from datetime import datetime,timezone
import json,hashlib,os,re,xml.etree.ElementTree as ET,shutil
ROOT=Path(__file__).resolve().parent
SITE=ROOT/'site'
BASE=os.environ.get('CAREER_PUBLIC_URL','https://playerlad2-hub.github.io/Apprenticeship/').rstrip('/')+'/'
def clean(x):return escape(str(x or ''),quote=True)
def safeurl(x):
    try:
        p=urlsplit(x);return p.scheme=='https' and p.hostname and not p.username and not p.password
    except (TypeError,ValueError):return False
def key(x):return re.sub(r'[^a-z0-9]+','-',str(x).lower()).strip('-')[:65]+'-'+hashlib.sha256(str(x).encode()).hexdigest()[:12]
def state(j):
    today=datetime.now(timezone.utc).date().isoformat()
    if j.get('vacancyStatus')=='closed' or (j.get('deadline') and j['deadline']<today):return 'Closed'
    if j.get('cached') or j.get('vacancyStatus') in ('unknown','not-listed') or not j.get('live') or j.get('discovery') or j.get('linkStatus')=='may-be-unavailable':return 'Availability unconfirmed'
    return 'Recently listed'
def page(path,title,desc,content):
    dest=SITE/path;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{clean(title)} | Career Hub</title><meta name="description" content="{clean(desc[:160])}"><link rel="canonical" href="{clean(BASE+path)}"><link rel="icon" href="{clean(BASE+"icon-192.png")}"><link rel="stylesheet" href="{clean(BASE+"public.css")}"></head><body><header><a class="brand" href="{clean(BASE)}">Career Hub</a><nav><a href="{clean(BASE)}#opportunities">Find vacancies</a><a href="{clean(BASE)}#support">♡ Support</a></nav></header><main>{content}</main><footer><a href="{clean(BASE)}">Free apprenticeship tools</a> · <a href="{clean(BASE)}#support">Support</a></footer></body></html>',encoding='utf-8')
def generate(jobs):
    for d in ('vacancies','employers','guides'):
        if (SITE/d).exists():shutil.rmtree(SITE/d)
    paths=[''];groups=defaultdict(list);cards=[]
    for j in jobs:
        if not isinstance(j,dict) or not j.get('id') or not j.get('title') or not j.get('company'):continue
        p='vacancies/'+key(j['id'])+'.html';s=state(j);title=f"{j['title']} – {j['company']}";closed=s=='Closed';url=j.get('applyUrl') or j.get('url');fields=[('Location',j.get('location')),('Level',j.get('level')),('Salary',j.get('salary')),('Published',j.get('posted')),('Deadline',j.get('deadline')),('Start',j.get('start')),('Duration',j.get('duration')),('University',j.get('university'))]
        c=f'<p class="tag">{clean(s)}</p><h1>{clean(title)}</h1><dl>'+''.join(f'<div><dt>{clean(k)}</dt><dd>{clean(v or "Not published")}</dd></div>' for k,v in fields)+'</dl>'
        c+=f'<h2>About this role</h2><p>{clean(str(j.get("description") or "Read the employer advert for full details.")[:2200])}</p><h2>Entry requirements</h2><p>{clean(j.get("requirements") or "Check the employer advert.")}</p>'
        if safeurl(url):c+=f'<a class="button" rel="noopener noreferrer" href="{clean(url)}">{"View original advert" if closed else "Open application advert"}</a> '
        c+=f'<a class="button secondary" href="{clean(BASE+"#vacancy="+quote(str(j["id"]),safe=""))}">Open in Career Hub</a><p class="muted">Independent listing. Confirm current availability and requirements with the employer.</p>'
        # JobPosting deliberately withheld: imported feed data often lacks full employer-authorised text and complete location/date fields.
        page(p,title,j.get('description') or title,c)
        if not closed:paths.append(p)
        groups[j['company']].append((p,j,s))
        if not closed:cards.append(f'<li><a href="{clean(p.split("/")[-1])}">{clean(title)}</a> <span>{clean(s)}</span></li>')
    for company,rows in groups.items():
        p='employers/'+key(company)+'.html';open_rows=[r for r in rows if r[2]!='Closed'];paths.append(p)
        page(p,company+' apprenticeships','Explore published apprenticeship opportunities at '+company,f'<h1>{clean(company)} apprenticeships</h1><p>{len(open_rows)} currently listed or unconfirmed opportunities. Confirm availability with the employer.</p><ul>'+''.join(f'<li><a href="{clean(BASE+r[0])}">{clean(r[1]["title"])}</a> · {clean(r[2])}</li>' for r in rows)+'</ul>')
    page('vacancies/index.html','Degree apprenticeship vacancies','Browse UK apprenticeship listings','<h1>Degree apprenticeship vacancies</h1><p>Updated from the public vacancy directory.</p><ul>'+''.join(cards)+'</ul>');paths.append('vacancies/index.html')
    page('employers/index.html','Apprenticeship employers','Browse employer profiles','<h1>Apprenticeship employers</h1><ul>'+''.join(f'<li><a href="{clean(key(c)+".html")}">{clean(c)}</a></li>' for c in sorted(groups))+'</ul>');paths.append('employers/index.html')
    guides={
    'application-guide':('How to apply for degree apprenticeships',['Check the published qualifications, location, start date and closing date.','Tailor your CV and application answers to the role. Use specific evidence of your skills.','Track every application and its next action.','Prepare using original practice questions, not confidential test content.']),
    'assessment-guide':('Preparing for online assessments',['Find the provider named in your invitation.','Read the real instructions carefully. Practise numerical, verbal and logical skills with explanations.','Use timed practice after learning the underlying concepts.','Ask the employer about adjustments if you need them.']),
    'interview-guide':('Preparing for apprenticeship interviews',['Research the employer and the actual role.','Prepare specific examples using situation, task, action and result.','Practise explaining your motivation and skills.','Prepare questions about the degree, training and support.']),
    'offer-guide':('Comparing apprenticeship offers',['Compare the degree qualification, employer training, salary, commute and study support.','Check written conditions and acceptance deadlines.','Ask the employer about progression and university arrangements.'])}
    for slug,(title,points) in guides.items():
        p='guides/'+slug+'.html';page(p,title,title,'<h1>'+clean(title)+'</h1><ol>'+''.join('<li>'+clean(x)+'</li>' for x in points)+'</ol><p><a href="'+clean(BASE)+'">Use Career Hub’s free applicant tools</a></p>');paths.append(p)
    page('guides/index.html','Apprenticeship advice','Free applicant guides','<h1>Apprenticeship advice</h1><ul>'+''.join(f'<li><a href="{clean(k)}.html">{clean(v[0])}</a></li>' for k,v in guides.items())+'</ul>');paths.append('guides/index.html')
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns);root=ET.Element('{'+ns+'}urlset')
    for p in sorted(set(paths)):ET.SubElement(ET.SubElement(root,'{'+ns+'}url'),'{'+ns+'}loc').text=BASE+p
    ET.ElementTree(root).write(SITE/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    print('Generated',len(paths),'indexable public pages (closed listings remain accessible without job markup).')
if __name__=='__main__':generate(json.loads((SITE/'vacancies.json').read_text()).get('jobs',[]))
