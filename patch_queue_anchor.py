import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = '<div className="absolute bottom-16 right-0 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4 max-h-96 overflow-y-auto custom-scrollbar flex flex-col gap-2">'
replacement = '<div className="absolute bottom-full mb-4 right-0 sm:right-8 w-80 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-4 max-h-96 overflow-y-auto custom-scrollbar flex flex-col gap-2">'

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
