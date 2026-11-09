#!/usr/bin/env python3
"""Baut docs/index.html: Losung + Lehrtext des Tages, erst Vulgata, per Klick Deutsch."""
import argparse, html, json, os, re, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

# Kanonischer Name (= Schluessel in data/vulgata.json) -> Aliase (Losungen-Abkuerzungen + Volltext)
BOOKS = {
 "Genesis": ["1mo","1mose"], "Exodus": ["2mo","2mose"], "Leviticus": ["3mo","3mose"],
 "Numbers": ["4mo","4mose"], "Deuteronomy": ["5mo","5mose"], "Joshua": ["jos","josua"],
 "Judges": ["ri","richter"], "Ruth": ["rut","ruth"], "1 Samuel": ["1sam","1samuel"],
 "2 Samuel": ["2sam","2samuel"], "1 Kings": ["1kön","1koen","1könige"],
 "2 Kings": ["2kön","2koen","2könige"], "1 Chronicles": ["1chr","1chronik"],
 "2 Chronicles": ["2chr","2chronik"], "Ezra": ["esr","esra"], "Nehemiah": ["neh","nehemia"],
 "Esther": ["est","ester"], "Job": ["hiob","hi"], "Psalms": ["ps","psalm","psalmen"],
 "Proverbs": ["spr","sprüche","sprueche"], "Ecclesiastes": ["pred","prediger"],
 "Song of Solomon": ["hld","hoheslied"], "Isaiah": ["jes","jesaja"], "Jeremiah": ["jer","jeremia"],
 "Lamentations": ["klgl","klagelieder"], "Ezekiel": ["hes","hesekiel"], "Daniel": ["dan","daniel"],
 "Hosea": ["hos","hosea"], "Joel": ["joel"], "Amos": ["am","amos"], "Obadiah": ["obd","obadja"],
 "Jonah": ["jona"], "Micah": ["mi","micha"], "Nahum": ["nah","nahum"], "Habakkuk": ["hab","habakuk"],
 "Zephaniah": ["zef","zefanja"], "Haggai": ["hag","haggai"], "Zechariah": ["sach","sacharja"],
 "Malachi": ["mal","maleachi"], "Matthew": ["mt","matthäus","matthaeus"], "Mark": ["mk","markus"],
 "Luke": ["lk","lukas"], "John": ["joh","johannes"], "Acts": ["apg","apostelgeschichte"],
 "Romans": ["röm","roem","römer"], "1 Corinthians": ["1kor","1korinther"],
 "2 Corinthians": ["2kor","2korinther"], "Galatians": ["gal","galater"], "Ephesians": ["eph","epheser"],
 "Philippians": ["phil","philipper"], "Colossians": ["kol","kolosser"],
 "1 Thessalonians": ["1thess","1thessalonicher"], "2 Thessalonians": ["2thess","2thessalonicher"],
 "1 Timothy": ["1tim","1timotheus"], "2 Timothy": ["2tim","2timotheus"], "Titus": ["tit","titus"],
 "Philemon": ["phlm","philemon"], "Hebrews": ["hebr","hebräer","hebraeer"], "James": ["jak","jakobus"],
 "1 Peter": ["1petr","1petrus"], "2 Peter": ["2petr","2petrus"], "1 John": ["1joh","1johannes"],
 "2 John": ["2joh","2johannes"], "3 John": ["3joh","3johannes"], "Jude": ["jud","judas"],
 "Revelation": ["offb","offenbarung"], "Wisdom": ["weish","weisheit"], "Sirach": ["sir","sirach"],
 "Tobit": ["tob","tobit","tobias"], "Judith": ["jdt","judit"], "Baruch": ["bar","baruch"],
 "1 Maccabees": ["1makk","1makkabäer"], "2 Maccabees": ["2makk","2makkabäer"],
}
ALIAS = {}
for canon, al in BOOKS.items():
    ALIAS[re.sub(r"[.\s]", "", canon).lower()] = canon
    for a in al: ALIAS[a] = canon

def norm(s): return re.sub(r"[.\s]", "", s).lower()

def ps_chapter(h):
    """Hebraeische/Luther-Psalmzaehlung -> Vulgata-Zaehlung."""
    if h <= 8 or h >= 148: return h
    if h in (9, 10): return 9
    if h in (114, 115): return 113
    if h == 147: return 146
    return h - 1

