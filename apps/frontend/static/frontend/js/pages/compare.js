document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const checkboxHost = document.getElementById("appCheckboxes");
  const btnCompare = document.getElementById("btnCompare");
  const resultsSection = document.getElementById("compareResults");
  const cardsHost = document.getElementById("compareCards");
  const tableSection = document.getElementById("compareTable");
  const tableHead = document.getElementById("compareTableHead");
  const tableBody = document.getElementById("compareTableBody");

  let selectedIds = new Set();

  try {
    const response = await Api.get("/api/apps/");
    const apps = Api.extractArray(response);
    if (!apps.length) {
      checkboxHost.innerHTML = '<p class="text-muted">No apps found. Create apps from the Dashboard first.</p>';
      return;
    }

    apps.forEach(app => {
      const label = document.createElement("label");
      label.className = "compare-checkbox-item";
      label.innerHTML = `
        <input type="checkbox" value="${app.id}" />
        <span class="compare-app-name">${UI.escapeHtml(app.name)}</span>
        <span class="text-small text-muted font-mono">${UI.escapeHtml(app.package_name)}</span>
      `;
      checkboxHost.appendChild(label);

      label.querySelector("input").addEventListener("change", (e) => {
        if (e.target.checked) selectedIds.add(app.id);
        else selectedIds.delete(app.id);
        btnCompare.disabled = selectedIds.size < 2;
      });
    });
  } catch (err) {
    UI.showAlert(err.message || "Failed to load apps.");
  }

  btnCompare.addEventListener("click", async () => {
    if (selectedIds.size < 2) return;
    btnCompare.disabled = true;
    btnCompare.textContent = "Comparing...";

    try {
      const ids = Array.from(selectedIds).join(",");
      const data = await Api.get(`/api/apps/compare/?ids=${ids}`);
      renderComparison(data);
    } catch (err) {
      UI.showAlert(err.message || "Comparison failed.");
    } finally {
      btnCompare.disabled = false;
      btnCompare.textContent = "Compare Selected";
    }
  });

  function labelBadge(label) {
    if (!label) return '<span class="badge-unknown">N/A</span>';
    const cls = label === "FRAUD" ? "badge-fraud" : label === "LEGIT" ? "badge-legit" : label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown";
    return `<span class="${cls}">${UI.escapeHtml(label)}</span>`;
  }

  function scoreColor(score) {
    if (score == null) return "inherit";
    return score > 70 ? "var(--legit)" : score > 40 ? "var(--suspicious)" : "var(--fraud)";
  }

  function renderComparison(apps) {
    resultsSection.style.display = "block";
    cardsHost.innerHTML = "";

    apps.forEach(app => {
      const a = app.analysis || {};
      const health = a.health_scores || {};
      const card = document.createElement("div");
      card.className = "card compare-card";
      card.innerHTML = `
        <div class="card-header">
          <a href="/apps/${app.id}/" class="link-primary">${UI.escapeHtml(app.name)}</a>
        </div>
        <div class="card-body">
          <div class="compare-metric"><span class="text-muted">Developer</span><span>${UI.escapeHtml(app.developer || "—")}</span></div>
          <div class="compare-metric"><span class="text-muted">Category</span><span>${UI.escapeHtml(app.category || "—")}</span></div>
          <div class="compare-metric"><span class="text-muted">Reviews</span><span>${app.review_count}</span></div>
          <div class="compare-metric"><span class="text-muted">Reports</span><span>${app.report_count}</span></div>
          <hr style="border:none;border-top:1px solid var(--border);margin:12px 0;">
          <div class="compare-metric"><span class="text-muted">Label</span>${labelBadge(a.label)}</div>
          <div class="compare-metric"><span class="text-muted">Safety Score</span><span style="font-weight:700;color:${scoreColor(a.safety_score)}">${a.safety_score != null ? a.safety_score + '/100' : '—'}</span></div>
          <div class="compare-metric"><span class="text-muted">Confidence</span><span>${a.confidence != null ? (a.confidence * 100).toFixed(0) + '%' : '—'}</span></div>
          <div class="compare-metric"><span class="text-muted">Privacy Risk</span><span>${a.privacy_risk_score != null ? a.privacy_risk_score + '/100' : '—'}</span></div>
          <div class="compare-metric"><span class="text-muted">Action</span><span class="text-small">${(a.recommendation_action || '—').replace(/_/g, ' ')}</span></div>
          ${Object.keys(health).length ? `
          <hr style="border:none;border-top:1px solid var(--border);margin:12px 0;">
          <div class="text-small text-muted" style="margin-bottom:8px;">Health Scores</div>
          ${['safety','privacy','quality','trust','sentiment'].map(d =>
            `<div class="compare-metric"><span class="text-muted text-small" style="text-transform:capitalize;">${d}</span><span style="color:${scoreColor(health[d])}">${health[d] ?? '—'}</span></div>`
          ).join('')}` : ''}
        </div>
      `;
      cardsHost.appendChild(card);
    });

    // Build metrics table
    if (apps.some(a => a.analysis)) {
      tableSection.style.display = "block";
      tableHead.innerHTML = "<th>Metric</th>" + apps.map(a => `<th>${UI.escapeHtml(a.name)}</th>`).join("");
      const rows = [
        ["Label", apps.map(a => labelBadge(a.analysis?.label))],
        ["Safety Score", apps.map(a => a.analysis ? `<span style="color:${scoreColor(a.analysis.safety_score)};font-weight:700">${a.analysis.safety_score}/100</span>` : "—")],
        ["Privacy Risk", apps.map(a => a.analysis?.privacy_risk_score != null ? a.analysis.privacy_risk_score + "/100" : "—")],
        ["Confidence", apps.map(a => a.analysis?.confidence != null ? (a.analysis.confidence * 100).toFixed(0) + "%" : "—")],
        ["Reviews", apps.map(a => String(a.review_count))],
        ["Community Reports", apps.map(a => String(a.report_count))],
      ];
      tableBody.innerHTML = rows.map(([label, vals]) =>
        `<tr><td class="text-muted">${label}</td>${vals.map(v => `<td>${v}</td>`).join("")}</tr>`
      ).join("");
    }
  }
});
