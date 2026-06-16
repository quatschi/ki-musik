#!/usr/bin/env python3
"""
Fügt allen bestehenden Kanal-HTML-Dateien das heutige Datum
als <!-- created: YYYY-MM-DD --> Kommentar hinzu.
Einmalig ausführen – Dateien die bereits einen created-Kommentar
haben werden übersprungen.
"""

import os, re
from datetime import datetime

# ============================================================
FOLDER = "/Volumes/hk/Documents/GitHub/ki-musik"   # Mac
# FOLDER = r"C:\Users\hkron\OneDrive\Dokumente\GitHub\ki-musik"  # Windows
# ============================================================

SKIP = {"index.html", "neu.html", "radio2.html", "radio.html", "_Anleitung.html"}
TODAY = datetime.now().strftime("%Y-%m-%d")

files = [f for f in os.listdir(FOLDER)
         if f.endswith(".html") and not f.startswith("_") and f not in SKIP]

ok = 0
skip = 0
errors = []

for fname in sorted(files):
    fpath = os.path.join(FOLDER, fname)
    try:
        with open(fpath, encoding="utf-8") as f:
            content = f.read()

        if "<!-- created:" in content:
            skip += 1
            continue

        new_content = re.sub(
            r"(<!-- channel-url: [^\n]+ -->)",
            r"\1\n<!-- created: " + TODAY + " -->",
            content, count=1
        )

        if new_content != content:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            ok += 1
            print(f"  ✓ {fname}")
        else:
            print(f"  ⚠ kein channel-url Kommentar: {fname}")
            skip += 1

    except Exception as e:
        errors.append((fname, str(e)))
        print(f"  ✗ FEHLER: {fname} → {e}")

print(f"\n{'='*50}")
print(f"Eingetragen:  {ok}")
print(f"Übersprungen: {skip}")
print(f"Fehler:       {len(errors)}")
print(f"\nDatum: {TODAY}")
input("\nEnter drücken zum Beenden . . .")
