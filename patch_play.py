import re

with open("api/main.py", "r", encoding="utf-8") as f:
    content = f.read()

target = """        cmd = ['yt-dlp', '-f', 'bestaudio', '-g', f'https://music.youtube.com/watch?v={videoId}']
        url = subprocess.check_output(cmd).decode('utf-8').strip()
        
        return RedirectResponse(url)
    except Exception as e:"""

replacement = """        cmd = ['yt-dlp', '-f', 'bestaudio', '-g', f'https://music.youtube.com/watch?v={videoId}']
        url = subprocess.check_output(cmd).decode('utf-8').strip()
        
        def iterfile():
            import requests
            with requests.get(url, stream=True) as r:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
                        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(iterfile(), media_type="audio/mp4")
    except Exception as e:"""

content = content.replace(target, replacement)

with open("api/main.py", "w", encoding="utf-8") as f:
    f.write(content)
