"""Source coverage and integration checks for the JSON reference importer."""
import html
import json
import unittest

import build
from reference import load_reference_pages


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = load_reference_pages(build.ROOT)
        cls.by_id = {page['id']: page for page in cls.pages}

    def test_every_entry_and_rule_is_preserved(self):
        self.assertEqual(len(self.pages), 172)
        for catalogue, singular in [('skills', 'skill'), ('spells', 'spell')]:
            data = json.loads((build.ROOT / 'Reference' / ('dcc_%s.json' % catalogue)).read_text(encoding='utf-8'))
            for entry in data[catalogue]:
                page = self.by_id[singular + '-' + entry['id']]
                visible = html.unescape(page['html'])
                self.assertEqual(page['title'], entry['name'])
                for key in ['flavor_text', 'tags_raw', 'stat', 'mana_cost', 'range',
                            'duration', 'cooldown', 'ai_favor', 'limitations',
                            'base_damage', 'description', 'upgrades_note', 'raw_text']:
                    for paragraph in (entry.get(key) or '').split('\n\n'):
                        self.assertIn(paragraph, visible, (entry['id'], key))
                for value in entry['upgrades'].values():
                    for paragraph in value.split('\n\n'):
                        self.assertIn(paragraph, visible)
                self.assertIn('href="#' + page['id'] + '"', self.by_id[catalogue]['html'])
            for rule in data['rules']:
                for paragraph in rule['text'].split('\n\n'):
                    self.assertIn(paragraph, html.unescape(self.by_id[catalogue + '-rules']['html']))

    def test_links_resolve_and_do_not_collide_with_campaign(self):
        all_pages = build.load_pages() + self.pages
        ids = [p['id'] for p in all_pages]
        self.assertEqual(len(ids), len(set(ids)))
        for page in self.pages:
            for match in build.WIKILINK.finditer(page['raw']):
                self.assertIn(match.group(1), ids)
        self.assertIn('[[skill-pugilism]]', self.by_id['skill-iron-punch']['raw'])

    def test_transcription_excludes_reference(self):
        excluded = build.CFG['names_exclude_types']
        for page in self.pages:
            self.assertIn(page['type'], excluded)

    def test_rank_dice_and_missing_values(self):
        self.assertIn('+2d10', self.by_id['skills-rules']['html'])
        self.assertNotIn('<dt>Range</dt>', self.by_id['skill-back-claw']['html'])
        self.assertNotIn('<dt>Listed stat</dt>', self.by_id['spell-air-buddy']['html'])


if __name__ == '__main__':
    unittest.main()
