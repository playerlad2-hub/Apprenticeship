/* Keep vacancy list interactions in place, with accessible exit and reflow motion. */
(()=>{
'use strict';
const action=doAction;
const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const active=new Set();
function cardKey(card){return card.querySelector('[data-act="hidejob"]')?.dataset.id||''}
function boxes(list){return new Map([...list.querySelectorAll('.hub-job')].map(c=>[cardKey(c),c.getBoundingClientRect()]));}
function refreshHiddenCount(){const b=document.querySelector('[data-act="hiddenjobs"]');if(b)b.textContent=`Hidden vacancies (${hiddenIds.size})`;}
doAction=function(act,node){
 if(act!=='hidejob'||screen!=='opportunities')return action(act,node);
 const j=hJob(node?.dataset?.id),card=node?.closest('.hub-job'),list=document.getElementById('h-vacancies');
 if(!j||!card||!list||!list.contains(card))return action(act,node);
 if(active.has(j.id)||card.classList.contains('vacancy-leaving'))return;
 active.add(j.id);
 const restoring=isHidden(j),keyboardFocus=document.activeElement===node;
 if(restoring){hiddenIds.delete(hiddenKey(j));hiddenIds.delete('id:'+j.id)}else{hiddenIds.add(hiddenKey(j))}
 saveHidden();refreshHiddenCount();hToast(restoring?'Vacancy restored':'Vacancy hidden');
 card.classList.add('vacancy-leaving');card.setAttribute('aria-hidden','true');card.inert=true;
 const finish=()=>{
  active.delete(j.id);
  if(screen!=='opportunities'||document.getElementById('h-vacancies')!==list||!list.contains(card))return;
  const before=boxes(list),scroll=window.scrollY,scrollX=window.scrollX;
  const order=[...list.querySelectorAll('.hub-job')].map(cardKey),index=order.indexOf(j.id);
  hDrawJobs();refreshHiddenCount();
  window.scrollTo({top:scroll,left:scrollX,behavior:'instant'});
  if(!reduced()&&typeof Element.prototype.animate==='function'){
   for(const c of list.querySelectorAll('.hub-job')){
    const prior=before.get(cardKey(c)),after=c.getBoundingClientRect();
    if(prior){const x=prior.left-after.left,y=prior.top-after.top;if(Math.abs(x)+Math.abs(y)>2)c.animate([{transform:`translate(${x}px,${y}px)`},{transform:'translate(0,0)'}],{duration:240,easing:'cubic-bezier(.2,.75,.25,1)'});}
    else c.animate([{opacity:0,transform:'translateY(8px)'},{opacity:1,transform:'translateY(0)'}],{duration:200,easing:'ease-out'});
   }
  }
  if(keyboardFocus){const cards=[...list.querySelectorAll('.hub-job')];const next=cards[Math.min(Math.max(index,0),cards.length-1)]?.querySelector('[data-act="hidejob"]')||document.querySelector('[data-act="hiddenjobs"]');next?.focus({preventScroll:true});}
 };
 if(reduced()||typeof card.animate!=='function'){finish();return;}
 const motion=card.animate([{opacity:1,transform:'translateX(0) scale(1)'},{opacity:0,transform:'translateX(22px) scale(.975)'}],{duration:210,easing:'cubic-bezier(.4,0,.9,.6)',fill:'forwards'});
 motion.finished.then(finish,finish);
};
})();
