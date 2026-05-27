document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } }
  };

  const fetchSection = (endpoint) => {
    return fetch(`${API_BASE}/dashboard-data/${endpoint}`, { credentials: "include" })
      .then(res => res.ok ? res.json() : null)
      .catch(() => null);
  };

  // Track how many sections loaded to hide loader
  let sectionsLoaded = 0;
  const totalSections = 5;
  const checkAllLoaded = () => {
    sectionsLoaded++;
    if (sectionsLoaded >= totalSections && loader) {
      setTimeout(() => {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }, 500);
    }
  };

  // ── Traffic ──────────────────────────────────────────────────────────────
  fetchSection("traffic").then(traffic => {
    if (traffic) {
      if (document.getElementById("totalTraffic"))
        document.getElementById("totalTraffic").innerText = (traffic.total_sessions || 0).toLocaleString();
      const hourly = traffic.hourly_traffic || {};
      const sortedHours = Object.entries(hourly).sort((a, b) => b[1] - a[1]);
      if (document.getElementById("peakHour") && sortedHours.length > 0)
        document.getElementById("peakHour").innerText = sortedHours[0][0] + ":00";
      if (document.getElementById("trafficChart")) {
        new Chart(document.getElementById("trafficChart"), {
          type: "line",
          data: {
            labels: Object.keys(hourly),
            datasets: [{ label: "Page Views", data: Object.values(hourly), borderColor: "#3b82f6", backgroundColor: "rgba(59,130,246,0.1)", fill: true, tension: 0.4 }]
          },
          options: commonOptions
        });
      }
    }
    checkAllLoaded();
  });

  // ── Load ─────────────────────────────────────────────────────────────────
  fetchSection("load").then(load => {
    if (load && document.getElementById("loadChart")) {
      const requests = load.requests_by_hour || {};
      new Chart(document.getElementById("loadChart"), {
        type: "line",
        data: {
          labels: Object.keys(requests),
          datasets: [{ label: "Server Load", data: Object.values(requests), borderColor: "#8b5cf6", backgroundColor: "rgba(139,92,246,0.1)", fill: true, tension: 0.4 }]
        },
        options: commonOptions
      });
    }
    checkAllLoaded();
  });

  // ── Ads ───────────────────────────────────────────────────────────────────
  fetchSection("ads").then(ads => {
    if (ads) {
      if (document.getElementById("ctr"))
        document.getElementById("ctr").innerText = (ads.ctr || 0) + "%";
      if (document.getElementById("adsChart")) {
        const perf = ads.campaign_performance || {};
        new Chart(document.getElementById("adsChart"), {
          type: "bar",
          data: {
            labels: Object.keys(perf),
            datasets: [{ label: "Conversions", data: Object.values(perf), backgroundColor: "#f97316", borderRadius: 6 }]
          },
          options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.05)" } }, x: { grid: { display: false } } } }
        });
      }
    }
    checkAllLoaded();
  });

  // ── Users ─────────────────────────────────────────────────────────────────
  fetchSection("users").then(users => {
    if (users && document.getElementById("userChart")) {
      const buyers = users.buyers || {};
      new Chart(document.getElementById("userChart"), {
        type: "doughnut",
        data: {
          labels: ["One-time", "Repeat"],
          datasets: [{ data: [buyers["One-time"] || 0, buyers["Repeat"] || 0], backgroundColor: ["#f43f5e", "#3b82f6"], borderWidth: 0, hoverOffset: 20 }]
        },
        options: { responsive: true, maintainAspectRatio: false, cutout: "75%", layout: { padding: 30 }, plugins: { legend: { display: true, position: "bottom", labels: { usePointStyle: true, padding: 20, font: { family: "'Poppins', sans-serif", size: 12 } } } } }
      });
    }
    checkAllLoaded();
  });

  // ── Security ──────────────────────────────────────────────────────────────
  fetchSection("security").then(security => {
    if (security) {
      const score = security.security_score || 0;
      const status = score > 80 ? "stable" : score > 50 ? "fine" : score > 30 ? "moderate" : "risk";
      if (typeof updateSystemStatus === "function") updateSystemStatus(status);
      else if (document.getElementById("systemStatus"))
        document.getElementById("systemStatus").innerText = status.toUpperCase();
    }
    checkAllLoaded();
  });

});