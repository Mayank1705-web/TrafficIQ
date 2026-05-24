const API_BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
  ? "http://127.0.0.1:8000"
  : "";

async function loadSystemStatus() {
  try {
    const res = await fetch(`${API_BASE}/system-status`, {
      credentials: "include",
    });

    const data = await res.json();
    const el = document.querySelector(".status-green");

    if (!el) return;

    if (data.status === "operational") {
      el.textContent = "All Systems Operational";
      el.style.color = "#22c55e";
    } else {
      el.textContent = "System Issues Detected";
      el.style.color = "#ef4444";
    }
  } catch (err) {
    console.error("System status error:", err);
  }
}

function buildHistoryRow(item) {
  const path = item.path || "Unknown file";
  const fileName = path.split("/").pop();
  const records = (item.records || 0).toLocaleString();
  const time = item.time || "";
  const status = (item.status || "Complete").toLowerCase();

  let statusText = "✓ Complete";
  let statusClass = "complete";

  if (status === "failed" || status === "error") {
    statusText = "✗ Failed";
    statusClass = "failed";
  } else if (status === "running") {
    statusText = "⟳ Running";
    statusClass = "running";
  }

  return `
    <div class="history-row">

      <div class="history-left">
        <div class="history-icon">
          <i class="fa-solid fa-check"></i>
        </div>

        <div>
          <h4 style="margin:0;font-size:15px;">${fileName}</h4>
          <p style="font-size:12px;color:#94a3b8;margin:2px 0;">
            ${path}
          </p>
          <p style="font-size:13px;color:#64748b;margin:0;">
            ${records} records processed
          </p>
        </div>
      </div>

      <div class="history-right">
        <span style="font-size:13px;color:#94a3b8;">${time}</span><br>
        <span class="${statusClass}">${statusText}</span>
      </div>

    </div>
  `;
}

async function loadHistory() {
  const container = document.getElementById("historyContainer");
  if (!container) return;

  // loading state
  container.innerHTML = `
    <div style="text-align:center;padding:30px;color:#94a3b8;">
      <i class="fa-solid fa-spinner fa-spin"></i>
      <p>Loading history...</p>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/history`, {
      credentials: "include",
    });

    const history = await res.json();

    if (!Array.isArray(history) || history.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:40px;color:#94a3b8;">
          <i class="fa-solid fa-clock-rotate-left" style="font-size:28px;"></i>
          <p>No processing history yet</p>
        </div>
      `;
      return;
    }

    container.innerHTML = history
      .map(item => buildHistoryRow(item))
      .join("");

  } catch (err) {
    console.error("History error:", err);

    container.innerHTML = `
      <div style="text-align:center;padding:30px;color:#ef4444;">
        <i class="fa-solid fa-triangle-exclamation"></i>
        <p>Failed to load history</p>
      </div>
    `;
  }
}

async function runPipeline() {
  const input = document.getElementById("datasetPath");
  const btn = document.querySelector(".pipeline-btn");

  if (!input || !input.value.trim()) {
    input.style.border = "1px solid red";

    setTimeout(() => {
      input.style.border = "";
    }, 2000);

    alert("Please enter dataset path");
    return;
  }

  const path = input.value.trim();

  // button loading
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Running...`;
  }

  try {
    const res = await fetch(`${API_BASE}/run-pipeline`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ path }),
    });

    const data = await res.json();

    alert(data.message || "Pipeline executed");

    // reload history after run
    loadHistory();

  } catch (err) {
    console.error("Pipeline error:", err);
    alert("Pipeline failed");
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i class="fa-solid fa-play"></i> Run Analytics Pipeline`;
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadSystemStatus();
  loadHistory();

  const btn = document.querySelector(".pipeline-btn");
  if (btn) {
    btn.addEventListener("click", runPipeline);
  }
});