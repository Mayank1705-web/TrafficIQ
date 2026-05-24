document.addEventListener("DOMContentLoaded", function () {
  const loader = document.getElementById("loader");

  fetch("http://127.0.0.1:8000/ads", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      if (document.getElementById("impressions")) document.getElementById("impressions").innerText = data.total_impressions.toLocaleString();
      if (document.getElementById("ctr")) document.getElementById("ctr").innerText = data.ctr + "%";
      if (document.getElementById("cpc")) document.getElementById("cpc").innerText = "$" + data.cpc;
      if (document.getElementById("roas")) document.getElementById("roas").innerText = data.roas + "x";

      const commonOptions = { responsive: true, maintainAspectRatio: false };

      if (document.getElementById("campaignChart")) {
        new Chart(document.getElementById("campaignChart"), {
          type: "bar",
          data: {
            labels: Object.keys(data.campaign_performance),
            datasets: [{ label: "Conversions", data: Object.values(data.campaign_performance), backgroundColor: "#f97316" }],
          },
          options: commonOptions,
        });
      }

      if (document.getElementById("ctrChart")) {
        new Chart(document.getElementById("ctrChart"), {
          type: "line",
          data: {
            labels: Object.keys(data.ctr_trend),
            datasets: [
              { label: "CTR %", data: Object.values(data.ctr_trend), borderColor: "#8b5cf6", tension: 0.4 },
              { label: "ROAS", data: Object.values(data.roas_trend), borderColor: "#10b981", tension: 0.4 },
            ],
          },
          options: commonOptions,
        });
      }

      if (document.getElementById("adFormatChart")) {
        new Chart(document.getElementById("adFormatChart"), {
          type: "doughnut",
          data: {
            labels: Object.keys(data.ad_formats),
            datasets: [{ data: Object.values(data.ad_formats), backgroundColor: ["#3b82f6", "#8b5cf6", "#f97316", "#10b981"] }],
          },
          options: { ...commonOptions, plugins: { legend: { position: "bottom" } } },
        });
      }

      /* FUNNEL DATA */
      if (document.getElementById("funnel_impressions")) document.getElementById("funnel_impressions").innerText = data.funnel.impressions.toLocaleString();
      if (document.getElementById("funnel_clicks")) document.getElementById("funnel_clicks").innerText = data.funnel.clicks.toLocaleString();
      if (document.getElementById("funnel_landing")) document.getElementById("funnel_landing").innerText = data.funnel.landing.toLocaleString();
      if (document.getElementById("funnel_cart")) document.getElementById("funnel_cart").innerText = data.funnel.add_to_cart.toLocaleString();
      if (document.getElementById("funnel_checkout")) document.getElementById("funnel_checkout").innerText = data.funnel.checkout.toLocaleString();
      if (document.getElementById("funnel_purchase")) document.getElementById("funnel_purchase").innerText = data.funnel.purchase.toLocaleString();

      function loss(prev, curr) { return (((prev - curr) / prev) * 100).toFixed(1); }
      function pct(v, t) { return ((v / t) * 100).toFixed(1); }

      if (document.getElementById("loss_clicks")) document.getElementById("loss_clicks").innerText = `(-${loss(data.funnel.impressions, data.funnel.clicks)}%)`;
      if (document.getElementById("loss_landing")) document.getElementById("loss_landing").innerText = `(-${loss(data.funnel.clicks, data.funnel.landing)}%)`;
      if (document.getElementById("loss_cart")) document.getElementById("loss_cart").innerText = `(-${loss(data.funnel.landing, data.funnel.add_to_cart)}%)`;
      if (document.getElementById("loss_checkout")) document.getElementById("loss_checkout").innerText = `(-${loss(data.funnel.add_to_cart, data.funnel.checkout)}%)`;
      if (document.getElementById("loss_purchase")) document.getElementById("loss_purchase").innerText = `(-${loss(data.funnel.checkout, data.funnel.purchase)}%)`;

      if (document.getElementById("pct_impressions")) document.getElementById("pct_impressions").innerText = "100% of total";
      if (document.getElementById("pct_clicks")) document.getElementById("pct_clicks").innerText = pct(data.funnel.clicks, data.funnel.impressions) + "% of total";
      if (document.getElementById("pct_landing")) document.getElementById("pct_landing").innerText = pct(data.funnel.landing, data.funnel.impressions) + "% of total";
      if (document.getElementById("pct_cart")) document.getElementById("pct_cart").innerText = pct(data.funnel.add_to_cart, data.funnel.impressions) + "% of total";
      if (document.getElementById("pct_checkout")) document.getElementById("pct_checkout").innerText = pct(data.funnel.checkout, data.funnel.impressions) + "% of total";
      if (document.getElementById("pct_purchase")) document.getElementById("pct_purchase").innerText = pct(data.funnel.purchase, data.funnel.impressions) + "% of total";

      if (loader) {
        loader.classList.add("hidden");
        const wrapper = document.querySelector(".middle-wrapper");
        if (wrapper) wrapper.classList.remove("is-loading");
      }
    })
    .catch((error) => {
      console.error("Ads API error:", error);
      if (loader) loader.classList.add("hidden");
    });
});
