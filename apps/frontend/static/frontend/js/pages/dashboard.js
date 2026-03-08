document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const tableBody = document.querySelector("#appsTable tbody");
  const empty = document.getElementById("appsEmpty");
  const form = document.getElementById("createAppForm");
  const selectAll = document.getElementById("selectAllApps");
  const btnBulkAnalyze = document.getElementById("btnBulkAnalyze");
  const bulkProgress = document.getElementById("bulkProgress");
  const bulkProgressText = document.getElementById("bulkProgressText");
  const bulkResults = document.getElementById("bulkResults");

  const params = new URLSearchParams(window.location.search);
  const paste = params.get("paste");
  if (paste && form) {
    if (/^[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+/.test(paste) && !paste.startsWith("http")) {
      form.querySelector('input[name="package_name"]').value = paste;
    } else {
      form.querySelector('input[name="store_url"]').value = paste;
    }
  }

  let selectedAppIds = new Set();

  function updateBulkBtn() {
    btnBulkAnalyze.disabled = selectedAppIds.size === 0;
    btnBulkAnalyze.textContent = selectedAppIds.size > 0
      ? `Analyze Selected (${selectedAppIds.size})`
      : "Analyze Selected";
  }

  async function loadApps() {
    tableBody.innerHTML = "";
    empty.style.display = "none";
    selectedAppIds.clear();
    updateBulkBtn();

    try {
      const response = await Api.get("/api/apps/");
      const apps = Api.extractArray(response);
      if (!apps || apps.length === 0) {
        empty.style.display = "block";
        return;
      }

      apps.forEach(app => {
        const tr = document.createElement("tr");
        const analysis = app.latest_analysis;
        const safetyScore = analysis ? analysis.safety_score : "—";
        const safetyColor = analysis ? (analysis.safety_score > 70 ? "var(--legit)" : analysis.safety_score > 40 ? "var(--suspicious)" : "var(--fraud)") : "inherit";

        tr.innerHTML = `
          <td><input type="checkbox" class="app-select-cb" value="${app.id}" /></td>
          <td><a href="/apps/${app.id}/" class="link-primary">${UI.escapeHtml(app.name)}</a></td>
          <td class="font-mono text-small text-muted">${UI.escapeHtml(app.package_name)}</td>
          <td>${UI.escapeHtml(app.developer || "—")}</td>
          <td>
            ${analysis ? `<a href="/analysis/${analysis.id}/" style="color:${safetyColor};font-weight:bold;">${safetyScore}/100</a>` : '<span class="text-muted">—</span>'}
          </td>
          <td class="text-small text-muted">${new Date(app.created_at).toLocaleString()}</td>
          <td><button class="btn-danger" data-del="${app.id}" type="button">Delete</button></td>
        `;
        tableBody.appendChild(tr);
      });

      tableBody.querySelectorAll(".app-select-cb").forEach(cb => {
        cb.addEventListener("change", () => {
          const id = Number(cb.value);
          if (cb.checked) selectedAppIds.add(id);
          else selectedAppIds.delete(id);
          updateBulkBtn();
        });
      });

      tableBody.querySelectorAll("button[data-del]").forEach(btn => {
        btn.addEventListener("click", async () => {
          const id = btn.getAttribute("data-del");
          if (!confirm("Delete this app and all related reviews/analysis?")) return;
          try {
            await Api.del(`/api/apps/${id}/`);
            await loadApps();
          } catch (err) {
            UI.showAlert(err.message || "Delete failed.");
          }
        });
      });
    } catch (err) {
      UI.showAlert(err.message || "Failed to load apps.");
    }
  }

  selectAll.addEventListener("change", () => {
    const cbs = tableBody.querySelectorAll(".app-select-cb");
    cbs.forEach(cb => {
      cb.checked = selectAll.checked;
      const id = Number(cb.value);
      if (selectAll.checked) selectedAppIds.add(id);
      else selectedAppIds.delete(id);
    });
    updateBulkBtn();
  });

  // Feature 12: Bulk Scanning
  btnBulkAnalyze.addEventListener("click", async () => {
    if (selectedAppIds.size === 0) return;
    btnBulkAnalyze.disabled = true;
    bulkProgress.style.display = "block";
    bulkProgressText.textContent = `Analyzing ${selectedAppIds.size} app(s)... This may take a while.`;
    bulkResults.innerHTML = "";

    try {
      const data = await Api.post("/api/analysis/bulk-run/", {
        app_ids: Array.from(selectedAppIds),
        max_reviews: 200,
      });

      bulkProgressText.textContent = "Bulk analysis complete.";
      if (data.results) {
        data.results.forEach(r => {
          const div = document.createElement("div");
          const labelCls = r.label === "FRAUD" ? "badge-fraud" : r.label === "LEGIT" ? "badge-legit" : r.label === "SUSPICIOUS" ? "badge-suspicious" : "badge-unknown";
          div.className = "bulk-result-item";
          div.innerHTML = `
            <span>App #${r.app_id}</span>
            <span class="${labelCls}">${UI.escapeHtml(r.label || r.status)}</span>
            ${r.run_id ? `<a href="/analysis/${r.run_id}/" class="link-primary text-small">View</a>` : ""}
            ${r.error ? `<span class="text-small" style="color:var(--fraud);">${UI.escapeHtml(r.error.slice(0, 80))}</span>` : ""}
          `;
          bulkResults.appendChild(div);
        });
      }
      await loadApps();
    } catch (err) {
      bulkProgressText.textContent = "Bulk analysis failed.";
      UI.showAlert(err.message || "Bulk analysis failed.");
    } finally {
      btnBulkAnalyze.disabled = false;
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = {
      name: fd.get("name"),
      package_name: fd.get("package_name"),
      store_url: fd.get("store_url") || null,
      developer: fd.get("developer") || null,
      category: fd.get("category") || null,
      description: fd.get("description") || null,
      privacy_policy_text: fd.get("privacy_policy_text") || null,
    };
    try {
      await Api.post("/api/apps/", payload);
      form.reset();
      if (paste) {
        form.querySelector('input[name="store_url"]').value = paste.includes("http") ? paste : "";
        form.querySelector('input[name="package_name"]').value = !paste.includes("http") ? paste : "";
      }
      await loadApps();
    } catch (err) {
      UI.showAlert(err.message || "Create failed.");
    }
  });

  await loadApps();
});
