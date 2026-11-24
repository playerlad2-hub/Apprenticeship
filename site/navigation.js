/* Organised navigation; applied after all feature extensions. */
const careerNavGroups = [
  ['Overview', ['home','focus']],
  ['Applications', ['opportunities','tracker','compare','journey','planner','studio']],
  ['Preparation', ['tools','cv','menu','prep','progress']],
  ['Personal', ['notifications','account','settings','support']]
];
const careerNavIcons = {
  cv: '<path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6M9 16h6"/>',
  home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21v-7h6v7"/>',
  focus: '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
  opportunities: '<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18m-11 0v2h4v-2"/>',
  tracker: '<rect x="5" y="4" width="14" height="18" rx="2"/><rect x="9" y="2" width="6" height="4" rx="1"/><path d="m8 12 2 2 5-5M8 18h8"/>',
  compare: '<path d="M12 3v18M4 6h16M3 14l4-8 4 8m2 0 4-8 4 8M3 14a4 4 0 0 0 8 0m2 0a4 4 0 0 0 8 0M8 21h8"/>',
  journey: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16m6-16v16M5.5 8H7m4 0h2m4 0h1.5M5.5 11H7m4 2h2"/>',
  planner: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18m-13 5h.01m4 0h.01m4 0h.01M8 18h.01m4 0h.01"/>',
  studio: '<path d="M12 20H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v5M7 7h7M7 11h4m-4 4h3m4 5 1-4 5-5 3 3-5 5z"/>',
  tools: '<path d="M3 8l9-4 9 4-9 4-9-4zM6 10v6c4 3 8 3 12 0v-6M21 8v7"/>',
  menu: '<path d="M6 7h12c3 0 4 3 4 7s-1 5-3 5l-4-4H9l-4 4c-2 0-3-1-3-5s1-7 4-7Z"/><path d="M7 10v5m-2.5-2.5h5m6-1h.01m3 3h.01"/>',
  prep: '<path d="M4 4h6a2 2 0 0 1 2 2v15a4 4 0 0 0-4-3H3V5a1 1 0 0 1 1-1Zm16 0h-6a2 2 0 0 0-2 2v15a4 4 0 0 1 4-3h5V5a1 1 0 0 0-1-1Z"/>',
  progress: '<path d="M4 3v17h17M8 16v-4m5 4V8m5 8V5"/>',
  notifications: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9ZM10 21h4"/>',
  account: '<circle cx="12" cy="8" r="3.5"/><path d="M4.5 21v-2a7.5 7.5 0 0 1 15 0v2"/>',
  settings: '<path d="m9 3-.7 2.5-2 .9-2.4-1.2-2 3.5 1.9 1.8v3l-1.9 1.8 2 3.5 2.4-1.2 2 .9L9 21h4l.7-2.5 2-.9 2.4 1.2 2-3.5-1.9-1.8v-3l1.9-1.8-2-3.5-2.4 1.2-2-.9L13 3z"/><circle cx="11" cy="12" r="3"/>',
  support: '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78Z"/>'
};
hNav.push(['cv','CV builder','cv']);
const careerNavExisting = new Map(hNav.filter(n=>!['coverage','managefeeds'].includes(n[0])).map(n=>[n[0],n]));
const careerNavPrimary=['home','opportunities','tracker','menu'];
const careerNavOrder=[...new Set([...careerNavPrimary,...careerNavGroups.flatMap(g=>g[1]),...careerNavExisting.keys()])];
hNav.splice(0,hNav.length,...careerNavOrder.filter(id=>careerNavExisting.has(id)).map(id=>[...careerNavExisting.get(id)]));
function careerIcon(id){return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${careerNavIcons[id]||careerNavIcons.focus}</svg>`}
function careerNavActive(id){return (id==='cv'&&screen==='tools'&&nextTab==='cv')||(screen===id&&!(id==='tools'&&nextTab==='cv'))||(id==='menu'&&['tutorial','results'].includes(screen))}
hNavBtn=function(n,mobile=false){const active=careerNavActive(n[0]);return `<button type="button" data-act="${n[0]}" class="${active?'current':''}" ${active?'aria-current="page"':''}>${careerIcon(n[0])}<span>${escH(mobile?({'opportunities':'Find','tracker':'Tracker','menu':'Practice'}[n[0]]||n[1]):n[1])}</span></button>`};
function careerNavMarkup(more=false){const byId=new Map(hNav.map(n=>[n[0],n]));const groups=careerNavGroups.map(([label,ids])=>[label,ids.filter(id=>byId.has(id)&&(!more||!careerNavPrimary.includes(id)))]);const remaining=hNav.map(n=>n[0]).filter(id=>!careerNavGroups.some(g=>g[1].includes(id))&&(!more||!careerNavPrimary.includes(id)));if(remaining.length)groups.push(['Other tools',remaining]);return groups.filter(g=>g[1].length).map(([label,ids])=>`<section class="career-nav-group" aria-label="${label}"><div class="career-nav-label">${label}</div><div class="career-nav-links">${ids.map(id=>hNavBtn(byId.get(id))).join('')}</div></section>`).join('')}
const careerNavShell=shell;shell=function(main){careerNavShell(main);if(screen==='play')return;const mobile=document.querySelector('.hub-mobile');if(mobile){mobile.innerHTML=careerNavPrimary.map(id=>hNav.find(n=>n[0]===id)).filter(Boolean).map(n=>hNavBtn(n,true)).join('')+`<button type="button" data-act="more" class="${!careerNavPrimary.some(careerNavActive)?'current':''}"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg><span>More</span></button>`}};
const careerNavAction=doAction;doAction=function(act,node){if(act==='cv')return nextTools('cv');if(act==='tools')return nextTools('profile');if(act!=='more')return careerNavAction(act,node);const d=hShowModal('More tools','',`<nav class="career-more-nav" aria-label="More tools">${careerNavMarkup(true)}</nav>`);d.querySelectorAll('.career-more-nav [data-act]').forEach(b=>{const id=b.dataset.act;b.removeAttribute('data-act');b.onclick=()=>{d.close();doAction(id,b)}})};
