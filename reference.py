"""Build rulebook reference pages directly from the supplied JSON (stdlib only)."""
import html
import json
import re


def esc(value):
    return html.escape(str(value), quote=True)


def paragraphs(text):
    return ''.join('<p>%s</p>' % esc(p) for p in (text or '').split('\n\n') if p)


def source_label(source):
    def span(key):
        values = source.get(key, [])
        return '–'.join(map(str, dict.fromkeys(values))) or 'not listed'
    return 'Printed pages %s · PDF pages %s' % (span('printed_pages'), span('pdf_pages'))


def load_reference_pages(root):
    pages = []
    for catalogue, singular in [('skills', 'skill'), ('spells', 'spell')]:
        path = root / 'Reference' / ('dcc_%s.json' % catalogue)
        if not path.exists():
            raise ValueError('Missing reference file: %s' % path)
        data = json.loads(path.read_text(encoding='utf-8'))
        entries = data[catalogue]
        expected = data['counts'][catalogue + '_total']
        if len(entries) != expected:
            raise ValueError('%s: expected %s entries, found %s' % (path, expected, len(entries)))
        ids = [e['id'] for e in entries]
        if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[a-z0-9-]+', i) for i in ids):
            raise ValueError('%s: duplicate or invalid entry IDs' % path)
        def pid(entry):
            return singular + '-' + entry['id']
        def category(entry):
            if singular == 'spell':
                return (entry.get('spell_mode') or 'other').title()
            return entry.get('subsection') or 'Utility Skills'
        def base(id_, title, type_, raw='', **extra):
            return dict(id=id_, title=title, type=type_, group=catalogue.title(),
                        aliases=[], raw=raw, reference=True, **extra)

        rules_id = catalogue + '-rules'
        rule_html = '<p><a class="wl" href="#%s">← Browse %s</a></p>' % (catalogue, catalogue)
        for rule in data['rules']:
            rule_html += '<h2>%s</h2>%s<p class="source">%s</p>' % (
                esc(rule['heading']), paragraphs(rule['text']), esc(source_label(rule['source'])))
        if data.get('rank_damage_dice'):
            rule_html += '<h2>Rank damage dice</h2><p>Use when an entry calls for Rank damage dice.</p><table class="reference-table"><thead><tr><th>Rank</th><th>Damage dice</th></tr></thead><tbody>'
            for row in data['rank_damage_dice']:
                ranks = str(row['rank_min']) if row['rank_min'] == row['rank_max'] else '%s–%s' % (row['rank_min'], row['rank_max'])
                rule_html += '<tr><td>%s</td><td>%s</td></tr>' % (ranks, esc(row['damage_dice']))
            rule_html += '</tbody></table>'
        pages.append(base(rules_id, catalogue.title() + ' — Rules', 'rule',
                          '[[%s]]' % catalogue, html=rule_html, order='1',
                          dek='General rules from the Royal Court Edition.',
                          search_extra=' '.join(r['text'] for r in data['rules'])))

        cards = []
        for entry in sorted(entries, key=lambda e: e['name']):
            facts = []
            for key, label in [('stat', 'Listed stat'), ('attack_mode', 'Attack mode'),
                               ('spell_mode', 'Spell mode'), ('mana_cost', 'Mana cost'),
                               ('range', 'Range'), ('duration', 'Duration'), ('cooldown', 'Cooldown'),
                               ('base_damage', 'Base damage'), ('ai_favor', 'AI Favor'),
                               ('damage_types', 'Damage / effect types'), ('favored_classes', 'Favored classes')]:
                value = entry.get(key)
                if value:
                    value = ', '.join(value) if isinstance(value, list) else value
                    facts.append('<div><dt>%s</dt><dd>%s</dd></div>' % (label, esc(value)))
            flags = [label for key, label in [('passive', 'Passive'), ('interrupt', 'Interrupt'), ('area_of_effect', 'Area of Effect')] if entry.get(key)]
            body = '<p><a class="wl" href="#%s">← All %s</a> · <a class="wl" href="#%s">General rules</a></p>' % (catalogue, catalogue, rules_id)
            if entry.get('flavor_text'):
                body += '<p><em>%s</em></p>' % esc(entry['flavor_text'])
            if entry.get('tags_raw'):
                body += '<p class="source">%s</p>' % esc(entry['tags_raw'])
            body += '<dl class="reference-facts">%s</dl>' % ''.join(facts)
            if entry.get('limitations'):
                body += '<div class="panel warn"><div class="ph">Limitations</div>%s</div>' % paragraphs(entry['limitations'])
            body += '<h2>Effect</h2>' + (paragraphs(entry.get('description')) or '<p>Use the base damage and listed properties above; no additional description is supplied.</p>')
            related = [e for e in entries if e != entry and e['name'] in (entry.get('damage_effect_for') or '')]
            if entry.get('damage_effect_for'):
                body += '<p><strong>Damage effect for:</strong> %s</p>' % esc(entry['damage_effect_for'])
            if related:
                body += '<p>' + ' · '.join('<a class="wl" href="#%s">%s</a>' % (pid(e), esc(e['name'])) for e in related) + '</p>'
            body += '<h2>Rank upgrades</h2><div class="rank-upgrades">'
            for rank, effect in sorted(entry.get('upgrades', {}).items(), key=lambda pair: int(pair[0])):
                body += '<section class="panel"><h3>Rank %s</h3>%s</section>' % (esc(rank), paragraphs(effect))
            body += '</div>'
            if entry.get('upgrades_note'):
                body += paragraphs(entry['upgrades_note'])
            body += '<h2>Source</h2><p class="source">%s · %s</p>' % (esc(data['source']['book']), esc(source_label(entry['source'])))
            body += '<details><summary>Original extracted text</summary><pre class="raw-reference">%s</pre></details>' % esc(entry.get('raw_text') or '')
            search = ' '.join(str(v) for k, v in entry.items() if v is not None and k not in ('raw_text', 'source')).lower()
            pages.append(base(pid(entry), entry['name'], singular,
                              ' '.join('[[%s]]' % i for i in [catalogue, rules_id] + [pid(e) for e in related]),
                              html=body, dek=category(entry), reference_entry=True, search_extra=search))
            quick = [('Stat', entry.get('stat')), ('Mana', entry.get('mana_cost')),
                     ('Range', entry.get('range')), ('Damage', entry.get('base_damage'))]
            details = ' · '.join('%s: %s' % (label, esc(value)) for label, value in quick if value)
            cards.append('<article class="reference-card" data-search="%s" data-category="%s" data-stat="%s" data-traits="%s"><h2><a class="wl" href="#%s">%s</a></h2><p class="source">%s</p><p>%s</p>%s</article>' % (
                esc(search), esc(category(entry)), esc(entry.get('stat') or ''), esc('|'.join(flags)), pid(entry), esc(entry['name']),
                esc(category(entry)), details or 'See entry for effects and requirements.',
                '<p class="source">%s</p>' % esc(' · '.join(flags)) if flags else ''))
        def select(name, label, values):
            return '<label>%s<select data-filter="%s"><option value="">All</option>%s</select></label>' % (
                label, name, ''.join('<option value="%s">%s</option>' % (esc(v), esc(v)) for v in sorted(set(values)) if v))
        controls = '<div class="reference-controls"><label>Search %s<input type="search" data-filter="search" placeholder="Name, effect, class, damage…"></label>' % catalogue
        controls += select('category', 'Category', [category(e) for e in entries])
        controls += select('stat', 'Listed stat', [e.get('stat') for e in entries if e.get('stat')])
        controls += select('traits', 'Trait', ['Passive', 'Interrupt', 'Area of Effect'])
        controls += '<button type="button" data-reset-reference>Clear filters</button></div>'
        introduction = '<p><a class="wl" href="#%s">Read the %s rules →</a></p><p>Browse by category, listed stat, or trait. Search includes effects, upgrades, damage types, and favored classes. Open an entry for full rules and sources.</p>' % (rules_id, catalogue)
        introduction += '<p class="source">Fields absent from the source are omitted; consult the general rules for defaults. The supplied extraction is preserved, including any extraction errors.</p>'
        index_html = introduction + controls + '<p data-reference-count role="status">%s entries</p><div class="reference-grid">%s</div><p data-reference-empty hidden>No entries match. Try clearing a filter.</p>' % (len(entries), ''.join(cards))
        pages.append(base(catalogue, catalogue.title(), 'reference',
                          ' '.join('[[%s]]' % i for i in [rules_id] + [pid(e) for e in entries]),
                          html=index_html, order='0', dek='%s entries · Royal Court Edition' % len(entries)))
    return pages
