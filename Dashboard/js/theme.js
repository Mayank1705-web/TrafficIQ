// theme.js
// Handles the application of the global dark theme

function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    // Apply to html element immediately for early styles
    document.documentElement.classList.add('dark-theme');
    // Ensure body also gets it when ready
    document.addEventListener("DOMContentLoaded", () => {
      document.body.classList.add('dark-theme');
      updateThemeIcon(true);
    });
  }
}

function toggleTheme(event) {
  if (event) event.preventDefault();
  
  const isDark = document.body.classList.toggle('dark-theme');
  
  if (isDark) {
    localStorage.setItem('theme', 'dark');
  } else {
    localStorage.removeItem('theme');
  }
  
  updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
  const themeIcons = document.querySelectorAll('.theme-icon-toggle');
  themeIcons.forEach(icon => {
    if (isDark) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
    }
  });
}

// Initialize theme immediately to prevent flash of wrong theme
initTheme();
