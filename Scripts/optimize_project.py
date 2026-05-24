import os
import glob
import re

dashboard_dir = r'd:\MediCaps University\6 SEM\Mini project\TrafficIQ\Dashboard'
pages_dir = os.path.join(dashboard_dir, 'pages')
css_file = os.path.join(dashboard_dir, 'css', 'styles.css')

print(f"Starting optimization in {dashboard_dir}")

# 1. Optimize styles.css
if os.path.exists(css_file):
    with open(css_file, 'r', encoding='utf-8') as f:
        css = f.read()

    # Add CSS Variables if not present
    vars_css = """
:root {
  --bg-color: #f5f6fa;
  --text-color: #1e293b;
  --sidebar-bg: #ffffff;
  --card-bg: #ffffff;
  --primary-gradient: linear-gradient(135deg, #8b5cf6, #ec4899);
  --sidebar-hover: #f8fafc;
  --border-color: #e2e8f0;
}

body.dark-theme {
  --bg-color: #0f172a;
  --text-color: #f8fafc;
  --sidebar-bg: #1e293b;
  --card-bg: #1e293b;
  --sidebar-hover: #334155;
  --border-color: #334155;
}
"""
    if ':root' not in css:
        css = vars_css + '\n' + css

    # Fix Footer in Dark Theme - make it robust
    old_footer = """body.dark-theme .dashboard-footer {
  background: linear-gradient(90deg, #f8fafc, #e2e8f0);
  color: #0f172a;
}"""
    new_footer = """body.dark-theme .dashboard-footer {
  background: linear-gradient(90deg, #1e293b, #0f172a);
  color: #f8fafc;
}"""
    css = css.replace(old_footer, new_footer)

    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css)
    print("styles.css optimized.")

# 2. Update HTML pages
html_files = glob.glob(os.path.join(pages_dir, '*.html'))
for html_path in html_files:
    filename = os.path.basename(html_path)
    if filename in ['login.html', 'signup.html']:
        continue
        
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove redundant updateClock scripts
    # This regex is more robust
    content = re.sub(r'<script>\s*function updateClock.*?setInterval\(updateClock, 1000\);.*?updateClock\(\);?\s*</script>', '', content, flags=re.DOTALL)
    
    # Add common.js before auth.js or other scripts if not present
    if 'common.js' not in content:
        if '<script src="/js/auth.js"></script>' in content:
            content = content.replace('<script src="/js/auth.js"></script>', 
                                      '<script src="/js/auth.js"></script>\n    <script src="/js/common.js"></script>')
        elif '</body>' in content:
            content = content.replace('</body>', '    <script src="/js/common.js"></script>\n  </body>')
            
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Optimized {filename}")

print('Optimization script finished.')
