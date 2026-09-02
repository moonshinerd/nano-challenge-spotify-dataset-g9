import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        cmd = ['yt-dlp', '-f', 'bestaudio', '-g', f'https://music.youtube.com/watch?v={videoId}']
        url = subprocess.check_output(cmd).decode('utf-8').strip()
        
        def iterfile():
            import requests
            with requests.get(url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
                        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(iterfile(), media_type="audio/mp4")"""

replacement = """        def iterfile():
            import subprocess
            process = subprocess.Popen(
                ['yt-dlp', '-f', 'bestaudio', '-o', '-', f'https://music.youtube.com/watch?v={videoId}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            try:
                while True:
                    chunk = process.stdout.read(65536)
                    if not chunk:
                        break
                    yield chunk
            finally:
                process.terminate()
                
        from fastapi.responses import StreamingResponse
        return StreamingResponse(iterfile(), media_type="audio/mp4")"""

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
