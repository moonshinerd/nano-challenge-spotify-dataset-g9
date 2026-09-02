import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = '<div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-4 px-8 flex items-center justify-between z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)]">'
replacement = '<div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-4 px-4 sm:px-8 flex flex-wrap sm:flex-nowrap items-center justify-between z-50 shadow-[0_-10px_30px_rgba(0,0,0,0.5)] gap-4 sm:gap-0">'

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
