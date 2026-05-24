document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");

  fetch(`${API_BASE}/traffic`, { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("sessions").innerText = data.total_sessions.toLocaleString();
      document.getElementById("duration").innerText = data.avg_session_duration + " sec";
      document.getElementById("pages").innerText = data.pages_per_session;
      document.getElementById("bounce").innerText = data.bounce_rate + "%";

      const commonOptions = { 
        responsive: true, 
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: false } }
        }
      };

      new Chart(document.getElementById("hourChart"), {
        type: "line",
        data: {
          labels: Object.keys(data.hourly_traffic),
          datasets: [{
            label: "Page Views",
            data: Object.values(data.hourly_traffic),
            borderColor: "#3b82f6",
            tension: 0.4,
            fill: false,
          }],
        },
        options: commonOptions
      });

      new Chart(document.getElementById("monthChart"), {
        type: "bar",
        data: {
          labels: Object.keys(data.monthly_traffic),
          datasets: [{
            label: "Monthly Traffic",
            data: Object.values(data.monthly_traffic),
            backgroundColor: "#8b5cf6",
          }],
        },
        options: commonOptions
      });

      new Chart(document.getElementById("sourceChart"), {
        type: "doughnut",
        data: {
          labels: Object.keys(data.traffic_sources),
          datasets: [{
            data: Object.values(data.traffic_sources),
            backgroundColor: ["#3b82f6", "#8b5cf6", "#f97316", "#10b981"],
          }],
        },
        options: { ...commonOptions, plugins: { legend: { position: "bottom" } } }
      });

      new Chart(document.getElementById("geoChart"), {
        type: "bar",
        data: {
          labels: Object.keys(data.geo_distribution),
          datasets: [{
            label: "Visitors",
            data: Object.values(data.geo_distribution),
            backgroundColor: "#10b981",
            borderRadius: 6,
          }],
        },
        options: { ...commonOptions, plugins: { legend: { position: "bottom" } } }
      });

      // Hide loader and de-blur
      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    })
    .catch((error) => {
      console.error("TrafficIQ API error:", error);
      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    });
});
