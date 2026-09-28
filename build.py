#!/usr/bin/env python3
"""
Build the campaign wiki.

Reads  content/*.md   (Obsidian-style vault: YAML-ish frontmatter + [[wikilinks]])
Writes docs/index.html (one self-contained page, no runtime dependencies)

Standard library only. Run it with:  python3 build.py
"""

import html
import json
import pathlib
import re
import sys
from datetime import date

ROOT = pathlib.Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"

CONF_LABEL = {"hi": "Confirmed", "mid": "Needs review", "lo": "Low confidence"}

# Everything campaign-specific lives in config.json, so one generator serves
# every campaign. A repo with no config.json keeps the original behaviour.
DEFAULTS = {
    "title": "Campaign Archive",
    "subtitle": "",
    "groups": ["Session V", "Player Characters", "Crew & Allies",
               "Adversaries", "Places", "Things", "Factions"],
    "type_labels": {"character": "Character", "place": "Place",
                    "thing": "Item", "faction": "Faction", "doc": "Session"},
    "axis": None,
    "status_labels": {},
    "status_tone": {},
}

def load_config():
    cfg = dict(DEFAULTS)
    path = ROOT / "config.json"
    if path.exists():
        cfg.update(json.loads(path.read_text(encoding="utf-8")))
    return cfg

CFG = load_config()
TYPE_LABEL = CFG["type_labels"]
GROUP_ORDER = CFG["groups"]
AXIS = CFG.get("axis")

WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


# ---------------------------------------------------------------- parsing

