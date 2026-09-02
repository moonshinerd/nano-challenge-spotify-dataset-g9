import psycopg2
from psycopg2.extras import execute_batch

conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()
cur.execute("SELECT track_id, track_name, artists FROM tracks;")
rows = cur.fetchall()

def fix_mojibake(text):
    if not text:
        return text
    try:
        # If it can be encoded to win1252 and then decoded as utf-8, and it's different!
        fixed = text.encode('windows-1252').decode('utf-8')
        return fixed
    except Exception:
        # If it throws an error (e.g. contains real UTF-8 chars not in win1252)
        return text

updates = []
for tid, tname, tartists in rows:
    fixed_name = fix_mojibake(tname)
    fixed_artists = fix_mojibake(tartists)
    if fixed_name != tname or fixed_artists != tartists:
        updates.append((fixed_name, fixed_artists, tid))

print(f"Found {len(updates)} tracks to fix with win1252 heuristic.")
if updates:
    execute_batch(cur, "UPDATE tracks SET track_name = %s, artists = %s WHERE track_id = %s", updates)
    conn.commit()
    print("Fixed!")
