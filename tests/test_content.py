from pathlib import Path
import json, re, unittest, urllib.parse
ROOT=Path(__file__).resolve().parents[1]
J=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))

class HandbookTests(unittest.TestCase):
 def test_counts(self):
  self.assertEqual(len(J['chapters']),26)
  self.assertEqual(len(J['offers']),10)
  self.assertEqual(len(J['prompts']),48)
  self.assertEqual(len(J['faq']),24)
  self.assertEqual(len(J['days7']),7)
  self.assertEqual(len(J['weeks30']),4)
  self.assertEqual(len(J['sources']),10)
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

if __name__=='__main__':unittest.main()
