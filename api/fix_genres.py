import psycopg2
from main import ITUNES_TO_KAGGLE_GENRES
from psycopg2.extras import execute_batch

conn = psycopg2.connect(host="db", dbname="spotify", user="user", password="password")
cur = conn.cursor()

cur.execute("SELECT track_id, track_genre FROM tracks;")
rows = cur.fetchall()

updates = []
for tid, genre in rows:
    if genre:
        # Split por virgula se houver mais de um
        genres = [g.strip().lower() for g in genre.split(',')]
        new_genres = []
        for g in genres:
            new_genres.append(ITUNES_TO_KAGGLE_GENRES.get(g, g))
        
        new_genre_str = ", ".join(new_genres)
        if new_genre_str != genre:
            updates.append((new_genre_str, tid))

print(f"Found {len(updates)} genres to fix.")
if updates:
    execute_batch(cur, "UPDATE tracks SET track_genre = %s WHERE track_id = %s", updates)
    conn.commit()
    print("Fixed!")
