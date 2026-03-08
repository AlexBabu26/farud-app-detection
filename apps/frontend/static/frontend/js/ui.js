const UI = (() => {
  function showAlert(message, type = "danger", timeoutMs = 5000) {
    const host = document.getElementById("globalAlertHost");
    if (!host) return;

    const id = "a" + Math.random().toString(16).slice(2);
    const div = document.createElement("div");
    div.id = id;
    div.className = `alert alert-${type}`;
    div.role = "alert";
    div.innerHTML = `
      <div class="flex-1">${escapeHtml(message)}</div>
      <button type="button" class="btn-close" aria-label="Close">×</button>
    `;
    host.appendChild(div);
    div.querySelector('.btn-close').addEventListener('click', () => div.remove());

    if (timeoutMs) {
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.remove();
      }, timeoutMs);
    }
  }

  function escapeHtml(str) {
    return (str || "").replace(/[&<>"']/g, (m) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[m]));
  }

  function requireAuth() {
    if (!Auth.hasAccessToken()) {
      window.location.href = "/login/";
      return false;
    }
    return true;
  }

  return { showAlert, escapeHtml, requireAuth };
})();

