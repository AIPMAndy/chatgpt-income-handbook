from pathlib import Path
import json, re, unittest, urllib.parse
ROOT=Path(__file__).resolve().parents[1]
J=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))

class HandbookTests(unittest.TestCase):
 def test_counts(self):
  self.assertEqual(len(J['chapters']),34)
  self.assertEqual(len(J['offers']),10)
  self.assertEqual(len(J['prompts']),64)
  self.assertEqual(len(J['faq']),36)
  self.assertEqual(len(J['days7']),7)
  self.assertEqual(len(J['weeks30']),4)
  self.assertEqual(len(J['sources']),13)
  self.assertEqual(len(J['scenarios']),4)
 def test_json_js_sync(self):
  s=(ROOT/'data/catalog.js').read_text(encoding='utf-8')
  self.assertTrue(s.startswith('window.CHATGPT_INCOME_DATA = '))
  j=json.loads(s[len('window.CHATGPT_INCOME_DATA = '):].rstrip(';\n'))
  self.assertEqual(J,j)
 def test_unique_ids(self):
  for cat in ['offers','chapters','prompts','faq','days7','weeks30']:
   ids=[x['id'] for x in J[cat]]
   self.assertEqual(len(ids),len(set(ids)),cat)
 def test_chapters_are_actionable(self):
  s=set(x['id'] for x in J['sources'])
  for x in J['chapters']:
   self.assertGreaterEqual(len(x['steps']),4)
   self.assertTrue(x['check'] and x['pitfall'] and x['source'] in s)
 def test_offers_have_auditable_contract(self):
  for x in J['offers']:
   for field in ['inputs','deliverable','risk','pricing']:
    self.assertGreaterEqual(len(x[field]),4)
   self.assertGreater(x['illustrativePrice'],0)
   self.assertGreaterEqual(x['illustrativeCost'],0)
 def test_prompt_structure(self):
  stages={x['stage'] for x in J['prompts']}
  self.assertEqual(stages,{'需求澄清','首版交付','红队质检','验收与复盘'})
  for x in J['prompts']:
   for word in ['经过授权','脱敏','【待核实】']:
    # Marking uncertain facts is explicit in initial-delivery prompt and all prompts prohibit fabricated facts.
    if word=='【待核实】' and x['stage']!='首版交付': continue
    self.assertIn(word,x['prompt'])
 def test_official_sources(self):
  for src in J['sources']:
   url=urllib.parse.urlparse(src['url'])
   self.assertEqual(url.scheme,'https')
   self.assertIn(url.hostname,['openai.com','help.openai.com','academy.openai.com'])
 def test_faq_source_refs(self):
  valid={s['id'] for s in J['sources']}
  for x in J['faq']:self.assertIn(x['source'],valid)
 def test_cases_not_claimed_verified(self):
  self.assertTrue(J['cases'])
  for x in J['cases']:
   self.assertEqual(x['type'],'作者自述')
   self.assertIn('未',x['evidence'])
   self.assertTrue(x['notClaim'])
 def test_site_dom_refs(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  ids=re.findall(r'\bid="([\w-]+)"',html)
  self.assertEqual(len(ids),len(set(ids)))
  js=(ROOT/'app.js').read_text(encoding='utf-8')
  refs=re.findall(r"\$\('#([A-Za-z][A-Za-z0-9-]*)'\)",js)
  self.assertTrue(set(refs)<=set(ids),sorted(set(refs)-set(ids)))
 def test_site_local_assets(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  for attr in ['src','href']:
   for v in re.findall(r'\b'+attr+r'="([^"]+)"',html):
    if v.startswith(('https://','mailto:','#')):continue
    self.assertTrue((ROOT/v.split('#')[0]).exists(),v)
 def test_safe_commercial_links(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  self.assertIn('AIPMAndy',html)
  self.assertIn('https://metaver.vip/',html)
  self.assertIn('https://metaver.vip/services',html)
 def test_contact_visible_in_hero_nav_modal_and_footer(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  js=(ROOT/'app.js').read_text(encoding='utf-8')
  css=(ROOT/'style.css').read_text(encoding='utf-8')
  readme=(ROOT/'README.md').read_text(encoding='utf-8')
  self.assertIn('class="nav-contact"',html)
  self.assertIn('class="hero-contact-strip"',html)
  self.assertIn('href="https://metaver.vip/"',html)
  self.assertIn('href="https://metaver.vip/services"',html)
  self.assertGreaterEqual(html.count('data-copy-wechat'),3)
  self.assertIn("copyText('AIPMAndy')",js)
  self.assertIn('官网 metaver.vip',js)
  self.assertIn('.topbar nav>a.nav-contact{display:inline-flex}',css)
  self.assertIn('微信：`AIPMAndy`',readme)
  self.assertIn('metaver.vip/services',readme)
 def test_audit_v22_interactive_and_claims(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  app=(ROOT/'app.js').read_text(encoding='utf-8')
  for ident in ['calcUnconvertedHours','calcLaborRate','calcAcquisitionSpend','calcAfterLabor','calcBreakeven','evidenceLevel','evidencePermission','evidenceArtifact','evidenceResult']:
   self.assertIn('id="'+ident+'"',html)
   self.assertIn(ident,app)
  self.assertIn('lib/economics.js',html)
  self.assertIn('ChatGPTIncomeEconomics',app)
  self.assertIn('docs/END-TO-END-TRIAL.md',html)
 def test_release_qa_current(self):
  txt=(ROOT/'docs/RELEASE-QA.md').read_text(encoding='utf-8')
  for term in ['34 章','64 套','36 个','45 个','未实际测试']:
   self.assertIn(term,txt)
  for stale in ['仓库尚未创建','Pages 尚未发布','26 章','48 套']:
   self.assertNotIn(stale,txt)
 def test_math_runs_before_pages(self):
  for name in ['.github/workflows/check.yml','.github/workflows/deploy-pages.yml']:
   txt=(ROOT/name).read_text(encoding='utf-8')
   self.assertIn('node tests/test_economics.cjs',txt)
   self.assertIn('node --check lib/economics.js',txt)
 def test_pages_quality_gate(self):
  y=(ROOT/'.github/workflows/deploy-pages.yml').read_text(encoding='utf-8')
  self.assertIn('needs: verify',y)
  self.assertIn('pages: write',y)
  self.assertIn('actions/deploy-pages@v4',y)
 def test_no_credential_leak(self):
  for p in ROOT.rglob('*'):
   if not p.is_file() or '__pycache__' in p.parts or '.git' in p.parts:continue
   if p.suffix not in ['.js','.json','.html','.md','.txt','.csv','.yml','.svg','.css','.xml',''] and p.name!='.nojekyll':continue
   txt=p.read_text(encoding='utf-8-sig')
   self.assertNotIn('-----BEGIN PRIVATE KEY-----',txt)
   self.assertNotRegex(txt,r'\bsk-[A-Za-z0-9]{30,}\b')
 def test_no_earnings_guarantee_in_metadata(self):
  self.assertIn('无收入',J['meta']['disclaimer'])
  self.assertIn('独立',J['meta']['disclaimer'])
 def test_docs_exist(self):
  for p in ['README.md','CONTRIBUTING.md','LICENSE','docs/COMPLETE-GUIDE.md','docs/PROMPT-LIBRARY.md','docs/ADVERSARIAL-AUDIT.md','docs/SOURCES.md','guides/7-DAY-PLAN.md','guides/30-DAY-PLAN.md','templates/CASE-STUDY.md','templates/QUOTE.md','templates/CLIENT-BRIEF.md']:
   self.assertTrue((ROOT/p).is_file(),p)
 def test_all_templates_same_four_stages(self):
  for name in {x['scenario'] for x in J['prompts']}:
   self.assertEqual(len([x for x in J['prompts'] if x['scenario']==name]),4,name)
 def test_calc_label_says_illustrative(self):
  h=(ROOT/'index.html').read_text(encoding='utf-8')
  self.assertIn('纯假设测算',h)
  self.assertIn('真实收入可能为 0 或负数',h)
 def test_source_index_references(self):
  content=(ROOT/'docs/SOURCES.md').read_text(encoding='utf-8')
  for src in J['sources']:self.assertIn(src['url'],content)
 def test_readme_disclaims_affiliation(self):
  txt=(ROOT/'README.md').read_text(encoding='utf-8')
  self.assertIn('非 OpenAI 官方',txt)
  self.assertIn('不承诺收益',txt)


 def test_deep_service_sops_all_have_acceptance_and_scope(self):
  fields=['scope','deliverable','acceptance','excluded','revisions','workflow','proof','changeControl','pricingNote']
  for o in J['offers']:
   for f in fields:
    self.assertIn(f,o)
    self.assertGreaterEqual(len(o[f]),8,(o['id'],f))
   self.assertIn('确认',o['changeControl'])
 def test_no_marketing_claim_on_simulated_cases(self):
  for x in J['scenarios']:
   self.assertTrue('演示' in x['kind'] or '模拟' in x['kind'])
   self.assertTrue(all(x.get(k) for k in ['input','process','output','qa','failure','evidence']))
  self.assertIn('模拟交付案例', (ROOT/'docs/DEMO-CASE-LAB.md').read_text(encoding='utf-8'))
 def test_v2_interactive_tools_exist(self):
  h=(ROOT/'index.html').read_text(encoding='utf-8')
  js=(ROOT/'app.js').read_text(encoding='utf-8')
  for id in ['proposalOffer','proposalProblem','proposalDeadline','makeProposal','copyProposal','proposalOutput','privacyType','privacyAllowed','privacyEnvironment','privacyResult','readinessResult','calcAcqHours','calcReworkHours','calcRefundRate','calcFeeRate']:
   self.assertIn('id="'+id+'"',h)
   self.assertIn(id,js)
  self.assertIn('textContent=proposalText',js) # user's raw text never injected into HTML
  self.assertIn("permit==='no'||env==='no'",js)
 def test_v2_cost_arithmetic_has_human_labor_and_refunds(self):
  js=(ROOT/'lib/economics.js').read_text(encoding='utf-8')
  for term in ['gross * (1 - refundRate)','orders * (hours + acqHours + reworkHours) + unconvertedHours','gross * feeRate','margin - Math.max(0, margin) * reserveRate','totalHours * laborRate']:
   self.assertIn(term,js)
  self.assertIn('未成交线索',(ROOT/'index.html').read_text(encoding='utf-8'))
 def test_sop_and_new_templates_in_repository(self):
  for x in ['docs/SERVICE-SOPS.md','docs/PRIVACY-SOP.md','docs/CLAIM-LEDGER.md','docs/QUALITY-METHOD.md','docs/DEMO-CASE-LAB.md','templates/ACCEPTANCE-REPORT.md','templates/CHANGE-REQUEST.md','templates/PRIVACY-CONSENT.md','templates/FAILURE-RETRO.md','templates/AI-DISCLOSURE.md']:
   self.assertGreater((ROOT/x).stat().st_size,120,x)
 def test_v2_all_prompts_have_nonfabrication_guard(self):
  for x in J['prompts']:
   self.assertTrue('未经授权' in x['prompt'] or '经过授权' in x['prompt'] or '获授权' in x['prompt'])
   self.assertTrue(any(t in x['prompt'] for t in ['不可编造','不要编造','不得编造','不能编造','禁止编造','不可补写']))
 def test_v2_high_risk_sources_tracked(self):
  text=(ROOT/'docs/CLAIM-LEDGER.md').read_text(encoding='utf-8')
  for term in ['分开计费','个人聊天','Business','共享','模拟','作者自行']:
   self.assertIn(term,text)
 def test_website_does_not_send_private_form_contents(self):
  js=(ROOT/'app.js').read_text(encoding='utf-8')
  self.assertNotIn('fetch(',js)
  self.assertNotIn('XMLHttpRequest',js)
  self.assertNotIn('sendBeacon',js)
  self.assertNotIn('localStorage.setItem(K,proposalText)',js)

if __name__=='__main__':unittest.main()
