(() => {
'use strict';
const data = window.CHATGPT_INCOME_DATA;
if (!data || !Array.isArray(data.chapters)) return;
const chapters = data.chapters;
const $ = id => document.getElementById(id);
const escape = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\"':'&quot;'}[c]));
const key = 'chatgpt-income-handbook-v1';
let state = { finished: [], favorite: [], day: [] };
try { const obj=JSON.parse(localStorage.getItem(key)||'{}');if(Array.isArray(obj.finished))state={...state,...obj}; } catch(_) { /* private browsing */ }
let current=chapters[0]?.id, query='';
function getChapterId(){return new URLSearchParams(location.search).get('chapter');}
function toast(message){const t=$('readerToast');t.textContent=message;t.hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>t.hidden=true,1800);}
function copyWechat(){const value='AIPMAndy';if(navigator.clipboard && navigator.clipboard.writeText){navigator.clipboard.writeText(value).then(()=>toast('微信号已复制')).catch(()=>window.prompt('请复制微信号：',value));}else window.prompt('请复制微信号：',value);}
function renderNav(){const groups = new Map(); chapters.forEach(c=>{if(!groups.has(c.category))groups.set(c.category,[]);groups.get(c.category).push(c);});const fragment=document.createDocumentFragment();let matches=0;
for (const [cat, items] of groups){const filt=items.filter(c=>(c.title+' '+c.summary+' '+c.category).toLowerCase().includes(query.toLowerCase()));if(!filt.length)continue;matches+=filt.length;const g=document.createElement('div');g.className='nav-group';const h=document.createElement('h3');h.textContent=cat;g.appendChild(h);for(const c of filt){const a=document.createElement('a');a.href='?chapter='+encodeURIComponent(c.id);a.className=c.id===current?'active':'';a.setAttribute('aria-current',c.id===current?'page':'false');const n=document.createElement('span');n.className='chapter-index';n.textContent=String(c.number).padStart(2,'0');const title=document.createElement('span');title.textContent=c.title;title.className='chapter-label';const done=document.createElement('span');done.className='done';done.textContent=state.finished.includes(c.id)?'✓':'';a.append(n,title,done);a.addEventListener('click',e=>{e.preventDefault();show(c.id,true);});g.appendChild(a);}fragment.appendChild(g);}
const target=$('chapterNav');target.replaceChildren(fragment);if(!matches){const p=document.createElement('p');p.className='empty';p.textContent='没有匹配的章节。';target.appendChild(p);}}
function show(id,updateURL){const c=chapters.find(a=>a.id===id)||chapters[0];if(!c)return;current=c.id;const pos=chapters.findIndex(x=>x.id===current);const src=data.sources.find(x=>x.id===c.source);
$('crumbCategory').textContent=c.category;$('crumbTitle').textContent=c.title;$('chapterBadge').textContent='CHAPTER '+String(c.number).padStart(2,'0')+' / '+chapters.length;$('chapterTitle').textContent=c.title;$('chapterSummary').textContent=c.summary;$('chapterMinutes').textContent='阅读约 '+c.minutes+' 分钟';
const done=state.finished.includes(c.id);$('chapterProgress').textContent=done?'✓ 已完成':'尚未完成';$('toggleFinished').textContent=done?'取消已完成':'标记已完成 ✓';
const list=$('chapterSteps');list.replaceChildren();for(const step of c.steps){const li=document.createElement('li');li.textContent=step;list.appendChild(li);}
$('chapterCheck').textContent=c.check;$('chapterPitfall').textContent=c.pitfall;
const link=$('chapterSource');link.href=src?.url||'docs/SOURCES.md';link.textContent='打开官方资料：'+(src?.name||'来源索引')+' ↗';
const setPage=(element,index,label)=>{const el=$(element);if(index<0||index>=chapters.length){el.hidden=true;return;}el.hidden=false;el.href='?chapter='+encodeURIComponent(chapters[index].id);el.textContent=label+chapters[index].title;el.onclick=e=>{e.preventDefault();show(chapters[index].id,true);};};
setPage('prevChapter',pos-1,'← ');setPage('nextChapter',pos+1,'下一章 → ');
document.title=c.title+' · ChatGPT 商业实践手册 · Andy';if(updateURL){const u=new URL(location.href);u.searchParams.set('chapter',c.id);history.pushState(null,'',u);window.scrollTo({top:0,behavior:'instant'});}renderNav();}
$('toggleFinished').addEventListener('click',()=>{if(state.finished.includes(current))state.finished=state.finished.filter(x=>x!==current);else state.finished=[...state.finished,current];try{localStorage.setItem(key,JSON.stringify(state));}catch(_){toast('当前浏览器无法保存学习记录');}show(current,false);});
$('chapterSearch').addEventListener('input',e=>{query=e.target.value.trim();renderNav();});
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('chapterSearch').focus();}});
$('copyWechatSide').addEventListener('click',copyWechat);$('copyWechatBottom').addEventListener('click',copyWechat);
window.addEventListener('popstate',()=>show(getChapterId(),false));
show(getChapterId(),false);
})();