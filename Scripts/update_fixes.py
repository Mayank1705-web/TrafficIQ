import os
import glob
import re

dashboard_dir = r'd:\MediCaps University\6 SEM\Mini project\TrafficIQ\Dashboard'
pages_dir = os.path.join(dashboard_dir, 'pages')
css_file = os.path.join(dashboard_dir, 'css', 'styles.css')
users_file = os.path.join(pages_dir, 'users.html')

# 1. Update users.html to remove Customer Journey Touchpoints
with open(users_file, 'r', encoding='utf-8') as f:
    users_content = f.read()

replace_str = '''        <section class="charts">
          <div class="chart-card">
            <div class="chart-header">
              <h3 class="chart-title-purple">Customer Journey Touchpoints</h3>

              <div class="chart-icon chart-purple">
                <i class="fa-solid fa-arrow-trend-up"></i>
              </div>
            </div>

            <div class="chart-wrap">
              <canvas id="journeyChart"></canvas>
            </div>
          </div>
          </div>
        </div>'''
users_content = users_content.replace(replace_str, '')

with open(users_file, 'w', encoding='utf-8') as f:
    f.write(users_content)


# 2. Update styles.css to fix .activity-row dark theme
with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

if '.activity-row' not in css_content.split('body.dark-theme')[-1]:
    css_content += '''\nbody.dark-theme .activity-row { background: #334155; border-color: #475569; }
body.dark-theme .activity-row h4 { color: #f8fafc; }\n'''
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)

# 3. Add About Us to all pages navigation
files = glob.glob(os.path.join(pages_dir, '*.html'))
for file in files:
    if os.path.basename(file) in ['login.html', 'signup.html', 'about.html']:
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'about.html' not in content:
        content = content.replace('</ul>\n        </nav>', '  <li>\n              <a href="about.html">\n                <i class="fa-solid fa-address-card"></i> About Us\n              </a>\n            </li>\n        </ul>\n        </nav>')
        content = content.replace('</ul>\n      </nav>', '  <li><a href="about.html"><i class="fa-solid fa-address-card"></i> About Us</a></li>\n        </ul>\n      </nav>')
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print('Executed fixes and nav updates.')
