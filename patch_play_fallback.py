import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        if not videoId and query:
            yt_res = yt_client.search(query, filter="songs", limit=1)
            if yt_res:
                videoId = yt_res[0].get('videoId')"""

replacement = """        if not videoId and query:
            yt_res = yt_client.search(query + " audio", limit=3)
            # Try to find a valid videoId that is not None
            for res in yt_res:
                if res.get('videoId'):
                    videoId = res.get('videoId')
                    break"""

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
