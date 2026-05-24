document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");
  fetch("http://127.0.0.1:8000/users", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      /* KPI */
      if (document.getElementById("orders")) document.getElementById("orders").innerText = (data.total_orders || 0).toLocaleString();
      if (document.getElementById("aov")) document.getElementById("aov").innerText = "$" + (data.avg_order_value || 0);
      if (document.getElementById("retention")) document.getElementById("retention").innerText = (data.retention_rate || 0) + "%";
      if (document.getElementById("rating")) document.getElementById("rating").innerText = (data.avg_rating || 0);

      /* HOURLY */
      const hourly = data.hourly || {};
      new Chart(document.getElementById("hourChart"), {
        type: "line",
        data: {
          labels: Object.keys(hourly),
          datasets: [{
            label: "Purchases",
            data: Object.values(hourly),
            borderColor: "#10b981",
            backgroundColor: "rgba(16, 185, 129, 0.1)",
            fill: true,
            tension: 0.4,
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      });

      /* CATEGORY */
      const category = data.category || {};
      new Chart(document.getElementById("categoryChart"), {
        type: "bar",
        data: {
          labels: Object.keys(category),
          datasets: [{
            label: "Revenue",
            data: Object.values(category),
            backgroundColor: "#3b82f6",
            borderRadius: 6
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      });

      /* SEGMENTS */
      const segments = data.segments || {};
      new Chart(document.getElementById("segmentChart"), {
        type: "doughnut",
        data: {
          labels: Object.keys(segments),
          datasets: [{
            data: Object.values(segments),
            backgroundColor: ["#3b82f6", "#8b5cf6", "#f97316", "#10b981"],
            borderWidth: 0
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: "70%",
          plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 20 } } },
        },
      });

      /* BUYERS */
      const buyers = data.buyers || {};
      new Chart(document.getElementById("buyerChart"), {
        type: "pie",
        data: {
          labels: Object.keys(buyers),
          datasets: [{
            data: Object.values(buyers),
            backgroundColor: ["#10b981", "#f97316"],
            borderWidth: 0
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom", labels: { usePointStyle: true, padding: 20 } } },
        },
      });

      /* JOURNEY */
      const journey = data.user_journey || data.journey || {};
      new Chart(document.getElementById("journeyChart"), {
        type: "bar",
        data: {
          labels: ["Home", "Product", "Cart", "Checkout", "Purchase"],
          datasets: [{
            label: "Users",
            data: [
              journey.home || 0,
              journey.product || 0,
              journey.cart || 0,
              journey.checkout || 0,
              journey.purchase || 0
            ],
            backgroundColor: ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6"],
            borderRadius: 6
          }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
      });

      // Hide loader
      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    })
    .catch((err) => {
      console.error("Error loading users data:", err);
      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    });
});
