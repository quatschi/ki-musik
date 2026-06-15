#!/usr/bin/env python3
"""
Konvertiert alle bestehenden Kanal-HTML-Dateien im ki-musik-Verzeichnis
so dass sie die Sternebewertung und noten.json-Speicherung enthalten.

Lauf: python3 convert_to_rating.py
"""

import os, re, json, shutil
from datetime import datetime

# ============================================================
# PFAD ANPASSEN:
FOLDER = "/Volumes/hk/Documents/GitHub/ki-musik"   # Mac
# FOLDER = r"C:\Users\Harry\Documents\GitHub\ki-musik"  # Windows
# ============================================================

SKIP = {"index.html", "neu.html", "radio2.html", "radio.html", "_Anleitung.html"}


def extract_data(content, fname):
    title_m   = re.search(r'<title>(.*?)</title>', content)
    cat_m     = re.search(r'<!-- categories: (.*?) -->', content)
    chid_m    = re.search(r'<!-- channel-id: (.*?) -->', content)
    churl_m   = re.search(r'<!-- channel-url: (.*?) -->', content)
    avatar_m  = re.search(r"class='channel-avatar' src='([^']+)'", content)
    count_m   = re.search(r'(\d+) Videos', content)

    channel_name     = title_m.group(1)   if title_m   else fname.replace('.html','').replace('_',' ')
    categories       = cat_m.group(1)     if cat_m     else ''
    channel_id       = chid_m.group(1)    if chid_m    else ''
    channel_url      = churl_m.group(1)   if churl_m   else ''
    channel_thumbnail= avatar_m.group(1)  if avatar_m  else ''
    video_count      = count_m.group(1)   if count_m   else '0'

    cards = re.findall(
        r'<a class="video-card" href="https://www\.youtube\.com/watch\?v=([^"]+)"[^>]*>.*?'
        r'(?:<img src="([^"]*)"[^>]*>|<div class="[^"]*nothumb[^"]*">.*?</div>).*?'
        r'<span class="video-title">(.*?)</span>.*?'
        r'<span class="video-dur">(.*?)</span>',
        content, re.DOTALL
    )
    videos = [{"id": vid_id, "title": title.strip(), "thumb": thumb, "dur": dur.strip()}
              for vid_id, thumb, title, dur in cards]

    return channel_name, categories, channel_id, channel_url, channel_thumbnail, video_count, videos


