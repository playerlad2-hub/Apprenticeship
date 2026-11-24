/* Account-specific browser storage. No account credentials are stored here. */
(()=>{
 const scopeKey='career_workspace_session_v1';
 const get=Storage.prototype.getItem,set=Storage.prototype.setItem,remove=Storage.prototype.removeItem;
 let scope='';try{scope=get.call(sessionStorage,scopeKey)||''}catch{}
 if(!/^[A-Za-z0-9_-]{1,128}$/.test(scope))scope='';
 const privateKey=k=>/^(career_plus_|career_hidden_v2$|career_hub_tracker_v1$|career_hub_extra_vacancies_v1$|cognitive_lab_results_v2$)/.test(String(k));
 const key=(obj,k)=>obj===localStorage&&scope&&privateKey(k)?`career_account_${scope}:${k}`:k;
 Storage.prototype.getItem=function(k){return get.call(this,key(this,k))};
 Storage.prototype.setItem=function(k,v){return set.call(this,key(this,k),v)};
 Storage.prototype.removeItem=function(k){return remove.call(this,key(this,k))};
 if(scope)document.documentElement.classList.add('workspace-locked');
 window.careerWorkspace={scope,confirm(uid){uid=uid||'';if(uid===scope){document.documentElement.classList.remove('workspace-locked');return true}try{if(uid)set.call(sessionStorage,scopeKey,uid);else remove.call(sessionStorage,scopeKey);sessionStorage.setItem('career_workspace_return','account');}catch{}location.reload();return false;},clear(){const prefix=scope?`career_account_${scope}:`:'';for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(scope?k.startsWith(prefix):privateKey(k))remove.call(localStorage,k)}},unlockGuest(){if(scope)this.confirm('');else document.documentElement.classList.remove('workspace-locked')}};
})();
