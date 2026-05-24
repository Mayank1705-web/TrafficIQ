function signup() {
  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const btn = document.querySelector(".btn");

  if (!username || !email || !password) {
    showMsg("Please fill in all fields.", "error");
    return;
  }

  if (password.length < 8) {
    // ✅ Fix 3: minimum 8 characters
    showMsg("Password must be at least 8 characters.", "error");
    return;
  }

  btn.disabled = true;
  btn.textContent = "Creating account…";

  fetch("http://127.0.0.1:8000/api/signup", {
    // ✅ Fix 1: correct URL
    method: "POST",
    credentials: "include", // ✅ Fix 2: include cookies
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        showMsg(data.message, "success");
        setTimeout(() => {
          window.location.href = "login.html";
        }, 1500);
      } else {
        showMsg(data.message || "Signup failed.", "error");
        btn.disabled = false;
        btn.textContent = "Create Account";
      }
    })
    .catch(() => {
      showMsg("Server unreachable. Make sure the backend is running.", "error");
      btn.disabled = false;
      btn.textContent = "Create Account";
    });
}

function showMsg(text, type) {
  let el = document.getElementById("signup-msg");
  if (!el) {
    el = document.createElement("p");
    el.id = "signup-msg";
    el.style.cssText = `       font-size: 0.82rem; text-align: center;
      margin-top: 14px; animation: fadeSlide 0.3s ease both;
    `;
    const wrap = document.querySelector(".btn-wrap");
    if (wrap) wrap.insertAdjacentElement("afterend", el);
  }
  el.textContent = text;
  el.style.color = type === "success" ? "#4ade80" : "#f87171";
}
