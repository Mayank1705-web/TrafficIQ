document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");

  fetch("http://127.0.0.1:8000/security", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      if (document.getElementById("score")) document.getElementById("score").innerText = data.security_score + "%";
      if (document.getElementById("threats")) document.getElementById("threats").innerText = data.threats_blocked;
      if (document.getElementById("firewall")) document.getElementById("firewall").innerText = data.firewall_status;
      if (document.getElementById("alerts")) document.getElementById("alerts").innerText = data.critical_alerts;

      const commonOptions = { responsive: true, maintainAspectRatio: false };

      if (document.getElementById("statusChart")) {
        new Chart(document.getElementById("statusChart"), {
          type: "bar",
          data: {
            labels: Object.keys(data.status_dist),
            datasets: [{ label: "Requests", data: Object.values(data.status_dist), backgroundColor: "#3b82f6" }],
          },
          options: { ...commonOptions, plugins: { legend: { display: false } } }
        });
      }

      if (document.getElementById("errorChart")) {
        new Chart(document.getElementById("errorChart"), {
          type: "line",
          data: {
            labels: Object.keys(data.error_by_hour),
            datasets: [{ label: "Errors per Hour", data: Object.values(data.error_by_hour), borderColor: "#f97316", tension: 0.4 }],
          },
          options: { ...commonOptions, plugins: { legend: { display: false } } }
        });
      }

      if (document.getElementById("attackChart")) {
        new Chart(document.getElementById("attackChart"), {
          type: "doughnut",
          data: {
            labels: Object.keys(data.attack_types),
            datasets: [{ data: Object.values(data.attack_types), backgroundColor: ["#ef4444", "#f97316", "#3b82f6", "#8b5cf6"] }],
          },
          options: { ...commonOptions, plugins: { legend: { position: "bottom" } } }
        });
      }

      if (document.getElementById("timelineChart")) {
        new Chart(document.getElementById("timelineChart"), {
          type: "line",
          data: {
            labels: Object.keys(data.error_by_hour),
            datasets: [{ label: "Threat Events", data: Object.values(data.error_by_hour), borderColor: "#ef4444", tension: 0.4 }],
          },
          options: { ...commonOptions, plugins: { legend: { display: false } } }
        });
      }

      const container = document.getElementById("activityContainer");
      if (container) {
        container.innerHTML = ""; // Clear existing
        data.activity_log.forEach((item) => {
          let color = item.level === "Critical" ? "red" : (item.level === "High" || item.level === "Medium" ? "orange" : "blue");
          container.innerHTML += `
            <div class="activity-row">
              <div class="activity-left">
                <div class="activity-icon ${color}"><i class="fa-solid fa-triangle-exclamation"></i></div>
                <div><h4>${item.name}</h4><span class="tag ${item.level.toLowerCase()}">${item.level}</span></div>
              </div>
              <div class="activity-right"><h2>${item.count}</h2><p>Incidents</p></div>
            </div>`;
        });
      }

      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    })
    .catch((err) => {
      console.error("Security API error:", err);
      if (loader) loader.classList.add("hidden");
    });
});
