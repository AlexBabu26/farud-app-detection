document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const name = window.__DEV_NAME__;
  const title = document.getElementById("devTitle");
  const statsHost = document.getElementById("devStats");
  const tableBody = document.querySelector("#devAppsTable tbody");
  const empty = document.getElementById("devEmpty");

  title.textContent = name || "Developer Profile";

  try {
    const data = await Api.get(`/api/insights/developers/${encodeURIComponent(name)}/`);

    function scoreColor(score) {
      if (score == null) return "inherit";
      return score > 70 ? "var(--legit)" : score > 40 ? "var(--suspicious)" : "var(--fraud)";
    }

    statsHost.innerHTML = `
      <div class="stat-card">
        <div class="stat-value">${data.app_count}</div>
        <div class="stat-label">Total Apps</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:${scoreColor(data.avg_safety_score)}">${data.avg_safety_score}</div>
        <div class="stat-label">Avg Safety Score</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" style="color:var(--fraud)">${data.total_reports}</div>
        <div class="stat-label">Community Reports</div>
      </div>
    `;

    if (!data.apps || !data.apps.length) {
      empty.style.display = "block";
      return;
    }

    data.apps.forEach(app => {
      const labelCls = app.latest_label === "FRAUD" ? "badge-fraud" : app.latest_label === "LEGIT" ? "badge-legit" : app.latest_label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><a href="/apps/${app.id}/" class="link-primary">${UI.escapeHtml(app.name)}</a></td>
        <td class="font-mono text-small text-muted">${UI.escapeHtml(app.package_name)}</td>
        <td>${UI.escapeHtml(app.category || "—")}</td>
        <td>${app.review_count}</td>
        <td>${app.latest_label ? `<span class="${labelCls}">${UI.escapeHtml(app.latest_label)}</span>` : '<span class="text-muted">—</span>'}</td>
        <td style="font-weight:700;color:${scoreColor(app.safety_score)}">${app.safety_score != null ? app.safety_score + '/100' : '—'}</td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (err) {
    UI.showAlert(err.message || "Failed to load developer profile.");
  }
});
