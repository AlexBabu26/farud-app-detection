document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const runId = window.__RUN_ID__;
  const host = document.getElementById("runHost");
  const btnExport = document.getElementById("btnExport");

  // Feature 10: Export link
  btnExport.href = `/api/analysis/${runId}/export/`;

  try {
    const run = await Api.get(`/api/analysis/${runId}/`);

    let parsed = null;
    try { parsed = run.llm_json ? JSON.parse(run.llm_json) : null; } catch {}
    const signals = parsed?.key_signals || [];

    const label = (run.llm_label || "").toUpperCase();
    const labelCls = label === "FRAUD" ? "badge-fraud" : label === "LEGIT" ? "badge-legit" : label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown";
    const conf = (run.llm_confidence ?? 0) * 100;

    const safetyScore = run.safety_score || parsed?.safety_score || 0;
    const addictionRisk = parsed?.addiction_risk || "UNKNOWN";
    const privacyConcerns = parsed?.privacy_concerns || [];
    const topBugs = parsed?.top_bugs || [];
    const featureRequests = parsed?.feature_requests || [];
    const sentiment = parsed?.sentiment_breakdown || { anger: 0, joy: 0, fear: 0, sadness: 0 };

    // Feature 6: Privacy Assessment
    const privacyRisk = parsed?.privacy_risk_score ?? 0;
    const policyReadability = parsed?.privacy_policy_readability || "MISSING";
    const dataSharingConcerns = parsed?.data_sharing_concerns || [];

    // Feature 7: Safety Recommendations
    const safetyRec = parsed?.safety_recommendation || "";
    const recAction = parsed?.recommendation_action || "";

    // Feature 11: Health Scores
    const health = parsed?.health_scores || {};

    function scoreColor(s) { return s > 70 ? "var(--legit)" : s > 40 ? "var(--suspicious)" : "var(--fraud)"; }
    function listHtml(items, emptyMsg) {
      if (!items.length) return `<p class="text-muted text-small">${emptyMsg}</p>`;
      return `<ul style="padding-left:1.25em;font-size:0.9375rem;">${items.map(i => `<li>${UI.escapeHtml(i)}</li>`).join("")}</ul>`;
    }

    const recBannerCls = recAction === "RECOMMEND_UNINSTALL" ? "rec-recommend-uninstall"
      : recAction === "PROCEED_WITH_CAUTION" ? "rec-proceed-with-caution"
      : "rec-safe-to-install";

    host.className = "";
    host.innerHTML = `
      ${safetyRec ? `
      <div class="recommendation-banner mb-6 ${recBannerCls}">
        <div class="rec-action-badge">${(recAction || "").replace(/_/g, " ")}</div>
        <p class="rec-text">${UI.escapeHtml(safetyRec)}</p>
      </div>` : ""}

      <div class="grid-2" style="gap:24px;margin-bottom:24px;">
        <div class="card">
          <div class="card-header">Overview</div>
          <div class="card-body">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <span class="text-muted">Fraud Risk</span>
              <span class="${labelCls}">${UI.escapeHtml(run.llm_label)}</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <span class="text-muted">Confidence</span>
              <span style="font-weight:700">${conf.toFixed(0)}%</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <span class="text-muted">Safety Score</span>
              <span style="font-weight:700;color:${scoreColor(safetyScore)}">${safetyScore}/100</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;">
              <span class="text-muted">Addiction Risk</span>
              <span class="${addictionRisk === 'HIGH' ? 'badge-fraud' : addictionRisk === 'MEDIUM' ? 'badge-suspicious' : 'badge-legit'}">${UI.escapeHtml(addictionRisk)}</span>
            </div>
          </div>
        </div>
        <div class="card">
          <div class="card-header">Sentiment Breakdown</div>
          <div class="card-body">
            <div style="display:flex;gap:12px;flex-direction:column;">
              ${Object.entries(sentiment).map(([emotion, score]) => `
                <div>
                  <div style="display:flex;justify-content:space-between;font-size:0.875rem;margin-bottom:4px;">
                    <span style="text-transform:capitalize;">${emotion}</span>
                    <span>${score}%</span>
                  </div>
                  <div style="background:var(--bg-page);height:8px;border-radius:4px;overflow:hidden;">
                    <div style="width:${score}%;height:100%;background:${
                      emotion === 'joy' ? 'var(--legit)' : emotion === 'anger' ? 'var(--fraud)' : emotion === 'fear' ? 'var(--suspicious)' : 'var(--primary)'
                    }"></div>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      </div>

      ${Object.keys(health).length ? `
      <div class="card" style="margin-bottom:24px;">
        <div class="card-header">App Health Score</div>
        <div class="card-body" style="display:flex;flex-wrap:wrap;align-items:center;gap:32px;">
          <canvas id="detailRadar" width="260" height="260" style="flex-shrink:0;"></canvas>
          <div style="flex:1;min-width:200px;">
            ${["safety","privacy","quality","trust","sentiment"].map(d => {
              const v = health[d] || 0;
              return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <span style="width:80px;font-size:0.875rem;text-transform:capitalize;color:var(--text-muted);">${d}</span>
                <div style="flex:1;height:8px;background:var(--bg-page);border-radius:4px;overflow:hidden;">
                  <div style="width:${v}%;height:100%;background:${scoreColor(v)};border-radius:4px;"></div>
                </div>
                <span style="width:32px;font-weight:700;font-size:0.875rem;color:${scoreColor(v)}">${v}</span>
              </div>`;
            }).join("")}
          </div>
        </div>
      </div>` : ""}

      <div class="grid-2" style="gap:24px;margin-bottom:24px;">
        <div class="card">
          <div class="card-header">Privacy Assessment</div>
          <div class="card-body">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
              <span class="text-muted">Privacy Risk Score</span>
              <span style="font-weight:700;color:${privacyRisk > 70 ? 'var(--fraud)' : privacyRisk > 40 ? 'var(--suspicious)' : 'var(--legit)'}">${privacyRisk}/100</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
              <span class="text-muted">Policy Readability</span>
              <span class="${policyReadability === 'GOOD' ? 'badge-legit' : policyReadability === 'FAIR' ? 'badge-suspicious' : 'badge-fraud'}">${UI.escapeHtml(policyReadability)}</span>
            </div>
            <h4 class="text-small text-muted" style="text-transform:uppercase;margin-bottom:8px;">Data Sharing Concerns</h4>
            ${listHtml(dataSharingConcerns, "No data sharing concerns detected.")}
            <h4 class="text-small text-muted" style="text-transform:uppercase;margin-top:16px;margin-bottom:8px;">Privacy Concerns</h4>
            ${listHtml(privacyConcerns, "No specific privacy concerns flagged.")}
          </div>
        </div>
        <div class="card">
          <div class="card-header">Product Intelligence</div>
          <div class="card-body">
            <h4 class="text-small text-muted" style="text-transform:uppercase;margin-bottom:8px;">Top Bugs</h4>
            ${listHtml(topBugs, "No bugs detected.")}
            <h4 class="text-small text-muted" style="text-transform:uppercase;margin-top:16px;margin-bottom:8px;">Feature Requests</h4>
            ${listHtml(featureRequests, "No feature requests detected.")}
          </div>
        </div>
      </div>

      <div class="grid-2" style="gap:24px;margin-bottom:24px;">
        <div class="card">
          <div class="card-header">Safety & Compliance</div>
          <div class="card-body">
            <h4 class="text-small text-muted" style="text-transform:uppercase;margin-bottom:8px;">Key Signals</h4>
            ${listHtml(signals, "No key signals detected.")}
          </div>
        </div>
        <div class="card">
          <div class="card-header">Analysis Rationale</div>
          <div class="card-body">
            <p class="text-muted" style="font-size:0.9375rem;line-height:1.6;">${UI.escapeHtml(run.llm_rationale || "No rationale provided.")}</p>
            ${run.error_message ? `<div class="alert alert-danger" style="margin-top:16px;">${UI.escapeHtml(run.error_message)}</div>` : ""}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">Debug</div>
        <div class="card-body">
          <details>
            <summary class="text-small text-muted" style="cursor:pointer;">Raw Response</summary>
            <pre style="margin-top:8px;padding:16px;background:var(--bg-page);border-radius:8px;font-size:0.75rem;overflow-x:auto;white-space:pre-wrap;">${UI.escapeHtml(run.raw_response || "")}</pre>
          </details>
        </div>
      </div>
    `;

    // Draw radar chart for health scores
    if (Object.keys(health).length) {
      const canvas = document.getElementById("detailRadar");
      if (canvas) drawRadarChart(canvas, health);
    }
  } catch (err) {
    host.className = "text-muted";
    host.textContent = "Failed to load analysis detail.";
    UI.showAlert(err.message || "Failed to load analysis detail.");
  }

  function drawRadarChart(canvas, scores) {
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2, R = Math.min(W, H) / 2 - 28;
    const dims = ["safety", "privacy", "quality", "trust", "sentiment"];
    const N = dims.length;
    ctx.clearRect(0, 0, W, H);

    for (let ring = 1; ring <= 5; ring++) {
      const r = R * ring / 5;
      ctx.beginPath();
      for (let i = 0; i <= N; i++) {
        const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
        const x = cx + r * Math.cos(angle), y = cy + r * Math.sin(angle);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "#e0e0e0";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    for (let i = 0; i < N; i++) {
      const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + R * Math.cos(angle), cy + R * Math.sin(angle));
      ctx.strokeStyle = "#e0e0e0";
      ctx.stroke();
    }

    ctx.beginPath();
    for (let i = 0; i <= N; i++) {
      const idx = i % N;
      const val = (scores[dims[idx]] || 0) / 100;
      const angle = (Math.PI * 2 * idx) / N - Math.PI / 2;
      const x = cx + R * val * Math.cos(angle), y = cy + R * val * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.fillStyle = "rgba(30, 78, 66, 0.2)";
    ctx.fill();
    ctx.strokeStyle = "#1E4E42";
    ctx.lineWidth = 2;
    ctx.stroke();

    for (let i = 0; i < N; i++) {
      const val = (scores[dims[i]] || 0) / 100;
      const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
      const x = cx + R * val * Math.cos(angle), y = cy + R * val * Math.sin(angle);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#1E4E42";
      ctx.fill();

      const lx = cx + (R + 16) * Math.cos(angle), ly = cy + (R + 16) * Math.sin(angle);
      ctx.font = "11px Inter, sans-serif";
      ctx.fillStyle = "#4F4F4F";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(dims[i].charAt(0).toUpperCase() + dims[i].slice(1), lx, ly);
    }
  }
});
