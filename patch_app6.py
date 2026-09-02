import re

with open("web/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

target1 = '<div key={track.track_id} className="flex items-center justify-between p-3 hover:bg-gray-700 rounded-lg transition-colors">'
replacement1 = '<div key={track.track_id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 hover:bg-gray-700 rounded-lg transition-colors gap-3 sm:gap-0">'

target2 = '<div className="flex items-center gap-4">'
# We need to make sure we only replace the one inside the search results.
# So we'll use a regex that matches the context, or just replace the first occurrence after target1.

content = content.replace(target1, replacement1)

# Now fix the buttons wrapper
target3 = '<div className="flex gap-2">'
# There are multiple "flex gap-2". The one in search results is the first one after `<div key={track.track_id}`
# Let's just use string replacement on the exact button code.

target_btn = """                  <button 
                    onClick={() => getRecommendations(track.track_id, track.source)}
                    className="px-6 py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-full transition-transform hover:scale-105"
                  >
                    Analisar & Recomendar
                  </button>
                </div>"""

replacement_btn = """                  <button 
                    onClick={() => getRecommendations(track.track_id, track.source)}
                    className="px-4 py-2 sm:px-6 sm:py-3 bg-green-500 hover:bg-green-600 text-black font-bold rounded-full transition-transform hover:scale-105 flex items-center gap-2"
                  >
                    <span className="hidden sm:inline">Analisar & Recomendar</span>
                    <span className="sm:hidden flex items-center gap-1"><Wand2 size={16}/> Analisar</span>
                  </button>
                </div>"""

content = content.replace(target_btn, replacement_btn)

# Also let's make sure the button wrapper has self-end on mobile
target_wrapper = """                <div className="flex gap-2">
                  <button 
                    onClick={() => toggleTrackSelection(track)}"""

replacement_wrapper = """                <div className="flex gap-2 self-end sm:self-auto">
                  <button 
                    onClick={() => toggleTrackSelection(track)}"""

content = content.replace(target_wrapper, replacement_wrapper)

with open("web/src/App.jsx", "w", encoding="utf-8") as f:
    f.write(content)
