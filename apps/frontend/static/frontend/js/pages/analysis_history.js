document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const tbody = document.querySelector("#runsTable tbody");
  const empty = document.getElementById("runsEmpty");
  const filterInput = document.getElementById("filterAppId");
  const btnApply = document.getElementById("btnApplyFilter");
  const btnClear = document.getElementById("btnClearFilter");
  const runsPager = document.getElementById("runsPager");
  const runsPageSizeSel = document.getElementById("runsPageSize");
  const runsPrevBtn = document.getElementById("runsPrev");
  const runsNextBtn = document.getElementById("runsNext");
  const runsPageInfo = document.getElementById("runsPageInfo");

  let allRuns = [];
  let runsPage = 1;
  let runsPageSize = 10;
  let currentAppFilter = null;

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }
  function getTotalPages(total, size) {
    return Math.max(1, Math.ceil(total / size));
  }
  function slicePage(arr, page, size) {
    const start = (page - 1) * size;
    return arr.slice(start, start + size);
  }

  function badgeClass(label) {
    const l = (label || "").toUpperCase();
    if (l === "FRAUD") return "badge-fraud";
    if (l === "SUSPICIOUS") return "badge-suspicious";
    if (l === "LEGIT") return "badge-legit";
    if (l === "UNKNOWN") return "badge-unknown";
    return "badge-neutral";
  }

  function renderRunsTable() {
    tbody.innerHTML = "";
    empty.style.display = "none";
    runsPager.style.display = "none";

    const total = allRuns.length;
    if (total === 0) {
      empty.style.display = "block";
      return;
    }

    const totalPages = getTotalPages(total, runsPageSize);
    runsPage = clamp(runsPage, 1, totalPages);
    const items = slicePage(allRuns, runsPage, runsPageSize);

    items.forEach(run => {
      const tr = document.createElement("tr");
      const cls = badgeClass(run.llm_label);
      tr.innerHTML = `
        <td class="font-mono text-sm">${run.id}</td>
        <td>${UI.escapeHtml(String(run.app))}</td>
        <td>${UI.escapeHtml(run.status)}</td>
        <td><span class="${cls}">${UI.escapeHtml(run.llm_label)}</span></td>
        <td class="font-mono text-small">${(run.llm_confidence ?? 0).toFixed(2)}</td>
        <td class="text-small text-muted">${new Date(run.created_at).toLocaleString()}</td>
        <td class="col-action"><a href="/analysis/${run.id}/" class="link-primary link-action">Open</a></td>
      `;
      tbody.appendChild(tr);
    });

    runsPager.style.display = "flex";
    runsPageInfo.textContent = `Page ${runsPage} of ${totalPages} (${total} runs)`;
    runsPrevBtn.disabled = runsPage <= 1;
    runsNextBtn.disabled = runsPage >= totalPages;
  }

  async function fetchRuns(appId = null) {
    tbody.innerHTML = "";
    empty.style.display = "none";
    runsPager.style.display = "none";
    const url = appId ? `/api/analysis/?app=${encodeURIComponent(appId)}` : "/api/analysis/";
    const response = await Api.get(url);
    allRuns = Api.extractArray(response);
    renderRunsTable();
  }

  runsPageSizeSel.addEventListener("change", () => {
    runsPageSize = Math.min(100, Math.max(10, Number(runsPageSizeSel.value) || 10));
    runsPage = 1;
    renderRunsTable();
  });
  runsPrevBtn.addEventListener("click", () => {
    runsPage = Math.max(1, runsPage - 1);
    renderRunsTable();
  });
  runsNextBtn.addEventListener("click", () => {
    const totalPages = getTotalPages(allRuns.length, runsPageSize);
    runsPage = Math.min(totalPages, runsPage + 1);
    renderRunsTable();
  });

  btnApply.addEventListener("click", async () => {
    const v = (filterInput.value || "").trim();
    currentAppFilter = v || null;
    runsPage = 1;
    try {
      await fetchRuns(currentAppFilter);
    } catch (err) {
      UI.showAlert(err.message || "Failed to load runs.");
    }
  });

  btnClear.addEventListener("click", async () => {
    filterInput.value = "";
    currentAppFilter = null;
    runsPage = 1;
    try {
      await fetchRuns(null);
    } catch (err) {
      UI.showAlert(err.message || "Failed to load runs.");
    }
  });

  try {
    runsPageSizeSel.value = "10";
    runsPageSize = 10;
    await fetchRuns(null);
  } catch (err) {
    UI.showAlert(err.message || "Failed to load runs.");
  }
});
