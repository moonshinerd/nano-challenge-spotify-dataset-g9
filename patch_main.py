import re

with open("web/src/main.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = "import App from './App.jsx'"
replacement = "import App from './App.jsx'\nimport ErrorBoundary from './ErrorBoundary.jsx'"
content = content.replace(target, replacement)

target2 = "<App />"
replacement2 = "<ErrorBoundary><App /></ErrorBoundary>"
content = content.replace(target2, replacement2)

with open("web/src/main.jsx", "w", encoding="utf-8") as f:
    f.write(content)
