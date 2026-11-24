"""Optional private daily email runner. Run on a trusted computer, NOT the public website.
Requires firebase-admin, Application Default Credentials and a permitted SMTP relay.
No messages or recipient details are written into the public repository.
"""
from pathlib import Path
import json,os,ssl,smtplib,argparse
from email.message import EmailMessage
from datetime import datetime,timezone,timedelta
from urllib.parse import urlsplit

def matching(j,p,today):
    if not j.get('live') or j.get('cached') or j.get('vacancyStatus')!='listed' or j.get('linkStatus')=='may-be-unavailable':return False
    if j.get('firstSeen')!=today or (j.get('deadline') and j['deadline']<today):return False
    def tokens(s):return [x.strip().casefold() for x in str(s or '').replace(';',',').split(',') if x.strip()]
    words=tokens(p.get('interests'));places=tokens(p.get('locations'));text=(str(j.get('title',''))+' '+str(j.get('sector',''))).casefold()
    return (not words or any(x in text for x in words)) and (not places or any(x in str(j.get('location','')).casefold() for x in places))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--feed',default='https://playerlad2-hub.github.io/Apprenticeship/vacancies.json');parser.add_argument('--send',action='store_true',help='Without this flag, show counts only.');args=parser.parse_args()
    from urllib.request import urlopen
    import firebase_admin
    from firebase_admin import firestore,auth
    firebase_admin.initialize_app();db=firestore.client();today=datetime.now(timezone.utc).date().isoformat()
    with urlopen(args.feed,timeout=20) as f:feed=json.loads(f.read(20_000_000))
    stamp=datetime.fromisoformat(feed['checked'].replace('Z','+00:00'))
    if datetime.now(timezone.utc)-stamp>timedelta(hours=4):raise SystemExit('Public feed is stale; no digest sent.')
    if args.send and not all(os.environ.get(x) for x in ('CAREER_SMTP_HOST','CAREER_SMTP_USER','CAREER_SMTP_PASSWORD','CAREER_MAIL_FROM')):raise SystemExit('SMTP configuration missing. No messages sent.')
    sent=0;eligible=0
    for doc in db.collection('career_alerts').stream():
        v=doc.to_dict();uid=doc.id
        if not v.get('enabled'):continue
        try:u=auth.get_user(uid)
        except auth.UserNotFoundError:continue
        if u.disabled or not u.email_verified or u.email!=v.get('email'):continue
        jobs=[j for j in feed.get('jobs',[]) if matching(j,v,today)][:20]
        if not jobs:continue
        ledger=db.collection('career_alert_delivery').document(uid+'_'+today)
        if ledger.get().exists:continue
        eligible+=1
        if not args.send:continue
        # Claim before sending to prevent duplicate emails on retry; failures require operator review.
        try:ledger.create({'date':today,'createdAt':firestore.SERVER_TIMESTAMP,'state':'claimed'})
        except Exception:continue
        msg=EmailMessage();msg['Subject']='Career Hub: new matching apprenticeships';msg['From']=os.environ['CAREER_MAIL_FROM'];msg['To']=u.email
        lines=['New opportunities matching your Career Hub preferences:', '']
        for j in jobs:lines.append(f"{j.get('company')} — {j.get('title')} ({j.get('location')})")
        lines+=['','Browse current vacancies: https://playerlad2-hub.github.io/Apprenticeship/#opportunities','To unsubscribe, sign in and open Applicant essentials → Vacancy alerts.']
        msg.set_content('\n'.join(lines))
        try:
            with smtplib.SMTP_SSL(os.environ['CAREER_SMTP_HOST'],int(os.environ.get('CAREER_SMTP_PORT','465')),timeout=20,context=ssl.create_default_context()) as smtp:
                smtp.login(os.environ['CAREER_SMTP_USER'],os.environ['CAREER_SMTP_PASSWORD']);smtp.send_message(msg)
            ledger.update({'state':'sent'});sent+=1
        except Exception:ledger.update({'state':'failed'})
    print(f'Eligible digests: {eligible}; sent: {sent}. No email addresses logged.')
if __name__=='__main__':main()
