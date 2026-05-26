async function checkAuth() {
  try {
    const res = await fetch(`${API_BASE}/api/me`, { credentials: "include" });
    if (!res.ok) {
      redirectToLogin();
    } else {
      const data = await res.json();
      const el = document.getElementById("username-display");
      if (el && data.username) el.textContent = data.username;
    }
  } catch {
    redirectToLogin();
  }
}

function checkLogin() {
  checkAuth();
}

function redirectToLogin() {
  window.location.replace("/login.html");
}

async function logout() {
  try {
    await fetch(`${API_BASE}/api/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {}
  window.location.replace("/login.html");
}