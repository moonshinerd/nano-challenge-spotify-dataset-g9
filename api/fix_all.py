import psycopg2
from ftfy import fix_text
from psycopg2.extras import execute_batch

conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()

cur.execute("SELECT track_id, track_name, artists FROM tracks;")
rows = cur.fetchall()

updates = []
for tid, tname, tartists in rows:
    fixed_name = fix_text(tname)
    fixed_artists = fix_text(tartists)
    if fixed_name != tname or fixed_artists != tartists:
        updates.append((fixed_name, fixed_artists, tid))

print(f"Found {len(updates)} remaining tracks to fix.")
if updates:
    execute_batch(cur, "UPDATE tracks SET track_name = %s, artists = %s WHERE track_id = %s", updates)
    conn.commit()
    print("Fixed!")
