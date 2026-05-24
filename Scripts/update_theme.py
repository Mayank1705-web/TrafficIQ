import os
import glob

pages_dir = r'd:\MediCaps University\6 SEM\Mini project\TrafficIQ\Dashboard\pages'
files = glob.glob(os.path.join(pages_dir, '*.html'))

for file in files:
    if os.path.basename(file) in ['index.html', 'login.html', 'signup.html']:
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add theme.js
    if '<script src="/js/theme.js"></script>' not in content:
        content = content.replace('</head>', '  <script src="/js/theme.js"></script>\n</head>')
    
    # Add toggle button
    if 'toggleTheme(event)' not in content:
        content = content.replace('</ul>', '  <li><a href="#" onclick="toggleTheme(event)"><i class="fa-solid fa-moon theme-icon-toggle"></i> Toggle Theme</a></li>\n        </ul>')
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Updated HTML files.')