REF = re.compile(r"^((?:[1-3]\.?\s*)?[A-Za-zÄÖÜäöüß]+\.?)\s*(\d+)\s*,\s*(.+)$")

def parse_ref(ref):
    """-> (kanon. Buch, [(kapitel, vers), ...]) oder None."""
    m = REF.match(ref.strip())
    if not m: return None
    book = ALIAS.get(norm(m.group(1)))
    if not book: return None
    ch, spec = int(m.group(2)), m.group(3)
    out = []
    for part in re.split(r"[.+]", spec):
        part = re.sub(r"[a-f]\b", "", part.strip())
        x = re.match(r"^(\d+)-(\d+),(\d+)$", part)          # Kapitelwechsel: 4-5,2
        if x:
            a, c2, b = map(int, x.groups())
            out += [(ch, v) for v in range(a, 200)] + [(c2, v) for v in range(1, b + 1)]
            continue
        x = re.match(r"^(\d+)(?:-(\d+))?$", part)
        if x:
            a = int(x.group(1)); b = int(x.group(2) or a)
            out += [(ch, v) for v in range(a, b + 1)]
    return book, out

def vulgate_text(vul, ref):
    p = parse_ref(ref)
    if not p: return None
    book, verses = p
    chapters = vul.get(book, {})
    parts = []
    for ch, v in verses:
        c = ps_chapter(ch) if book == "Psalms" else ch
        t = chapters.get(str(c), {}).get(str(v))
        if t: parts.append((v, t))
    return parts or None

def load_day(xml_path, day):
    iso, de = day.strftime("%Y-%m-%d"), day.strftime("%d.%m.%Y")
    for e in ET.parse(xml_path).getroot().iter():
        d = e.find("Datum")
        if d is not None and (d.text or "").strip()[:10] in (iso, de):
            g = lambda k: (e.findtext(k) or "").strip()
            return {"los_ref": g("Losungsvers"), "los": g("Losungstext"),
                    "lehr_ref": g("Lehrtextvers"), "lehr": g("Lehrtext")}
    return None

def card(label, ref, de_text, vul):
    parts = vulgate_text(vul, ref)
    if parts:
        body = " ".join(f'<sup>{v}</sup>{html.escape(t)}' for v, t in parts)
    else:
        body = '<span class="miss">Vulgata-Text nicht in data/vulgata.json gefunden.</span>'
    psalm = ' <span class="hint">(Psalmenzählung der Vulgata)</span>' if ref.lower().startswith(("ps", "psalm")) else ""
    return f'''<section class="card"><div class="label">{label}</div>
<p class="ref">{html.escape(ref)}{psalm}</p>
<p class="vul" lang="la">{body}</p>
<details><summary>Deutsch anzeigen</summary><p class="de" lang="de">{html.escape(de_text)}</p></details></section>'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", required=True)
    ap.add_argument("--vulgata", default="data/vulgata.json")
    ap.add_argument("--out", default="docs/index.html")
    a = ap.parse_args()
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    if os.environ.get("DATE"): now = datetime.fromisoformat(os.environ["DATE"])
    vul = json.loads(Path(a.vulgata).read_text(encoding="utf-8"))
    day = load_day(a.xml, now)
    months = "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split()
    days = "Montag Dienstag Mittwoch Donnerstag Freitag Samstag Sonntag".split()
    datum = f"{days[now.weekday()]}, {now.day}. {months[now.month-1]} {now.year}"
    if day:
        cards = card("Losung", day["los_ref"], day["los"], vul) + card("Lehrtext", day["lehr_ref"], day["lehr"], vul)
    else:
        cards = '<section class="card"><p>Für heute wurde in der Losungen-Datei kein Eintrag gefunden.</p></section>'
    tpl = Path("template.html").read_text(encoding="utf-8")
    out = tpl.replace("{{DATUM}}", datum).replace("{{CARDS}}", cards)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(out, encoding="utf-8")
    print("geschrieben:", a.out, "|", datum, "|", "ok" if day else "KEIN EINTRAG")

if __name__ == "__main__":
    sys.exit(main())
