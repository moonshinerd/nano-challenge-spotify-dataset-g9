import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = "const [duration, setDuration] = useState(0)"
replacement = "const [duration, setDuration] = useState(0)\n  const [showQueue, setShowQueue] = useState(false)"
content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
