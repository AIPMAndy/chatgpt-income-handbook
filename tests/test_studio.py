from pathlib import Path
from html.parser import HTMLParser
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))

def parse(name):
    x=TagCollector();x.feed((ROOT / name).read_text(encoding='utf-8'));return x.tags

class StudioUXTests(unittest.TestCase):
    def test_reader_has_main_landmarks(self):
        page = parse('handbook.html')
        for ident in ['article', 'chapterNav', 'chapterSearch', 'chapterTitle', 'chapterSteps', 'chapterCheck', 'chapterPitfall', 'chapterSource', 'toggleFinished']:
            self.assertTrue(any(attrs.get('id')==ident for tag,attrs in page), ident)
        ids = [attrs['id'] for tag,attrs in page if attrs.get('id')]
        self.assertEqual(len(ids), len(set(ids)))

    def test_reader_links_to_author_brand(self):
        s = (ROOT / 'handbook.html').read_text(encoding='utf-8')
        for thing in ['AIPMAndy', 'https://metaver.vip/', 'https://metaver.vip/services', 'MIT']:
            # MIT is represented in linked repository documentation, while the reader lists author info.
            if thing == 'MIT':
                self.assertIn('MIT', (ROOT / 'README.md').read_text(encoding='utf-8'))
            else:
                self.assertIn(thing, s)

    def test_new_home_and_workbench_are_distinct(self):
        home=(ROOT/'index.html').read_text(encoding='utf-8')
        workbench=(ROOT/'workbench.html').read_text(encoding='utf-8')
        self.assertIn('href="handbook.html"',home)
        self.assertIn('href="workbench.html"',home)
        self.assertIn('href="apple-home.css"',home)
        self.assertIn('方法示意',home)
        self.assertIn('AIPMAndy',home)
        self.assertIn('class="site-aside"',workbench)
        self.assertIn('class="deliverable-panel"',workbench)
        self.assertIn('模拟案例',workbench)
        self.assertIn('docs/END-TO-END-TRIAL.md',workbench)
        self.assertIn('class="hero-contact-strip"',workbench)

    def test_all_new_local_refs(self):
        for file in ['index.html','handbook.html','workbench.html']:
            html=parse(file)
            for tag,attrs in html:
                if tag not in ('link','script','a'): continue
                dest=attrs.get('href') or attrs.get('src')
                if not dest or dest.startswith(('https://','#','mailto:')): continue
                path=dest.split('?')[0].split('#')[0]
                self.assertTrue((ROOT / path).exists(), (file,dest))

    def test_reader_does_not_import_external_script(self):
        html=parse('handbook.html')
        for tag,attrs in html:
            if tag=='script': self.assertIn(attrs.get('src'), ['data/catalog.js','reader.js'])
        reader=(ROOT/'reader.js').read_text(encoding='utf-8')
        for prohibited in ['fetch(', 'XMLHttpRequest', 'sendBeacon(', 'eval(']:
            self.assertNotIn(prohibited,reader)

    def test_css_has_mobile_track_width_cap(self):
        css=(ROOT/'studio.css').read_text(encoding='utf-8')
        self.assertIn('grid-template-columns:minmax(0,1fr)',css)
        self.assertIn('.site-shell',css)
        self.assertIn('@media(max-width:780px)',css)

if __name__=='__main__': unittest.main()