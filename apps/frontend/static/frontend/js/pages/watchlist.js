document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const grid = document.getElementById("watchlistGrid");
  const empty = document.getElementById("watchlistEmpty");

  async function load() {
    grid.innerHTML = "";
    empty.style.display = "none";

    try {
      const response = await Api.get("/api/watchlist/");
      const items = Api.extractArray(response);
      if (!items.length) {
        empty.style.display = "block";
        return;
      }

      items.forEach(item => {
        const latest = item.latest_analysis;
        const prev = item.previous_analysis;
        let scoreDelta = null;
        if (latest && prev) {
          scoreDelta = latest.safety_score - prev.safety_score;
        }

        const card = document.createElement("div");
        card.className = "card watchlist-card";

        const labelCls = latest
          ? (latest.label === "FRAUD" ? "badge-fraud" : latest.label === "LEGIT" ? "badge-legit" : latest.label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown")
          : "badge-unknown";

        const scoreColor = latest
          ? (latest.safety_score > 70 ? "var(--legit)" : latest.safety_score > 40 ? "var(--suspicious)" : "var(--fraud)")
          : "inherit";

        const deltaHtml = scoreDelta !== null
          ? `<span class="score-delta ${scoreDelta > 0 ? 'delta-up' : scoreDelta < 0 ? 'delta-down' : 'delta-flat'}">${scoreDelta > 0 ? '+' : ''}${scoreDelta}</span>`
          : '';

        card.innerHTML = `
          <div class="card-body">
            <div class="flex-wrap items-center justify-between mb-6">
              <div>
                <a href="/apps/${item.app}/" class="link-primary" style="font-weight:600;font-size:1.1rem;">${UI.escapeHtml(item.app_name)}</a>
                <div class="text-small text-muted">${UI.escapeHtml(item.app_developer || "")} ${item.app_category ? '· ' + UI.escapeHtml(item.app_category) : ''}</div>
              </div>
              <button class="btn-danger text-small" data-unwatch="${item.id}" type="button">Unwatch</button>
            </div>
            <div class="watchlist-metrics">
              <div>
                <span class="text-muted text-small">Label</span>
                ${latest ? `<span class="${labelCls}">${UI.escapeHtml(latest.label)}</span>` : '<span class="text-muted">—</span>'}
              </div>
              <div>
                <span class="text-muted text-small">Safety Score</span>
                <span style="font-weight:700;color:${scoreColor}">${latest ? latest.safety_score + '/100' : '—'} ${deltaHtml}</span>
              </div>
              <div>
                <span class="text-muted text-small">Community Reports</span>
                <span>${item.report_count || 0}</span>
              </div>
              <div>
                <span class="text-muted text-small">Watched Since</span>
                <span class="text-small">${new Date(item.added_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        `;
        grid.appendChild(card);
      });

      grid.querySelectorAll("button[data-unwatch]").forEach(btn => {
        btn.addEventListener("click", async () => {
          if (!confirm("Remove from watchlist?")) return;
          try {
            await Api.del(`/api/watchlist/${btn.getAttribute("data-unwatch")}/`);
            await load();
          } catch (err) {
            UI.showAlert(err.message || "Failed to unwatch.");
          }
        });
      });
    } catch (err) {
      UI.showAlert(err.message || "Failed to load watchlist.");
    }
  }

  await load();
});
