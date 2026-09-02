import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = '<div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto flex flex-col lg:flex-row gap-8 pb-32 justify-center">'
replacement = '<div className={`min-h-screen p-4 md:p-8 max-w-7xl mx-auto flex flex-col lg:flex-row gap-8 justify-center transition-all duration-300 ${currentPlaying ? "pb-48" : "pb-12"}`}>'

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
