document.addEventListener("DOMContentLoaded", async () => {
  if (!UI.requireAuth()) return;

  const host = document.getElementById("meHost");
  try {
    const me = await Api.get("/api/auth/me/");
    host.className = "";
    host.innerHTML = `
      <div>
        <div><span class="text-small text-muted">User ID</span><br/><span class="font-mono">${me.id}</span></div>
        <div style="margin-top:8px;"><span class="text-small text-muted">Username</span><br/>${UI.escapeHtml(me.username)}</div>
        <div style="margin-top:8px;"><span class="text-small text-muted">Email</span><br/>${UI.escapeHtml(me.email || "—")}</div>
      </div>
      <div class="disclaimer-box" style="margin-top: 24px;">
        <strong>Disclaimer:</strong> This tool is not malware analysis and not a definitive security audit.
      </div>
    `;
  } catch (err) {
    host.className = "text-muted";
    host.textContent = "Failed to load profile.";
    UI.showAlert(err.message || "Failed to load profile.");
  }
});
