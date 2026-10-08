import re

path = r"D:\Projects\Data_Quest_3.0\frontend\src\pages\ResultsDashboard.jsx"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<div className="flex justify-between items-center mb-8">.*?Start Over\s*</button>\s*(</div>)?\s*(</div>)?'

new_header = '''<div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900">PRISM Analysis Results</h1>
          <div className="flex gap-4">
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 cursor-pointer shadow-sm"
            >
              <option value="English">English</option>
              <option value="Hindi">Hindi</option>
              <option value="Tamil">Tamil</option>
              <option value="Telugu">Telugu</option>
            </select>
            <button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Start Over
            </button>
          </div>
        </div>'''

# Actually, because the previous regex might have messed up the tree, let's just find the exact block:
# It starts at <div className="flex justify-between items-center mb-8">
# and we should replace until the next <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
pattern2 = r'<div className="flex justify-between items-center mb-8">.*?<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">'

replacement2 = new_header + '\n\n        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">'

new_content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Fixed JSX tree.")
