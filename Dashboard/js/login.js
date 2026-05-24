function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  const btn = document.querySelector(".btn");

  if (!username || !password) {
    showError("Please enter both username and password.");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Signing in…";

  fetch(`${API_BASE}/api/login`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        window.location.href = "index.html";
      } else {
        showError(data.message || "Invalid username or password.");
        btn.disabled = false;
        btn.textContent = "Login";
      }
    })
    .catch(() => {
      showError("Server unreachable. Make sure the backend is running.");
      btn.disabled = false;
      btn.textContent = "Login";
    });
}

function showError(message) {
  let el = document.getElementById("error-msg");
  if (!el) {
    el = document.createElement("p");
    el.id = "error-msg";
    el.style.cssText = `       color: #f87171; font-size: 0.82rem; text-align: center;
      margin-top: 14px; animation: fadeSlide 0.3s ease both;
    `;
    const wrap = document.querySelector(".btn-wrap");
    if (wrap) wrap.insertAdjacentElement("afterend", el);
  }
  el.textContent = message;
}

function logout() {
  window.location.href = "../pages/login.html";
}
