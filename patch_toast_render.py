import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target = '    <div className={`min-h-screen'
replacement = """    {/* TOAST NOTIFICATION */}
    {toast && (
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-6 py-3 rounded-full shadow-2xl z-50 flex items-center gap-3 animate-fade-in">
        <X size={18} className="cursor-pointer hover:text-gray-200" onClick={() => setToast(null)} />
        <span className="font-bold text-sm md:text-base">{toast}</span>
      </div>
    )}

    <div className={`min-h-screen"""

content = content.replace(target, replacement)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
