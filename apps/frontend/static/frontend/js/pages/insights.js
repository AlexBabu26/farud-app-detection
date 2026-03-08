document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabCategories = document.getElementById("tabCategories");
  const tabDevelopers = document.getElementById("tabDevelopers");
  const categoryGrid = document.getElementById("categoryGrid");
  const categoryEmpty = document.getElementById("categoryEmpty");
  const developerGrid = document.getElementById("developerGrid");
  const developerEmpty = document.getElementById("developerEmpty");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("tab-active"));
      btn.classList.add("tab-active");
      const tab = btn.getAttribute("data-tab");
      tabCategories.style.display = tab === "categories" ? "block" : "none";
      tabDevelopers.style.display = tab === "developers" ? "block" : "none";
    });
  });

  function scoreColor(score) {
    if (score == null || score === 0) return "inherit";
    return score > 70 ? "var(--legit)" : score > 40 ? "var(--suspicious)" : "var(--fraud)";
  }

  function riskLevel(score) {
    if (!score) return "No Data";
    if (score > 70) return "Low Risk";
    if (score > 40) return "Medium Risk";
    return "High Risk";
  }

  // Load categories
  try {
    const cats = await Api.get("/api/insights/categories/");
    if (!cats || !cats.length) {
      categoryEmpty.style.display = "block";
    } else {
      cats.forEach(cat => {
        const card = document.createElement("div");
        card.className = "card insight-card";
        card.innerHTML = `
          <div class="card-body">
            <h3 class="insight-card-title">${UI.escapeHtml(cat.category)}</h3>
            <div class="insight-metrics">
              <div class="insight-metric">
                <span class="insight-metric-val">${cat.app_count}</span>
                <span class="insight-metric-label">Apps</span>
              </div>
              <div class="insight-metric">
                <span class="insight-metric-val" style="color:${scoreColor(cat.avg_safety_score)}">${cat.avg_safety_score}</span>
                <span class="insight-metric-label">Avg Safety</span>
              </div>
              <div class="insight-metric">
                <span class="insight-metric-val" style="color:var(--fraud)">${cat.fraud_app_count}</span>
                <span class="insight-metric-label">Fraud</span>
              </div>
              <div class="insight-metric">
                <span class="insight-metric-val" style="color:var(--suspicious)">${cat.suspicious_app_count}</span>
                <span class="insight-metric-label">Suspicious</span>
              </div>
            </div>
            <div class="insight-risk-bar">
              <div class="insight-risk-fill" style="width:${cat.avg_safety_score}%;background:${scoreColor(cat.avg_safety_score)}"></div>
            </div>
            <div class="text-small text-muted" style="margin-top:8px;">${riskLevel(cat.avg_safety_score)}</div>
          </div>
        `;
        categoryGrid.appendChild(card);
      });
    }
  } catch (err) {
    UI.showAlert(err.message || "Failed to load category insights.");
  }

  // Load developers
  try {
    const devs = await Api.get("/api/insights/developers/");
    if (!devs || !devs.length) {
      developerEmpty.style.display = "block";
    } else {
      devs.forEach(dev => {
        const card = document.createElement("div");
        card.className = "card insight-card";
        card.innerHTML = `
          <div class="card-body">
            <h3 class="insight-card-title">
              <a href="/developer/${encodeURIComponent(dev.developer)}/" class="link-primary">${UI.escapeHtml(dev.developer)}</a>
            </h3>
            <div class="insight-metrics">
              <div class="insight-metric">
                <span class="insight-metric-val">${dev.app_count}</span>
                <span class="insight-metric-label">Apps</span>
              </div>
              <div class="insight-metric">
                <span class="insight-metric-val" style="color:${scoreColor(dev.avg_safety_score)}">${dev.avg_safety_score}</span>
                <span class="insight-metric-label">Avg Safety</span>
              </div>
              <div class="insight-metric">
                <span class="insight-metric-val" style="color:var(--fraud)">${dev.fraud_app_count}</span>
                <span class="insight-metric-label">Fraud Apps</span>
              </div>
            </div>
            <div class="insight-risk-bar">
              <div class="insight-risk-fill" style="width:${dev.avg_safety_score}%;background:${scoreColor(dev.avg_safety_score)}"></div>
            </div>
          </div>
        `;
        developerGrid.appendChild(card);
      });
    }
  } catch (err) {
    UI.showAlert(err.message || "Failed to load developer insights.");
  }
});