def build_html(fname, channel_name, categories, channel_id, channel_url,
               channel_thumbnail, video_count, videos):
    radio_kanal  = fname
    avatar_html  = f"<img class='channel-avatar' src='{channel_thumbnail}'>" if channel_thumbnail else ""
    videos_json  = json.dumps(videos, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{channel_name}</title>
<!-- categories: {categories} -->
<!-- channel-id: {channel_id} -->
<!-- channel-url: {channel_url} -->
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; padding: 30px 20px 70px; color: white; }}
  .back {{ display: inline-block; color: #9b8fc0; text-decoration: none; font-size: 0.85rem; margin-bottom: 20px; letter-spacing: 0.05em; }}
  .back:hover {{ color: #e0d7ff; }}
  .channel-header {{ display: flex; align-items: center; gap: 20px; max-width: 860px; margin: 0 auto 30px; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
  .channel-avatar {{ width: 64px; height: 64px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(180,150,255,0.4); }}
  .channel-title {{ font-size: 1.5rem; font-weight: 300; color: #e0d7ff; letter-spacing: 0.05em; }}
  .channel-count {{ font-size: 0.8rem; color: #7a6fa0; margin-top: 4px; }}
  .grid {{ max-width: 860px; margin: 0 auto; display: flex; flex-direction: column; gap: 8px; }}
  .video-card {{ display: flex; align-items: center; gap: 14px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 10px 16px 10px 10px; color: white; transition: all 0.2s ease; }}
  .video-card:hover {{ background: rgba(255,255,255,0.12); border-color: rgba(180,150,255,0.35); }}
  .thumb {{ width: 120px; height: 68px; object-fit: cover; border-radius: 6px; flex-shrink: 0; }}
  .nothumb {{ width: 120px; height: 68px; background: rgba(255,255,255,0.08); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; color: #cc0000; flex-shrink: 0; }}
  .video-info {{ flex: 1; display: flex; flex-direction: column; gap: 6px; }}
  .video-title {{ font-size: 0.92rem; color: #e8e0ff; line-height: 1.3; }}
  .video-dur {{ font-size: 0.78rem; color: #7a6fa0; }}
  .rating-area {{ display: flex; align-items: center; gap: 6px; flex-shrink: 0; }}
  .stars {{ display: flex; gap: 3px; }}
  .star {{ font-size: 1.3rem; cursor: pointer; color: #4a4060; transition: color 0.15s; user-select: none; }}
  .star:hover, .star.active {{ color: #f0c040; }}
  .clear-btn {{ font-size: 0.7rem; cursor: pointer; padding: 2px 6px; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px; background: none; color: #9b8fc0; }}
  .clear-btn:hover {{ color: #fff; border-color: rgba(255,255,255,0.4); }}
  .save-bar {{ position: fixed; bottom: 0; left: 0; right: 0; background: rgba(20,15,50,0.97); border-top: 1px solid rgba(180,150,255,0.3); padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; gap: 12px; z-index: 100; }}
  .save-bar span {{ font-size: 0.85rem; color: #9b8fc0; }}
  .save-btn {{ background: #5a3fa0; color: white; border: none; padding: 8px 20px; border-radius: 8px; font-size: 0.9rem; cursor: pointer; }}
  .save-btn:hover {{ background: #7a5fc0; }}
  .changed-hint {{ font-size: 0.75rem; color: #f0c040; display: none; }}
  .status-msg {{ font-size: 0.78rem; color: #7a6fa0; font-style: italic; }}
  .status-ok {{ color: #6fcf97; }}
</style>
</head>
<body>
  <div style="max-width:860px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
    <a class="back" href="index.html">← Zurück zur Übersicht</a>
    <a class="back" href="radio2.html?kanal={radio_kanal}" style="border:1px solid rgba(180,150,255,0.4);padding:6px 14px;border-radius:20px">▶ Nur diesen Kanal im Radio</a>
  </div>
  <div class="channel-header">
    {avatar_html}
    <div>
      <div class="channel-title">{channel_name}</div>
      <div class="channel-count">{video_count} Videos</div>
    </div>
  </div>
  <div class="grid" id="grid"></div>

  <div class="save-bar">
    <span>Bewertet: <strong id="rated-count">0</strong> &nbsp;<span class="changed-hint" id="changed-hint">● ungespeichert</span></span>
    <span class="status-msg" id="status-msg"></span>
    <button class="save-btn" onclick="saveRatings()">💾 Speichern</button>
  </div>

<script>
const CHANNEL = {json.dumps(channel_name)};
const VIDEOS = {videos_json};
let ratings = {{}}, changed = false, fileHandle = null;

async function loadRatings() {{
  try {{
    const r = await fetch('noten.json');
    if (r.ok) {{ const d = await r.json(); ratings = d.ratings || {{}}; }}
  }} catch(e) {{}}
  renderGrid();
}}

function renderGrid() {{
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  VIDEOS.forEach(v => {{
    const card = document.createElement('div');
    card.className = 'video-card';
    const cur = ratings[v.id] || 0;
    card.innerHTML = `
      <a href="https://www.youtube.com/watch?v=${{v.id}}" target="_blank" style="display:flex;align-items:center;gap:14px;flex:1;text-decoration:none;color:inherit">
        ${{v.thumb ? `<img src="${{v.thumb}}" class="thumb">` : '<div class="nothumb">▶</div>'}}
        <div class="video-info">
          <span class="video-title">${{v.title}}</span>
          <span class="video-dur">${{v.dur}}</span>
        </div>
      </a>
      <div class="rating-area">
        <div class="stars" id="stars-${{v.id}}">
          ${{[1,2,3,4,5].map(n => `<span class="star ${{n <= cur ? 'active' : ''}}" onclick="setRating('${{v.id}}',${{n}})">★</span>`).join('')}}
        </div>
        <button class="clear-btn" onclick="setRating('${{v.id}}',0)">✕</button>
      </div>`;
    grid.appendChild(card);
  }});
  updateCount();
}}

function setRating(id, val) {{
  ratings[id] = val;
  changed = true;
  document.getElementById('changed-hint').style.display = 'inline';
  document.querySelectorAll(`#stars-${{id}} .star`).forEach((s,i) => s.classList.toggle('active', i < val));
  updateCount();
}}

function updateCount() {{
  document.getElementById('rated-count').textContent = Object.values(ratings).filter(v => v > 0).length;
}}

function buildJson() {{
  return JSON.stringify({{ channel: CHANNEL, updated: new Date().toISOString(), ratings }}, null, 2);
}}

async function saveRatings() {{
  const json = buildJson();
  if ('showSaveFilePicker' in window) {{
    try {{
      if (!fileHandle) {{
        fileHandle = await window.showSaveFilePicker({{
          suggestedName: 'noten.json',
          types: [{{ description: 'JSON', accept: {{'application/json': ['.json']}} }}]
        }});
      }}
      const w = await fileHandle.createWritable();
      await w.write(json); await w.close();
      changed = false;
      document.getElementById('changed-hint').style.display = 'none';
      document.getElementById('status-msg').textContent = '✓ Direkt gespeichert';
      document.getElementById('status-msg').className = 'status-msg status-ok';
      return;
    }} catch(e) {{ if (e.name === 'AbortError') return; fileHandle = null; }}
  }}
  const blob = new Blob([json], {{type: 'application/json'}});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = 'noten.json'; a.click();
  changed = false;
  document.getElementById('changed-hint').style.display = 'none';
  document.getElementById('status-msg').textContent = '↓ Als Download gespeichert';
}}

loadRatings();
</script>
</body>
</html>"""


def main():
    if not os.path.isdir(FOLDER):
        print(f"FEHLER: Verzeichnis nicht gefunden: {FOLDER}")
        print("Bitte FOLDER im Script anpassen.")
        input("\nEnter drücken zum Beenden . . .")
        return

    # Backup anlegen
    backup_dir = os.path.join(FOLDER, "_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_dir, exist_ok=True)

    files = [f for f in os.listdir(FOLDER)
             if f.endswith('.html') and not f.startswith('_') and f not in SKIP]
    files.sort()

    print(f"Gefunden: {len(files)} Kanal-HTML-Dateien")
    print(f"Backup-Verzeichnis: {backup_dir}")
    print()

    ok = 0
    skip = 0
    errors = []

    for fname in files:
        fpath = os.path.join(FOLDER, fname)
        try:
            with open(fpath, encoding='utf-8') as f:
                content = f.read()

            # Bereits konvertierte Dateien überspringen
            if 'saveRatings' in content:
                print(f"  ⊘ bereits konvertiert: {fname}")
                skip += 1
                continue

            # Backup
            shutil.copy2(fpath, os.path.join(backup_dir, fname))

            # Daten extrahieren
            channel_name, categories, channel_id, channel_url, \
                channel_thumbnail, video_count, videos = extract_data(content, fname)

            if not videos:
                print(f"  ⚠ keine Videos gefunden (Fallback-Seite?): {fname}")
                skip += 1
                continue

            # Neue HTML schreiben
            new_html = build_html(fname, channel_name, categories, channel_id,
                                  channel_url, channel_thumbnail, video_count, videos)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_html)

            print(f"  ✓ {fname} ({len(videos)} Videos)")
            ok += 1

        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  ✗ FEHLER: {fname} → {e}")

    print(f"\n{'='*50}")
    print(f"Konvertiert:  {ok}")
    print(f"Übersprungen: {skip}")
    print(f"Fehler:       {len(errors)}")
    if errors:
        print("\nDateien mit Fehlern:")
        for fname, err in errors:
            print(f"  {fname}: {err}")
    print(f"\nBackup liegt in: {backup_dir}")
    input("\nEnter drücken zum Beenden . . .")


if __name__ == "__main__":
    main()
