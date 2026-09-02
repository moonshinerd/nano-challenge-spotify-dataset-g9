import psycopg2
from ftfy import fix_text

conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()

# Get all tracks that might have bad encoding
cur.execute("SELECT track_id, track_name, artists FROM tracks WHERE track_name LIKE '%Ã%' OR track_name LIKE '%â€%' OR artists LIKE '%Ã%' OR artists LIKE '%â€%';")
rows = cur.fetchall()

print(f"Found {len(rows)} tracks to fix.")

update_query = "UPDATE tracks SET track_name = %s, artists = %s WHERE track_id = %s"
updates = []

for row in rows:
    tid, tname, tartists = row
    fixed_name = fix_text(tname)
    fixed_artists = fix_text(tartists)
    updates.append((fixed_name, fixed_artists, tid))

from psycopg2.extras import execute_batch
execute_batch(cur, update_query, updates)
conn.commit()

print(f"Fixed {len(updates)} tracks successfully!")
