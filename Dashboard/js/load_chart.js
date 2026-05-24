document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");

  fetch("http://127.0.0.1:8000/load", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      if (document.getElementById("cpu")) document.getElementById("cpu").innerText = data.avg_cpu_usage + "%";
      if (document.getElementById("memory")) document.getElementById("memory").innerText = data.memory_usage + "%";
      if (document.getElementById("response")) document.getElementById("response").innerText = data.avg_response_time + " ms";
      if (document.getElementById("error")) document.getElementById("error").innerText = data.error_rate + "%";

      const commonOptions = { responsive: true, maintainAspectRatio: false };

      if (document.getElementById("loadHourChart")) {
        new Chart(document.getElementById("loadHourChart"), {
          type: "line",
          data: {
            labels: Object.keys(data.requests_by_hour),
            datasets: [{
              label: "Requests",
              data: Object.values(data.requests_by_hour),
              borderColor: "#8b5cf6",
              tension: 0.4,
              fill: false,
            }],
          },
          options: commonOptions
        });
      }

      if (document.getElementById("requestChart")) {
        new Chart(document.getElementById("requestChart"), {
          type: "line",
          data: {
            labels: Object.keys(data.requests_by_hour),
            datasets: [
              {
                label: "Requests",
                data: Object.values(data.requests_by_hour),
                borderColor: "#8b5cf6",
                tension: 0.4,
                fill: false,
              },
              {
                label: "Errors",
                data: Object.keys(data.requests_by_hour).map(h => data.errors_by_hour[h] || 0),
                borderColor: "#ef4444",
                tension: 0.4,
                fill: false,
              },
            ],
          },
          options: commonOptions
        });
      }

      if (document.getElementById("responseChart")) {
        new Chart(document.getElementById("responseChart"), {
          type: "bar",
          data: {
            labels: Object.keys(data.avg_response_by_endpoint),
            datasets: [
              { label: "Avg Time (ms)", data: Object.values(data.avg_response_by_endpoint), backgroundColor: "#3b82f6" },
              { label: "P95 Time (ms)", data: Object.values(data.p95_response_by_endpoint), backgroundColor: "#06b6d4" },
            ],
          },
          options: commonOptions
        });
      }

      if (document.getElementById("endpointChart")) {
        new Chart(document.getElementById("endpointChart"), {
          type: "bar",
          data: {
            labels: Object.keys(data.top_endpoints),
            datasets: [{ label: "Requests", data: Object.values(data.top_endpoints), backgroundColor: "#10b981" }],
          },
          options: commonOptions
        });
      }

      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    })
    .catch((error) => {
      console.error("Load API error:", error);
      if (loader) loader.classList.add("hidden");
    });
});