def parse_frontmatter(text):
    """Minimal frontmatter reader: `key: value`, with JSON arrays for lists."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4:]
    meta = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if val.startswith("["):
            try:
                val = json.loads(val)
            except ValueError:
                val = []
        elif len(val) > 1 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        meta[key.strip()] = val
    return meta, body.lstrip("\n")


def load_pages():
    pages = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not meta.get("title"):
            sys.exit("%s is missing a title in its frontmatter" % path.name)
        meta["id"] = path.stem
        meta["raw"] = body
        aliases = meta.get("aliases") or []
        meta["aliases"] = [a for a in aliases if isinstance(a, str)]
        pages.append(meta)
    return pages


# ---------------------------------------------------------------- inline markdown

def inline(text, resolve, unresolved):
    """Escape, then apply the inline subset: wikilinks, emphasis, code."""
    out = html.escape(text, quote=False)

    def link(m):
        target = m.group(1).strip()
        label = (m.group(2) or "").strip()
        pid = resolve(target)
        shown = label or (resolve.title(pid) if pid else target)
        if not pid:
            unresolved.append(target)
            return '<a class="wl missing" title="No page for this yet">%s</a>' % shown
        return '<a class="wl" href="#%s">%s</a>' % (pid, shown)

    out = WIKILINK.sub(link, out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    return out


# ---------------------------------------------------------------- block markdown

CALLOUT = re.compile(r"^>\s*\[!(\w+)\]\s*(.*)$")


def render_prose(body, resolve, unresolved):
    lines = body.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        m = CALLOUT.match(stripped)
        if m:
            kind, heading = m.group(1).lower(), m.group(2)
            i += 1
            para = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                para.append(lines[i].lstrip()[1:].strip())
                i += 1
            cls = "panel note" + (" warn" if kind in ("warning", "caution") else "")
            out.append('<div class="%s"><div class="ph">%s</div><p>%s</p></div>'
                       % (cls, inline(heading, resolve, unresolved),
                          inline(" ".join(para).strip(), resolve, unresolved)))
            continue

        if stripped.startswith("## "):
            out.append("<h2>%s</h2>" % inline(stripped[3:], resolve, unresolved))
            i += 1
            continue

        if stripped.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append("<li>%s</li>" % inline(lines[i].strip()[2:], resolve, unresolved))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue

        para = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("## ", "- ", ">")):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % inline(" ".join(para), resolve, unresolved))

    return "".join(out)


BEAT = re.compile(r"^-\s*`([^`]+)`\s*\*\*(.+?)\*\*\s*[—-]\s*(.*)$")


def render_timeline(body, resolve, unresolved):
    rows = []
    for line in body.split("\n"):
        m = BEAT.match(line.strip())
        if not m:
            continue
        rows.append(
            '<div class="beat"><div class="t">%s</div><div class="b">'
            '<strong>%s</strong><p>%s</p></div></div>'
            % (html.escape(m.group(1)),
               inline(m.group(2), resolve, unresolved),
               inline(m.group(3), resolve, unresolved))
        )
    return "".join(rows)


def render_threads(body, resolve, unresolved):
    blocks, cur = [], None
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("### "):
            if cur:
                blocks.append(cur)
            cur = {"title": s[4:], "cls": "open", "status": "", "body": []}
        elif cur is not None and s.startswith("`"):
            m = re.match(r"^`(\w+)`\s*(.*)$", s)
            if m:
                cur["cls"], cur["status"] = m.group(1), m.group(2)
        elif cur is not None and s:
            cur["body"].append(s)
    if cur:
        blocks.append(cur)
    return "".join(
        '<div class="thread %s"><div class="st">%s</div><h3>%s</h3><p>%s</p></div>'
        % (b["cls"], html.escape(b["status"]),
           inline(b["title"], resolve, unresolved),
           inline(" ".join(b["body"]), resolve, unresolved))
        for b in blocks
    )


# ---------------------------------------------------------------- assembly

def build():
    pages = load_pages()
    by_id = {p["id"]: p for p in pages}

    alias_index = {}
    for p in pages:
        alias_index.setdefault(p["title"].lower(), p["id"])
        for a in p["aliases"]:
            alias_index.setdefault(a.lower(), p["id"])

    def resolve(target):
        if target in by_id:
            return target
        return alias_index.get(target.lower())
    resolve.title = lambda pid: by_id[pid]["title"] if pid else ""

    # first pass: render bodies, collecting the link graph
    graph, unresolved_all = {}, []
    for p in pages:
        found = []
        layout = p.get("layout", "prose")
        renderer = {"timeline": render_timeline, "threads": render_threads}.get(layout, render_prose)
        p["html"] = renderer(p["raw"], resolve, found)
        unresolved_all += [(p["id"], t) for t in found]
        targets = {resolve(m.group(1).strip()) for m in WIKILINK.finditer(p["raw"])}
        graph[p["id"]] = {t for t in targets if t and t != p["id"]}

    # A floor page lists everything tagged to that floor, assembled here rather
    # than maintained by hand - the same trick as backlinks. Tag a mob with
    # `floor: 3` and it appears on Floor 3 without anyone updating an index.
    if AXIS:
        field, atype = AXIS["field"], AXIS["type"]
        members = {}
        for q in pages:
            val = q.get(field)
            if val and q.get("type") != atype:
                members.setdefault(str(val), []).append(q)
        for q in pages:
            if q.get("type") != atype:
                continue
            mine = members.get(str(q.get(field) or q["title"]), [])
            if not mine:
                q["html"] += ('<h2>On this floor</h2><p><em>Nothing catalogued '
                              'here yet.</em></p>')
                continue
            by_group = {}
            for m in sorted(mine, key=lambda x: x["title"]):
                by_group.setdefault(m.get("group", "Other"), []).append(m)
            out = ['<h2>On this floor</h2>']
            for g in GROUP_ORDER:
                if g not in by_group:
                    continue
                items = "".join(
                    '<li><a class="wl" href="#%s">%s</a>%s</li>'
                    % (m["id"], m["title"],
                       (' <span class="st-%s">%s</span>'
                        % (CFG["status_tone"].get(m.get("status",""), "warn"),
                           CFG["status_labels"].get(m.get("status",""), ""))
                        if m.get("status") else ""))
                    for m in by_group[g])
                out.append('<div class="axis-grp"><div class="ph">%s</div><ul>%s</ul></div>' % (g, items))
            q["html"] += "".join(out)

    backlinks = {p["id"]: [] for p in pages}
    for src, targets in graph.items():
        for t in targets:
            backlinks[t].append(src)

    def sort_key(p):
        g = p.get("group", "")
        gi = GROUP_ORDER.index(g) if g in GROUP_ORDER else len(GROUP_ORDER)
        order = AXIS.get("order", []) if AXIS else []
        if AXIS and p.get("type") == AXIS["type"]:
            val = str(p.get(AXIS["field"], ""))
            ai = order.index(val) if val in order else len(order)
            return (gi, ai, p["title"])
        return (gi, int(p.get("order", 99)), p["title"])

    payload = []
    for p in sorted(pages, key=sort_key):
        payload.append({
            "id": p["id"],
            "title": p["title"],
            "group": p.get("group", "Other"),
            "type": p.get("type", "thing"),
            "typeLabel": TYPE_LABEL.get(p.get("type", "thing"), "Page"),
            "dek": p.get("dek", ""),
            "conf": p.get("conf", ""),
            "confLabel": CONF_LABEL.get(p.get("conf", ""), ""),
            "player": p.get("player", ""),
            "status": p.get("status", ""),
            "statusLabel": CFG["status_labels"].get(p.get("status", ""), ""),
            "statusTone": CFG["status_tone"].get(p.get("status", ""), "warn"),
            "axis": str(p.get(AXIS["field"], "")) if AXIS else "",
            "axisLabel": AXIS["label"] if AXIS else "",
            "aliases": p["aliases"],
            "html": p["html"],
            "backlinks": sorted(backlinks[p["id"]], key=lambda i: by_id[i]["title"]),
            "search": " ".join([p["title"]] + p["aliases"] + [p.get("dek", "")]).lower(),
        })

    titles = {p["id"]: p["title"] for p in pages}
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    page = (tpl
            .replace("/*__PAGES__*/", json.dumps(payload, ensure_ascii=False))
            .replace("/*__TITLES__*/", json.dumps(titles, ensure_ascii=False))
            .replace("__TITLE__", CFG["title"])
            .replace("__SUBTITLE__", CFG["subtitle"])
            .replace("__BUILT__", date.today().isoformat()))

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    # An artifact-flavoured copy: same page without the document wrapper.
    if "--artifact" in sys.argv:
        dest = pathlib.Path(sys.argv[sys.argv.index("--artifact") + 1])
        frag = page[page.index("<title>"):]
        for tail in ("</body>", "</html>"):
            frag = frag.replace(tail, "")
        dest.write_text(frag.strip() + "\n", encoding="utf-8")
        print("artifact fragment -> %s" % dest)

    # Two different artefacts, for two different jobs.
    #
    # names.txt  - CANONICAL SPELLINGS ONLY. This is prompted into the
    #              transcriber, so listing a mangled spelling here would teach
    #              it that the mangling is a real word. Never include aliases.
    # corrections.json - alias -> canonical. Applied to the transcript AFTER
    #              recognition, to repair what the prompt didn't prevent.
    skip = set(CFG.get("names_exclude_types", ["doc"]))
    entities = [p for p in pages if p.get("type") not in skip]

    names = set()
    for p in entities:
        names.add(p["title"])
        if p.get("short"):
            names.add(p["short"])          # the form people actually say
    names = sorted(names)
    (ROOT / "names.txt").write_text(
        "# Canonical names only - pass to the transcriber with --names.\n"
        "# Do NOT add misspellings here; they belong in corrections.json.\n"
        + "\n".join(names) + "\n", encoding="utf-8")

    corrections = {}
    for p in entities:
        # Correct towards the spoken form, not the formal title: a
        # transcript should read "Brak", not "Sgt Brak Tanris".
        canonical = p.get("short") or p["title"]
        for a in p["aliases"]:
            if a.lower() != canonical.lower():
                corrections[a] = canonical
    (ROOT / "corrections.json").write_text(
        json.dumps(dict(sorted(corrections.items())), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    print("%d pages -> docs/index.html" % len(pages))
    print("%d canonical names -> names.txt" % len(names))
    print("%d corrections -> corrections.json" % len(corrections))
    if unresolved_all:
        print("\nUnresolved wikilinks (they render in red on the site):")
        for src, target in unresolved_all:
            print("  %-26s -> [[%s]]" % (src + ".md", target))
        return 1
    print("All wikilinks resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(build())
