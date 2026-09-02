import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """                if db_match:
                    lista.append({
                        "track_id": db_match['track_id'], # Passamos o ID do Banco para ser instantâneo na hora de recomendar
                        "track_name": track_name,
                        "artists": arts,
                        "genre": db_match['track_genre'],
                        "thumbnail": img_url,
                        "source": "database"
                    })"""

replacement = """                if db_match:
                    t_genre = db_match['track_genre']
                    
                    if not t_genre or t_genre.lower() == "desconhecido":
                        new_g = get_genres_combined(track_name, arts)
                        if new_g:
                            t_genre = new_g
                            # Atualiza no banco na mesma conexão que temos! Mas db_match é só leitura, vamos fazer um update.
                            # Para evitar travar o loop ou transação complexa:
                            with engine.begin() as conn_upd:
                                conn_upd.execute(
                                    text("UPDATE tracks SET track_genre = :g WHERE track_id = :tid"),
                                    {"g": t_genre, "tid": db_match['track_id']}
                                )

                    lista.append({
                        "track_id": db_match['track_id'],
                        "track_name": track_name,
                        "artists": arts,
                        "genre": t_genre,
                        "thumbnail": img_url,
                        "source": "database"
                    })"""

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
