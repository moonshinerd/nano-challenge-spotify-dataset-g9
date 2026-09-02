import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = "import { Search, Play, Pause, X, Loader2, Music, SkipBack, SkipForward } from 'lucide-react'"
replacement = "import { Search, Play, Pause, X, Loader2, Music, SkipBack, SkipForward, Wand2 } from 'lucide-react'"

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
