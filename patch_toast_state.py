import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = "const [errorMsg, setErrorMsg] = useState(null);"
replacement = "const [errorMsg, setErrorMsg] = useState(null);\n  const [toast, setToast] = useState(null);"

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
