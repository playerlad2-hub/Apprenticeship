"""Fast offline release checks. No credentials or network needed."""
import pathlib,sys,subprocess,tempfile,json,unittest,re
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import generate_pages as g
from discovery_feeds import board
from vacancy_search import canonical
class Checks(unittest.TestCase):
 def test_urls(self):
  self.assertEqual(board('https://jobs.smartrecruiters.com/Example/123','Example')['slug'],'Example')
  self.assertIsNone(board('https://jobs.smartrecruiters.com.evil.test/Example/123','Example'))
  self.assertIsNone(board('https://evil.test/Example/123','Example'))
  self.assertEqual(canonical('https://example.com/x?utm_source=y&id=1'),'https://example.com/x?id=1')
 def test_static(self):
  with tempfile.TemporaryDirectory() as d:
   prior=g.SITE;g.SITE=pathlib.Path(d)
   try:
    g.generate([dict(id='a',title='Software & Data',company='Example',live=True,description='<script>alert(1)</script>',url='https://example.com/a'),dict(id='b',title='Closed example',company='Example',vacancyStatus='closed',live=False,url='https://example.com/b')]);text=(g.SITE/'vacancies'/ (g.key('a')+'.html')).read_text();self.assertIn('&lt;script&gt;',text);self.assertNotIn('<script>alert',text);self.assertNotIn(g.key('b'),(g.SITE/'sitemap.xml').read_text());self.assertTrue((g.SITE/'employers'/(g.key('Example')+'.html')).exists())
   finally:g.SITE=prior
 def test_js(self):
  for p in (ROOT/'site').glob('*.js'):subprocess.run(['node','--check',str(p)],check=True,capture_output=True)
  src=(ROOT/'site/index.html').read_text();
  with tempfile.TemporaryDirectory() as d:
   for i,s in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',src,re.S)):
    if s.strip():
     p=pathlib.Path(d)/f'{i}.js';p.write_text(s);subprocess.run(['node','--check',str(p)],check=True,capture_output=True)
if __name__=='__main__':unittest.main()
