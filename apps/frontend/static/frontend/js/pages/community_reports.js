document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const form = document.getElementById("reportForm");
  const appSelect = document.getElementById("reportAppSelect");
  const tableBody = document.querySelector("#reportsTable tbody");
  const empty = document.getElementById("reportsEmpty");

  // Load user's apps into the select
  try {
    const response = await Api.get("/api/apps/");
    const apps = Api.extractArray(response);
    apps.forEach(app => {
      const opt = document.createElement("option");
      opt.value = app.id;
      opt.textContent = app.name;
      appSelect.appendChild(opt);
    });
  } catch (err) {
    UI.showAlert("Failed to load apps for reporting.");
  }

  async function loadReports() {
    tableBody.innerHTML = "";
    empty.style.display = "none";

    try {
      const response = await Api.get("/api/reports/");
      const reports = Api.extractArray(response);
      if (!reports.length) {
        empty.style.display = "block";
        return;
      }

      reports.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${UI.escapeHtml(r.app_name || "—")}</td>
          <td><span class="badge-report badge-report-${(r.reason || '').toLowerCase()}">${UI.escapeHtml(r.reason)}</span></td>
          <td style="max-width:300px;">${UI.escapeHtml((r.description || "").slice(0, 150))}${(r.description || "").length > 150 ? "…" : ""}</td>
          <td class="text-small text-muted">${UI.escapeHtml(r.username || "—")}</td>
          <td class="text-small text-muted">${new Date(r.created_at).toLocaleDateString()}</td>
          <td><button class="btn-danger text-small" data-del="${r.id}" type="button">Delete</button></td>
        `;
        tableBody.appendChild(tr);
      });

      tableBody.querySelectorAll("button[data-del]").forEach(btn => {
        btn.addEventListener("click", async () => {
          if (!confirm("Delete this report?")) return;
          try {
            await Api.del(`/api/reports/${btn.getAttribute("data-del")}/`);
            await loadReports();
          } catch (err) {
            UI.showAlert(err.message || "Delete failed.");
          }
        });
      });
    } catch (err) {
      UI.showAlert(err.message || "Failed to load reports.");
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    try {
      await Api.post("/api/reports/", {
        app: Number(fd.get("app")),
        reason: fd.get("reason"),
        description: fd.get("description"),
      });
      form.reset();
      UI.showAlert("Report submitted. Thank you for helping keep users safe.", "success", 4000);
      await loadReports();
    } catch (err) {
      UI.showAlert(err.message || "Failed to submit report.");
    }
  });

  await loadReports();
});
