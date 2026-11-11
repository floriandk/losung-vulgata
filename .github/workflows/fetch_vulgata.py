#!/usr/bin/env python3
"""Laedt die Clementina (gemeinfrei) von latinprayer.org und schreibt data/vulgata.json
im Format {"Buch": {"Kapitel": {"Vers": "Text"}}} mit den Buchnamen aus build.py."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen

INDEX = "https://latinprayer.org/bible-index.json"

# Reihenfolge der 73 Buecher im Index (order 1..73) -> Schluessel wie in build.py
NAMES = """Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|1 Samuel|2 Samuel|1 Kings|2 Kings|
1 Chronicles|2 Chronicles|Ezra|Nehemiah|Tobit|Judith|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song of Solomon|
Wisdom|Sirach|Isaiah|Jeremiah|Lamentations|Baruch|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|
Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|1 Maccabees|2 Maccabees|Matthew|Mark|Luke|John|Acts|Romans|
1 Corinthians|2 Corinthians|Galatians|Ephesians|Philippians|Colossians|1 Thessalonians|2 Thessalonians|
1 Timothy|2 Timothy|Titus|Philemon|Hebrews|James|1 Peter|2 Peter|1 John|2 John|3 John|Jude|Revelation"""
NAMES = [n.strip() for n in NAMES.replace("\n", "").split("|")]

def get_json(url, tries=4):
    for i in range(tries):
        try:
            req = Request(url, headers={"User-Agent": "losung-vulgata/1.0 (private Lesehilfe)"})
            with urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(2 * (i + 1))

def fetch_chapter(url):
    d = get_json(url)
    return {str(v["verse"]): v["text"].strip() for v in d["verses"]}

def main(out="data/vulgata.json"):
    books = get_json(INDEX)["books"]
    if len(books) != len(NAMES):
        sys.exit(f"Erwartet {len(NAMES)} Buecher, Index liefert {len(books)}.")
    result = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for b in sorted(books, key=lambda x: x["order"]):
            name = NAMES[b["order"] - 1]
            idx = get_json(b["translations"]["latin"]["jsonUrl"])
            chapters = idx["chapters"]
            texts = list(pool.map(fetch_chapter, [c["jsonUrl"] for c in chapters]))
            result[name] = {str(c["chapter"]): t for c, t in zip(chapters, texts)}
            print(f'{b["order"]:2d} {b["canonicalSlug"]:22s} -> {name} ({len(chapters)} Kap.)', flush=True)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("geschrieben:", out)

if __name__ == "__main__":
    main(*sys.argv[1:])
