document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const appId = window.__APP_ID__;
  const appTitle = document.getElementById("appTitle");
  const appSubtitle = document.getElementById("appSubtitle");
  const reviewsBody = document.querySelector("#reviewsTable tbody");
  const reviewsEmpty = document.getElementById("reviewsEmpty");
  const btnRefreshReviews = document.getElementById("btnRefreshReviews");
  const reviewsPager = document.getElementById("reviewsPager");
  const reviewsPageSizeSel = document.getElementById("reviewsPageSize");
  const reviewsPrevBtn = document.getElementById("reviewsPrev");
  const reviewsNextBtn = document.getElementById("reviewsNext");
  const reviewsPageInfo = document.getElementById("reviewsPageInfo");
  const addReviewForm = document.getElementById("addReviewForm");
  const bulkJson = document.getElementById("bulkJson");
  const btnBulkUpload = document.getElementById("btnBulkUpload");
  const btnRunAnalysis = document.getElementById("btnRunAnalysis");
  const maxReviewsInput = document.getElementById("maxReviewsInput");
  const analysisProgress = document.getElementById("analysisProgress");
  const analysisProgressText = document.getElementById("analysisProgressText");
  const latestHost = document.getElementById("latestAnalysisHost");
  const kpiSection = document.getElementById("kpiSection");
  const kpiReviews = document.getElementById("kpiReviews");
  const kpiFraud = document.getElementById("kpiFraud");
  const kpiSentiment = document.getElementById("kpiSentiment");
  const kpiPrivacy = document.getElementById("kpiPrivacy");
  const btnWatchToggle = document.getElementById("btnWatchToggle");
  const btnReportApp = document.getElementById("btnReportApp");
  const reportModal = document.getElementById("reportModal");
  const reportModalForm = document.getElementById("reportModalForm");
  const closeReportModal = document.getElementById("closeReportModal");
  const recBanner = document.getElementById("recommendationBanner");
  const recActionBadge = document.getElementById("recActionBadge");
  const recText = document.getElementById("recText");
  const healthSection = document.getElementById("healthScoreSection");
  const trendSection = document.getElementById("trendSection");

  let allReviews = [];
  let reviewsPage = 1;
  let reviewsPageSize = 10;

  function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }
  function getTotalPages(total, size) { return Math.max(1, Math.ceil(total / size)); }
  function slicePage(arr, page, size) { const s = (page - 1) * size; return arr.slice(s, s + size); }

  function sentimentFromRating(rating) {
    if (rating == null) return { label: "—", cls: "badge-neutral" };
    const n = Number(rating);
    if (n <= 2) return { label: "Negative", cls: "badge-fraud" };
    if (n <= 3) return { label: "Neutral", cls: "badge-suspicious" };
    return { label: "Positive", cls: "badge-legit" };
  }

  function renderReviewsTable() {
    reviewsBody.innerHTML = "";
    reviewsEmpty.style.display = "none";
    reviewsPager.style.display = "none";
    const total = allReviews.length;
    if (total === 0) { reviewsEmpty.style.display = "block"; return; }
    const totalPages = getTotalPages(total, reviewsPageSize);
    reviewsPage = clamp(reviewsPage, 1, totalPages);
    const items = slicePage(allReviews, reviewsPage, reviewsPageSize);

    items.forEach(r => {
      const sent = sentimentFromRating(r.rating);
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.rating ?? "—"}</td>
        <td><span class="${sent.cls}">${sent.label}</span></td>
        <td style="max-width:240px;">${UI.escapeHtml((r.text || "").slice(0, 120))}${(r.text || "").length > 120 ? "…" : ""}</td>
        <td class="font-mono text-small text-muted">${UI.escapeHtml(r.author || "—")}</td>
        <td class="text-small text-muted">${new Date(r.created_at).toLocaleString()}</td>
        <td class="col-action"><button class="btn-danger" data-del="${r.id}" type="button">Delete</button></td>
      `;
      reviewsBody.appendChild(tr);
    });

    reviewsBody.querySelectorAll("button[data-del]").forEach(btn => {
      btn.addEventListener("click", async () => {
        if (!confirm("Delete this review?")) return;
        try { await Api.del(`/api/reviews/${btn.getAttribute("data-del")}/`); await loadReviews(); }
        catch (err) { UI.showAlert(err.message || "Delete failed."); }
      });
    });
    reviewsPager.style.display = "flex";
    reviewsPageInfo.textContent = `Page ${reviewsPage} of ${totalPages} (${total} reviews)`;
    reviewsPrevBtn.disabled = reviewsPage <= 1;
    reviewsNextBtn.disabled = reviewsPage >= totalPages;
  }

  async function loadApp() {
    const app = await Api.get(`/api/apps/${appId}/`);
    appTitle.textContent = app.name;
    appSubtitle.textContent = [app.package_name, app.developer].filter(Boolean).join(" · ");
  }

  async function loadReviews() {
    reviewsBody.innerHTML = "";
    reviewsEmpty.style.display = "none";
    reviewsPager.style.display = "none";
    const response = await Api.get(`/api/reviews/?app=${appId}`);
    allReviews = Api.extractArray(response);
    renderReviewsTable();
  }

  function updateKpi(run, parsed, reviewCount) {
    if (!run || !kpiSection) return;
    kpiSection.style.display = "grid";
    kpiReviews.textContent = reviewCount ?? "—";
    const conf = (run.llm_confidence ?? 0) * 100;
    const label = (run.llm_label || "").toUpperCase();
    kpiFraud.textContent = label === "FRAUD" ? conf.toFixed(0) + "%" : "0%";
    kpiFraud.className = "stat-value " + (label === "FRAUD" ? "text-fraud" : "");
    if (label !== "FRAUD") kpiFraud.style.color = "var(--primary)"; else kpiFraud.style.color = "";
    kpiSentiment.textContent = label || "—";
    kpiSentiment.className = "stat-value " + (label === "FRAUD" ? "text-fraud" : label === "LEGIT" ? "text-legit" : label === "SUSPICIOUS" ? "text-suspicious" : "text-muted");

    const privacyRisk = parsed?.privacy_risk_score;
    if (privacyRisk != null) {
      kpiPrivacy.textContent = privacyRisk + "/100";
      kpiPrivacy.style.color = privacyRisk > 70 ? "var(--fraud)" : privacyRisk > 40 ? "var(--suspicious)" : "var(--legit)";
    }

    // Safety Recommendation Banner (Feature 7)
    const recAction = parsed?.recommendation_action;
    const recMsg = parsed?.safety_recommendation;
    if (recAction && recMsg) {
      recBanner.style.display = "flex";
      recBanner.className = "recommendation-banner mb-6 rec-" + recAction.toLowerCase().replace(/_/g, "-");
      recActionBadge.textContent = recAction.replace(/_/g, " ");
      recText.textContent = recMsg;
    }

    // Health Score Radar Chart (Feature 11)
    const health = parsed?.health_scores;
    if (health && Object.keys(health).length) {
      healthSection.style.display = "block";
      drawRadarChart(document.getElementById("healthRadar"), health);
      const list = document.getElementById("healthScoresList");
      list.innerHTML = ["safety", "privacy", "quality", "trust", "sentiment"].map(d => {
        const val = health[d] || 0;
        const color = val > 70 ? "var(--legit)" : val > 40 ? "var(--suspicious)" : "var(--fraud)";
        return `<div class="health-score-row">
          <span class="health-dim-label">${d.charAt(0).toUpperCase() + d.slice(1)}</span>
          <div class="health-bar-track"><div class="health-bar-fill" style="width:${val}%;background:${color}"></div></div>
          <span class="health-dim-val" style="color:${color}">${val}</span>
        </div>`;
      }).join("");
    }
  }

  // Feature 3: Trend Timeline
  async function loadTrends() {
    try {
      const data = await Api.get(`/api/analysis/trends/${appId}/`);
      if (!data || data.length < 2) return;
      trendSection.style.display = "block";
      drawTrendChart(document.getElementById("trendChart"), data);
    } catch {}
  }

  async function loadLatestAnalysis() {
    latestHost.className = "text-muted";
    latestHost.textContent = "Loading...";
    const response = await Api.get(`/api/analysis/?app=${appId}`);
    const runs = Api.extractArray(response);
    if (!runs || runs.length === 0) {
      latestHost.className = "text-muted";
      latestHost.textContent = "No analysis run yet.";
      if (kpiSection) kpiSection.style.display = "grid";
      return;
    }
    const run = runs[0];
    let parsed = null;
    try { parsed = run.llm_json ? JSON.parse(run.llm_json) : null; } catch {}
    const signals = parsed?.key_signals || [];
    const label = (run.llm_label || "").toUpperCase();
    const labelCls = label === "FRAUD" ? "badge-fraud" : label === "LEGIT" ? "badge-legit" : label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown";

    latestHost.className = "";
    latestHost.innerHTML = `
      <div class="latest-analysis-block">
        <div><strong>Status:</strong> ${UI.escapeHtml(run.status)}</div>
        <div><strong>Label:</strong> <span class="${labelCls}">${UI.escapeHtml(run.llm_label)}</span> (confidence ${(run.llm_confidence ?? 0).toFixed(2)})</div>
        <div><strong>Rationale:</strong><br><span class="rationale-text">${UI.escapeHtml(run.llm_rationale || "—")}</span></div>
        ${signals.length ? `<div class="key-signals"><strong>Key signals:</strong><ul>${signals.map(s => `<li>${UI.escapeHtml(s)}</li>`).join("")}</ul></div>` : ""}
        <a class="link-primary" href="/analysis/${run.id}/" style="display:inline-block;margin-top:12px;">Open detail</a>
      </div>
    `;
    updateKpi(run, parsed, allReviews.length);
  }

  // Feature 2: Watchlist Toggle
  async function loadWatchState() {
    try {
      const res = await Api.get(`/api/watchlist/check/${appId}/`);
      btnWatchToggle.textContent = res.watched ? "Unwatch" : "Watch";
      btnWatchToggle.className = res.watched ? "btn-secondary btn-watched" : "btn-secondary";
    } catch {}
  }

  btnWatchToggle.addEventListener("click", async () => {
    try {
      const res = await Api.post("/api/watchlist/toggle/", { app_id: appId });
      btnWatchToggle.textContent = res.watched ? "Unwatch" : "Watch";
      btnWatchToggle.className = res.watched ? "btn-secondary btn-watched" : "btn-secondary";
      UI.showAlert(res.watched ? "Added to watchlist." : "Removed from watchlist.", "success", 3000);
    } catch (err) { UI.showAlert(err.message || "Failed."); }
  });

  // Feature 8: Report Modal
  btnReportApp.addEventListener("click", () => { reportModal.style.display = "flex"; });
  closeReportModal.addEventListener("click", () => { reportModal.style.display = "none"; });
  reportModal.addEventListener("click", (e) => { if (e.target === reportModal) reportModal.style.display = "none"; });

  reportModalForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(reportModalForm);
    try {
      await Api.post("/api/reports/", { app: appId, reason: fd.get("reason"), description: fd.get("description") });
      reportModal.style.display = "none";
      reportModalForm.reset();
      UI.showAlert("Report submitted. Thank you!", "success", 4000);
    } catch (err) { UI.showAlert(err.message || "Report failed."); }
  });

  addReviewForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(addReviewForm);
    const dt = fd.get("review_date");
    const payload = {
      app: appId,
      text: fd.get("text"),
      rating: fd.get("rating") ? Number(fd.get("rating")) : null,
      author: fd.get("author") || null,
      source: fd.get("source") || null,
      review_date: dt ? new Date(dt).toISOString() : null,
    };
    try {
      await Api.post("/api/reviews/", payload);
      addReviewForm.reset();
      reviewsPage = 1;
      await loadReviews();
      await loadLatestAnalysis();
    } catch (err) { UI.showAlert(err.message || "Add review failed."); }
  });

  btnBulkUpload.addEventListener("click", async () => {
    let reviews;
    try {
      reviews = JSON.parse(bulkJson.value || "[]");
      if (!Array.isArray(reviews) || reviews.length === 0) { UI.showAlert("Bulk JSON must be a non-empty JSON array."); return; }
    } catch { UI.showAlert("Invalid JSON."); return; }
    try {
      await Api.post("/api/reviews/bulk/", { app_id: appId, reviews });
      UI.showAlert("Bulk upload successful.", "success", 4000);
      bulkJson.value = "";
      reviewsPage = 1;
      await loadReviews();
    } catch (err) { UI.showAlert(err.message || "Bulk upload failed."); }
  });

  btnRefreshReviews.addEventListener("click", async () => {
    try { await loadReviews(); await loadLatestAnalysis(); }
    catch (err) { UI.showAlert(err.message || "Failed to refresh."); }
  });

  reviewsPageSizeSel.addEventListener("change", () => {
    reviewsPageSize = Math.min(100, Math.max(10, Number(reviewsPageSizeSel.value) || 10));
    reviewsPage = 1;
    renderReviewsTable();
  });
  reviewsPrevBtn.addEventListener("click", () => { reviewsPage = Math.max(1, reviewsPage - 1); renderReviewsTable(); });
  reviewsNextBtn.addEventListener("click", () => {
    reviewsPage = Math.min(getTotalPages(allReviews.length, reviewsPageSize), reviewsPage + 1);
    renderReviewsTable();
  });

  function showAnalysisProgress(text) { analysisProgressText.textContent = text || "Running analysis..."; analysisProgress.style.display = "block"; }
  function hideAnalysisProgress() { analysisProgress.style.display = "none"; }
  function getMaxReviews() { return clamp(Number(maxReviewsInput.value || 200), 1, 2000); }

  btnRunAnalysis.addEventListener("click", async () => {
    try {
      btnRunAnalysis.disabled = true;
      maxReviewsInput.disabled = true;
      const maxReviews = getMaxReviews();
      maxReviewsInput.value = maxReviews;
      const steps = ["Preparing request...", "Collecting recent reviews...", "Contacting analysis model...", "Waiting for classification...", "Saving results..."];
      let i = 0;
      const timer = setInterval(() => { i = Math.min(steps.length - 1, i + 1); showAnalysisProgress(steps[i]); }, 1200);
      const run = await Api.post("/api/analysis/run/", { app_id: appId, max_reviews: maxReviews });
      clearInterval(timer);
      hideAnalysisProgress();
      UI.showAlert(`Analysis completed: ${run.llm_label} (${(run.llm_confidence ?? 0).toFixed(2)})`, "success", 5000);
      await loadLatestAnalysis();
      await loadTrends();
    } catch (err) {
      hideAnalysisProgress();
      UI.showAlert(err.message || "Analysis failed.");
    } finally {
      btnRunAnalysis.disabled = false;
      maxReviewsInput.disabled = false;
    }
  });

  // --- Canvas Drawing: Radar Chart (Feature 11) ---
  function drawRadarChart(canvas, scores) {
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2, R = Math.min(W, H) / 2 - 30;
    const dims = ["safety", "privacy", "quality", "trust", "sentiment"];
    const N = dims.length;
    ctx.clearRect(0, 0, W, H);

    // Grid
    for (let ring = 1; ring <= 5; ring++) {
      const r = R * ring / 5;
      ctx.beginPath();
      for (let i = 0; i <= N; i++) {
        const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
        const x = cx + r * Math.cos(angle);
        const y = cy + r * Math.sin(angle);
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "#e0e0e0";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Axes
    for (let i = 0; i < N; i++) {
      const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + R * Math.cos(angle), cy + R * Math.sin(angle));
      ctx.strokeStyle = "#e0e0e0";
      ctx.stroke();
    }

    // Data polygon
    ctx.beginPath();
    for (let i = 0; i <= N; i++) {
      const idx = i % N;
      const val = (scores[dims[idx]] || 0) / 100;
      const angle = (Math.PI * 2 * idx) / N - Math.PI / 2;
      const x = cx + R * val * Math.cos(angle);
      const y = cy + R * val * Math.sin(angle);
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    }
    ctx.fillStyle = "rgba(30, 78, 66, 0.2)";
    ctx.fill();
    ctx.strokeStyle = "#1E4E42";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Data points and labels
    for (let i = 0; i < N; i++) {
      const val = (scores[dims[i]] || 0) / 100;
      const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
      const x = cx + R * val * Math.cos(angle);
      const y = cy + R * val * Math.sin(angle);
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = "#1E4E42";
      ctx.fill();

      const lx = cx + (R + 18) * Math.cos(angle);
      const ly = cy + (R + 18) * Math.sin(angle);
      ctx.font = "12px Inter, sans-serif";
      ctx.fillStyle = "#4F4F4F";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(dims[i].charAt(0).toUpperCase() + dims[i].slice(1), lx, ly);
    }
  }

  // --- Canvas Drawing: Trend Chart (Feature 3) ---
  function drawTrendChart(canvas, data) {
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    const W = rect.width, H = rect.height;
    const pad = { top: 20, right: 20, bottom: 40, left: 50 };
    const cw = W - pad.left - pad.right;
    const ch = H - pad.top - pad.bottom;

    ctx.clearRect(0, 0, W, H);

    // Y axis
    ctx.font = "11px Inter, sans-serif";
    ctx.fillStyle = "#828282";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (let v = 0; v <= 100; v += 25) {
      const y = pad.top + ch - (v / 100) * ch;
      ctx.fillText(v, pad.left - 8, y);
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(W - pad.right, y);
      ctx.strokeStyle = "#f0f0f0";
      ctx.stroke();
    }

    if (data.length < 2) return;

    // X positions
    const xStep = cw / (data.length - 1);

    // Line
    ctx.beginPath();
    data.forEach((d, i) => {
      const x = pad.left + i * xStep;
      const y = pad.top + ch - (d.safety_score / 100) * ch;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.strokeStyle = "#1E4E42";
    ctx.lineWidth = 2;
    ctx.stroke();

    // Area fill
    ctx.lineTo(pad.left + (data.length - 1) * xStep, pad.top + ch);
    ctx.lineTo(pad.left, pad.top + ch);
    ctx.closePath();
    ctx.fillStyle = "rgba(30, 78, 66, 0.08)";
    ctx.fill();

    // Points and labels
    ctx.textAlign = "center";
    data.forEach((d, i) => {
      const x = pad.left + i * xStep;
      const y = pad.top + ch - (d.safety_score / 100) * ch;
      const color = d.label === "FRAUD" ? "#FF4D4D" : d.label === "LEGIT" ? "#00C853" : "#FFAB00";
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 2;
      ctx.stroke();

      // X axis date labels
      if (i === 0 || i === data.length - 1 || data.length <= 8) {
        ctx.fillStyle = "#828282";
        ctx.font = "10px Inter, sans-serif";
        const date = new Date(d.date);
        ctx.fillText(date.toLocaleDateString(undefined, { month: "short", day: "numeric" }), x, H - pad.bottom + 16);
      }
    });

    // Y axis label
    ctx.save();
    ctx.translate(14, pad.top + ch / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillStyle = "#828282";
    ctx.font = "11px Inter, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Safety Score", 0, 0);
    ctx.restore();
  }

  // Initialize
  try {
    reviewsPageSizeSel.value = "10";
    reviewsPageSize = 10;
    await loadApp();
    await loadReviews();
    await loadLatestAnalysis();
    await loadWatchState();
    await loadTrends();
  } catch (err) {
    UI.showAlert(err.message || "Failed to load app detail.");
  }
});
