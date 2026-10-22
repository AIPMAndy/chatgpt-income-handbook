(() => {
'use strict';
const D=window.CHATGPT_INCOME_DATA;
if(!D || !Array.isArray(D.offers))return;
const $=(s)=>document.querySelector(s);
const escapeHtml=(s)=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const K='chatgpt-income-handbook-v1';
let saved={finished:[],favorite:[],day:[]};
try{const a=JSON.parse(localStorage.getItem(K)||'{}');for(const k of Object.keys(saved))if(Array.isArray(a?.[k]))saved[k]=a[k].filter(s=>typeof s==='string');}catch(_){/* storage could be unavailable */}
const store=()=>{try{localStorage.setItem(K,JSON.stringify(saved));}catch(_){}};
const has=(k,id)=>saved[k].includes(id);
const toggle=(k,id)=>{saved[k]=has(k,id)?saved[k].filter(x=>x!==id):[...saved[k],id];store();};
function toast(msg){let x=$('#toast');x.textContent=msg;x.hidden=false;clearTimeout(toast.t);toast.t=setTimeout(()=>x.hidden=true,2100);}
async function copyText(s){try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(s);toast('已复制到剪贴板');return;}}catch(_){}window.prompt('请复制内容：',s);}
$('#countLessons').textContent=D.chapters.length;$('#countOffers').textContent=D.offers.length;$('#countPrompts').textContent=D.prompts.length;$('#countFaq').textContent=D.faq.length;
// Deterministic self-assessment, not an earnings prediction.
const routeMap={content:['内容诊断与改写','短视频选题与口播包'],career:['简历与面试材料优化'],business:['企业客户FAQ与话术包','销售提案与方案制作'],data:['Excel经营数据周报','AI知识库与SOP搭建']};
function renderFinder(){const skill=$('#finderSkill').value,exp=$('#finderExperience').value,time=$('#finderTime').value;
 const options=routeMap[skill]||routeMap.content;const matched=D.offers.find(o=>o.name===options[(time==='long'&&exp==='yes'&&options.length>1)?1:0]);
 const stage=exp==='new'?'先做公开标明的演示样品，再访谈5个潜在客户。':'从已有客户的重复问题开始，优先做一份限定范围的试单。';
 const timeTip=time==='short'?'每周3—5小时，尽量只接一次性、小范围交付。':time==='medium'?'每周6—12小时，预留至少三分之一时间用于人工复核。':'每周12小时以上，先验证需求再做标准化，不建议上来就买复杂自动化工具。';
 $('#finderResult').innerHTML=`<strong>优先验证：${escapeHtml(matched.name)}</strong><p>${escapeHtml(stage)} ${escapeHtml(timeTip)} <a href="#paths" style="text-decoration:underline;color:#dcf1b4">在下方查看交付清单 →</a></p>`;
}
['#finderSkill','#finderTime','#finderExperience'].forEach(id=>$(id).addEventListener('change',renderFinder));renderFinder();
// Offers
let offerCat='全部';const offerCats=['全部',...new Set(D.offers.map(o=>o.category))];
$('#offerFilters').innerHTML=offerCats.map(c=>`<button class="chip ${c==='全部'?'active':''}" type="button" data-offer-cat="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join('');
function renderOffers(){const list=D.offers.filter(o=>offerCat==='全部'||o.category===offerCat);
 $('#offerCount').textContent=`显示 ${list.length} / ${D.offers.length} 种服务包`;
 $('#offerGrid').innerHTML=list.map(o=>`<article class="offer-card"><div class="offer-top"><span class="tag">${escapeHtml(o.category)} · ${escapeHtml(o.level)}</span><span class="offer-num">${escapeHtml(o.id.toUpperCase())}</span></div><h3>${escapeHtml(o.name)}</h3><p>${escapeHtml(o.what)}</p><div class="offer-list"><p><b>客户提供：</b>${escapeHtml(o.inputs)}</p><p><b>验收交付：</b>${escapeHtml(o.deliverable)}</p><p><b>风险提醒：</b>${escapeHtml(o.risk)}</p></div><div class="offer-hypo"><span>演示报价参数 <strong>¥${o.illustrativePrice}</strong></span><span>直接成本假设 ¥${o.illustrativeCost}</span><button type="button" data-use-price="${o.id}">代入测算 ↗</button></div></article>`).join('');
 $('#offerFilters').querySelectorAll('[data-offer-cat]').forEach(x=>x.classList.toggle('active',x.dataset.offerCat===offerCat));}
// Chapters
let lessonSearch='',lessonCat='全部',lessonUndone=false;
const lessonCats=['全部',...new Set(D.chapters.map(x=>x.category))];$('#lessonCategory').innerHTML=lessonCats.map(x=>`<option value="${escapeHtml(x)}">${escapeHtml(x)}</option>`).join('');
function renderLessons(){const list=D.chapters.filter(x=>(lessonCat==='全部'||lessonCat===x.category)&&(!lessonUndone||!has('finished',x.id))&&[x.title,x.summary,x.category,x.pitfall,...x.steps].join(' ').toLowerCase().includes(lessonSearch.toLowerCase()));
 $('#lessonCount').textContent=`显示 ${list.length} / ${D.chapters.length} 章`;
 const count=D.chapters.filter(x=>has('finished',x.id)).length;$('#progressCount').textContent=`已完成 ${count} / ${D.chapters.length}`;$('#progressBar').style.width=(100*count/D.chapters.length)+'%';
 $('#lessonGrid').innerHTML=list.length?list.map(c=>`<article class="lesson-card ${has('finished',c.id)?'complete':''}"><div class="lesson-card-top"><span>${escapeHtml(c.category)}</span><span>CH ${String(c.number).padStart(2,'0')} · ${c.minutes} MIN</span></div><h3>${escapeHtml(c.title)}</h3><p>${escapeHtml(c.summary)}</p><div class="lesson-bottom"><button type="button" data-open-lesson="${c.id}">查看步骤和验收 →</button><label><input type="checkbox" data-finished="${c.id}" ${has('finished',c.id)?'checked':''} aria-label="标记${escapeHtml(c.title)}完成"> 已完成</label></div></article>`).join(''):'<p>没有找到对应章节，试试其他关键词。</p>';}
function openLesson(id){const c=D.chapters.find(x=>x.id===id);if(!c)return;const source=D.sources.find(x=>x.id===c.source);$('#dialogBody').innerHTML=`<div class="modal-eyebrow">CH ${String(c.number).padStart(2,'0')} / ${escapeHtml(c.category)} / ${c.minutes} 分钟</div><h2 id="dialogTitle">${escapeHtml(c.title)}</h2><p>${escapeHtml(c.summary)}</p><div class="modal-block"><h3>跟着做 · 四步</h3><ol>${c.steps.map(s=>`<li>${escapeHtml(s)}</li>`).join('')}</ol></div><div class="modal-block"><h3>怎样算完成？</h3><p>${escapeHtml(c.check)}</p></div><div class="modal-block"><h3>最大的坑</h3><p>${escapeHtml(c.pitfall)}</p></div><div class="modal-foot"><button type="button" class="btn btn-dark" data-modal-finished="${c.id}">${has('finished',c.id)?'✓ 已完成':'✓ 标记已完成'}</button><a href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">查看官方相关说明 ↗</a></div><div class="modal-contact">自己的项目需要指导？微信 <b>AIPMAndy</b> <button type="button" data-copy-wechat>复制微信号</button> · <a href="https://metaver.vip/services" target="_blank" rel="noopener noreferrer">了解咨询服务 ↗</a></div>`;const d=$('#lessonDialog');if(!d.open)d.showModal();$('#closeDialog').focus();}
// Prompt library
let promptCat='全部',promptQuery='',onlyFavorite=false;const cats=['全部',...new Set(D.prompts.map(x=>x.category))];$('#promptFilters').innerHTML=cats.map(x=>`<button type="button" class="chip ${x==='全部'?'active':''}" data-prompt-cat="${escapeHtml(x)}">${escapeHtml(x)}</button>`).join('');
function renderPrompts(){const arr=D.prompts.filter(p=>(promptCat==='全部'||p.category===promptCat)&&(!onlyFavorite||has('favorite',p.id))&&[p.title,p.prompt,p.scenario,p.stage].join(' ').toLowerCase().includes(promptQuery.toLowerCase()));$('#promptCount').textContent=`显示 ${arr.length} / ${D.prompts.length} 套工作指令`;
 $('#promptGrid').innerHTML=arr.length?arr.map(p=>`<article class="prompt-card"><div class="prompt-card-head"><span>${escapeHtml(p.category)} / ${escapeHtml(p.stage)}</span><button type="button" class="favorite-btn ${has('favorite',p.id)?'active':''}" data-favorite="${p.id}" aria-pressed="${has('favorite',p.id)}" title="收藏${escapeHtml(p.title)}">${has('favorite',p.id)?'♥':'♡'}</button></div><h3>${escapeHtml(p.title)}</h3><p>交付：${escapeHtml(p.deliverable)}</p><div class="prompt-preview">${escapeHtml(p.prompt.slice(0,120))}…</div><div class="prompt-actions"><button type="button" data-copy-prompt="${p.id}">复制完整提示词 ↗</button><button type="button" data-expand-prompt="${p.id}">查看全文 +</button></div><details id="prompt-${p.id}"><summary>完整提示词与使用边界</summary><pre>${escapeHtml(p.prompt)}</pre></details></article>`).join(''):'<p>没有匹配的提示词。</p>';
 $('#promptFilters').querySelectorAll('[data-prompt-cat]').forEach(b=>b.classList.toggle('active',b.dataset.promptCat===promptCat));}
// Unit economics: illustrative math only; no earnings forecasts.
const calcIds=['calcPrice','calcOrders','calcCost','calcHours','calcFixed','calcReserve'];
const money=(n)=>Number.isFinite(n)?'¥'+n.toLocaleString('zh-CN',{maximumFractionDigits:2,minimumFractionDigits:0}):'—';
const num=id=>{let n=Number($('#'+id).value);return Number.isFinite(n)?Math.max(0,n):0;};
function calculate(){const price=num('calcPrice'),orders=Math.min(100000,Math.floor(num('calcOrders'))),direct=num('calcCost'),hours=num('calcHours'),fixed=num('calcFixed'),reserve=Math.min(100,num('calcReserve'))/100;
 const revenue=price*orders,margin=revenue-(direct*orders)-fixed,net=margin-Math.max(0,margin)*reserve,totalHours=hours*orders;
 $('#calcRevenue').textContent=money(revenue);$('#calcMargin').textContent=money(margin);$('#calcNet').textContent=money(net);$('#calcTotalHours').textContent=totalHours.toLocaleString('zh-CN',{maximumFractionDigits:2})+' h';$('#calcHourly').textContent=totalHours>0?money(net/totalHours):'—';
 return {price,orders,direct,hours,fixed,reserve:reserve*100,revenue,margin,net,totalHours};}
calcIds.forEach(x=>$('#'+x).addEventListener('input',calculate));calculate();
// Activity plan & case references
function renderPlan(){$('#daysGrid').innerHTML=D.days7.map(x=>`<article class="day-card ${has('day',x.id)?'checked':''}"><div class="day-label">${escapeHtml(x.day)}</div><h3>${escapeHtml(x.title)}</h3><p>${escapeHtml(x.deliverable)}</p><label class="day-check"><input type="checkbox" data-day="${x.id}" ${has('day',x.id)?'checked':''}> 我实际完成了</label></article>`).join('');
 $('#weeksGrid').innerHTML=D.weeks30.map(x=>`<article class="week-card"><span>${escapeHtml(x.week)}</span><strong>${escapeHtml(x.title)}</strong><p>${escapeHtml(x.deliverable)}</p></article>`).join('');}
$('#casesGrid').innerHTML=D.cases.map(c=>`<article class="case-card"><span class="tag risk">${escapeHtml(c.type)} · 未独立核验</span><h3>${escapeHtml(c.title)}</h3><p>${escapeHtml(c.description)}</p><dl><dt>证据等级</dt><dd>${escapeHtml(c.evidence)}</dd><dt>可以学习</dt><dd>${escapeHtml(c.usable)}</dd><dt>不能声称</dt><dd>${escapeHtml(c.notClaim)}</dd></dl></article>`).join('');
let faqQuery='';function renderFaq(){const arr=D.faq.filter(x=>(x.question+x.answer).toLowerCase().includes(faqQuery.toLowerCase()));$('#faqList').innerHTML=arr.map(x=>{const s=D.sources.find(a=>a.id===x.source);return `<details class="faq-item"><summary>${escapeHtml(x.question)}</summary><p>${escapeHtml(x.answer)}</p><a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer">核对官方依据 ↗</a></details>`;}).join('')||'<p>没有找到匹配的问题。</p>';}
$('#sourcesGrid').innerHTML=D.sources.map(x=>`<a class="source-card" href="${escapeHtml(x.url)}" target="_blank" rel="noopener noreferrer"><span>↗</span><strong>${escapeHtml(x.name)}</strong><p>${escapeHtml(x.scope)}</p></a>`).join('');
// Event delegation
 document.addEventListener('click',e=>{const t=e.target.closest('[data-offer-cat],[data-prompt-cat],[data-open-lesson],[data-favorite],[data-copy-prompt],[data-expand-prompt],[data-copy-wechat],[data-use-price],[data-modal-finished]');if(!t)return;
 if(t.hasAttribute('data-offer-cat')){offerCat=t.dataset.offerCat;renderOffers();return;}
 if(t.hasAttribute('data-prompt-cat')){promptCat=t.dataset.promptCat;renderPrompts();return;}
 if(t.hasAttribute('data-open-lesson')){openLesson(t.dataset.openLesson);return;}
 if(t.hasAttribute('data-favorite')){toggle('favorite',t.dataset.favorite);renderPrompts();return;}
 if(t.hasAttribute('data-copy-prompt')){let p=D.prompts.find(x=>x.id===t.dataset.copyPrompt);if(p)copyText(p.prompt);return;}
 if(t.hasAttribute('data-expand-prompt')){const d=document.getElementById('prompt-'+t.dataset.expandPrompt);if(d)d.open=!d.open;return;}
 if(t.hasAttribute('data-copy-wechat')){copyText('AIPMAndy');return;}
 if(t.hasAttribute('data-use-price')){let x=D.offers.find(o=>o.id===t.dataset.usePrice);if(x){$('#calcPrice').value=x.illustrativePrice;$('#calcCost').value=x.illustrativeCost;$('#calcOrders').value=1;calculate();document.querySelector('#calculator').scrollIntoView({behavior:'smooth'});toast('已代入假设价格和直接成本');}return;}
 if(t.hasAttribute('data-modal-finished')){if(!has('finished',t.dataset.modalFinished))toggle('finished',t.dataset.modalFinished);renderLessons();openLesson(t.dataset.modalFinished);toast('已标记完成');}
 });
 document.addEventListener('change',e=>{const t=e.target;if(t.hasAttribute('data-finished')){toggle('finished',t.dataset.finished);renderLessons();}if(t.hasAttribute('data-day')){toggle('day',t.dataset.day);renderPlan();}});
 $('#lessonSearch').addEventListener('input',e=>{lessonSearch=e.target.value.trim();renderLessons();});$('#lessonCategory').addEventListener('change',e=>{lessonCat=e.target.value;renderLessons();});$('#lessonUndone').addEventListener('change',e=>{lessonUndone=e.target.checked;renderLessons();});
 $('#promptSearch').addEventListener('input',e=>{promptQuery=e.target.value.trim();renderPrompts();});$('#onlyFavorite').addEventListener('change',e=>{onlyFavorite=e.target.checked;renderPrompts();});$('#clearPrompts').addEventListener('click',()=>{promptQuery='';promptCat='全部';onlyFavorite=false;$('#promptSearch').value='';$('#onlyFavorite').checked=false;renderPrompts();});
 $('#faqSearch').addEventListener('input',e=>{faqQuery=e.target.value.trim();renderFaq();});
 $('#copyCalc').addEventListener('click',()=>{let x=calculate();copyText(`ChatGPT服务报价情景（纯假设，非收益预测）\n报价：${x.price}元；假设单数：${x.orders}；每单直接成本：${x.direct}元；每单工时：${x.hours}小时；固定费用：${x.fixed}元；税费及其他预留：${x.reserve}%\n假设总收入：${x.revenue}元；扣除部分成本：${x.margin}元；预留后估算结余：${x.net}元；总交付时长：${x.totalHours}小时。\n未包括真实获客成本、退款、税务计算及成交不确定性。`);});
 $('#exportProgress').addEventListener('click',()=>{let finished=D.chapters.filter(x=>has('finished',x.id)).map(x=>'- '+x.title),days=D.days7.filter(x=>has('day',x.id)).map(x=>'- '+x.day+' '+x.title),fav=D.prompts.filter(x=>has('favorite',x.id)).map(x=>'- '+x.title);let content=['# ChatGPT 赚钱攻略学习记录','导出日期：'+new Date().toLocaleDateString('zh-CN'),'','## 已完成章节',...(finished.length?finished:['（无）']),'','## 已完成练习',...(days.length?days:['（无）']),'','## 收藏的提示词',...(fav.length?fav:['（无）']),'','提醒：学习记录不代表收入。'].join('\n');const u=URL.createObjectURL(new Blob([content],{type:'text/markdown;charset=utf-8'}));let a=document.createElement('a');a.href=u;a.download='ChatGPT-第一单练习记录.md';a.click();setTimeout(()=>URL.revokeObjectURL(u),2000);});
 $('#closeDialog').addEventListener('click',()=>$('#lessonDialog').close());$('#lessonDialog').addEventListener('click',e=>{if(e.target===$('#lessonDialog'))$('#lessonDialog').close();});
 renderOffers();renderLessons();renderPrompts();renderPlan();renderFaq();
})();
