import os
import glob
import re

pages_dir = r'd:\MediCaps University\6 SEM\Mini project\TrafficIQ\Dashboard\pages'
files = glob.glob(os.path.join(pages_dir, '*.html'))

for file in files:
    if os.path.basename(file) in ['login.html', 'signup.html']:
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the theme toggle from sidebar
    content = re.sub(r'\s*<li><a href="#" onclick="toggleTheme\(event\)"><i class="fa-solid fa-moon theme-icon-toggle"></i> Toggle Theme</a></li>', '', content)
    
    # 2. Add the toggle button next to the live-box.
    if 'id="themeToggle"' not in content:
        live_box_pattern = r'(<div class="live-box">.*?</div>)'
        
        replacement = r'''<div style="display: flex; gap: 15px; align-items: center;">
          <button id="themeToggle" onclick="toggleTheme(event)" style="padding: 10px 15px; border-radius: 12px; border: none; cursor: pointer; background: rgba(255,255,255,0.2); color: white; font-weight: 600; transition: 0.3s; display: flex; align-items: center; gap: 8px;">
            <i class="fa-solid fa-moon theme-icon-toggle"></i> Theme
          </button>
          \1
        </div>'''
        
        content = re.sub(live_box_pattern, replacement, content, count=1, flags=re.DOTALL)
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated HTML files.')
