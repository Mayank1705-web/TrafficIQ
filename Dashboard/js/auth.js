const API_BASE = "http://127.0.0.1:8000";

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
  const depth = location.pathname.split("/").filter(Boolean).length;
  const prefix = depth > 1 ? "../".repeat(depth - 1) : "";
  window.location.replace(`${prefix}pages/login.html`);
}

async function logout() {
  try {
    await fetch(`${API_BASE}/api/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {}
  window.location.replace("login.html");
}
