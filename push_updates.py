"""Optional generic vacancy alerts. Never reads personal trackers, notes or CVs."""
import json, os, re, sys
from pathlib import Path
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).parent
STATE=ROOT/'push_seen.json'

def candidates(doc):
    return {str(j.get('id')) for j in doc.get('jobs',[]) if j.get('id') and j.get('live') and not j.get('cached') and not j.get('discovery')}

def valid_endpoint(value):
    try:
        u=urlsplit(value); h=u.hostname or ''
        return u.scheme=='https' and u.port in (443,None) and not u.username and not u.password and not u.fragment and (h in ('fcm.googleapis.com','updates.push.services.mozilla.com','web.push.apple.com') or bool(re.fullmatch(r'[a-z0-9-]+\.notify\.windows\.com',h)))
    except (ValueError,TypeError):return False

def main():
    config=[os.environ.get(k,'').strip() for k in ('CAREER_SUPABASE_URL','CAREER_SUPABASE_SERVICE_KEY','CAREER_VAPID_PRIVATE_KEY','CAREER_VAPID_SUBJECT')]
    if not all(config):print('Background push not configured; skipped.');return
    base,key,private,subject=config
    if not re.fullmatch(r'https://[a-z0-9-]+\.supabase\.co/?',base) or not subject.startswith(('mailto:','https://')):raise ValueError('Invalid push configuration')
    doc=json.loads((ROOT/'site/vacancies.json').read_text()); now=candidates(doc)
    if not any(s.get('ok') for s in doc.get('sources',[])):print('No fresh source; push skipped.');return
    try:old=set(json.loads(STATE.read_text()))
    except (OSError,ValueError):STATE.write_text(json.dumps(sorted(now)));print('Initial push baseline created; no alert sent.');return
    new=now-old
    if not new:return
    from pywebpush import webpush, WebPushException
    api=base.rstrip('/')+'/rest/v1/career_push_subscriptions';headers={'apikey':key,'Authorization':'Bearer '+key,'Accept':'application/json'}
    # At most 200 endpoints per run; use a stable cap to keep free workflow runtime bounded.
    req=Request(api+'?select=user_id,endpoint,subscription&limit=200&order=created_at.asc',headers=headers)
    with urlopen(req,timeout=15) as response:rows=json.load(response)
    def send(row):
        endpoint=row.get('endpoint','');sub=row.get('subscription') or {}
        if not valid_endpoint(endpoint) or sub.get('endpoint')!=endpoint:return 'invalid'
        try:
            webpush(subscription_info=sub,data=json.dumps({'count':len(new)}),vapid_private_key=private,vapid_claims={'sub':subject},ttl=3600,timeout=8,headers={'Urgency':'low'})
            return 'sent'
        except WebPushException as exc:
            if exc.response is not None and exc.response.status_code in (404,410):
                try:
                    q=urlencode({'user_id':'eq.'+row['user_id'],'endpoint':'eq.'+endpoint})
                    with urlopen(Request(api+'?'+q,headers=headers,method='DELETE'),timeout=10):pass
                except Exception:pass
                return 'expired'
            return 'failed'
        except Exception:return 'failed'
    with ThreadPoolExecutor(max_workers=6) as ex:results=list(ex.map(send,rows))
    # Do not repeatedly alert users to the same roles if a subset fails.
    STATE.write_text(json.dumps(sorted(old|now)))
    print('Push delivery:',{k:results.count(k) for k in set(results)},';',len(new),'new vacancies. Max 200 registered devices per run.')
if __name__=='__main__':main()
