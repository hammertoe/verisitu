"""Dependency-free checks: python3 -m unittest discover -s tests -v."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / 'index.html').read_text()
        self.doc = Document(self.html)

    def test_semantic_sections_and_one_heading(self):
        self.assertEqual(sum(t == 'h1' for t, _ in self.doc.tags), 1)
        ids = {a.get('id') for _, a in self.doc.tags}
        for section in ['main', 'problem', 'approach', 'applications', 'vision', 'contact']:
            self.assertIn(section, ids)
        self.assertIn('Making local economies', self.html)
        self.assertIn('visible to AI.', self.html)

    def test_navigation_and_product_links(self):
        ids = {a.get('id') for _, a in self.doc.tags}
        links = [a.get('href', '') for t, a in self.doc.tags if t == 'a']
        for href in links:
            if href.startswith('#'):
                self.assertIn(href[1:], ids)
        self.assertIn('https://pulsebarbados.com', links)
        self.assertIn('https://yuhgettintru.com', links)
        self.assertTrue(any(h.startswith('mailto:') for h in links))

    def test_metadata_and_local_assets(self):
        metas = {a.get('name', a.get('property')): a.get('content') for t, a in self.doc.tags if t == 'meta'}
        for key in ['description', 'viewport', 'og:title', 'og:image', 'twitter:card']:
            self.assertTrue(metas.get(key))
        for tag, attrs in self.doc.tags:
            asset = attrs.get('src') if tag in ['img', 'script'] else attrs.get('href') if tag == 'link' and attrs.get('rel') in ['stylesheet', 'icon'] else None
            if asset and not asset.startswith('http'):
                self.assertTrue((ROOT / asset).is_file(), asset)
            if tag == 'img':
                self.assertIn('alt', attrs)
                self.assertIn('width', attrs)
                self.assertIn('height', attrs)

    def test_static_accessible_and_honest(self):
        self.assertNotIn('<form', self.html)
        self.assertIn('infrastructure direction', self.html)
        css = (ROOT / 'styles.css').read_text()
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn(':focus-visible', css)
        self.assertIn('@media', css)
        self.assertNotIn('react', self.html.lower())

    def test_contact_is_a_plain_email_link(self):
        self.assertIn('<a href="mailto:hello@verisitu.com">hello@verisitu.com</a>', self.html)
        self.assertNotIn('class="email-link"', self.html)


if __name__ == '__main__':
    unittest.main()
