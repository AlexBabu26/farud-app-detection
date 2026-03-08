document.addEventListener("DOMContentLoaded", () => {
  if (Auth.hasAccessToken()) {
    const heroRunScan = document.getElementById("heroRunScan");
    const heroScanInput = document.getElementById("heroScanInput");
    if (heroRunScan && heroScanInput) {
      heroRunScan.textContent = "Run Analysis";
      heroRunScan.addEventListener("click", () => {
        const v = (heroScanInput.value || "").trim();
        if (v) {
          window.location.href = "/dashboard/?paste=" + encodeURIComponent(v);
        } else {
          window.location.href = "/dashboard/";
        }
      });
    }
  } else {
    const heroRunScan = document.getElementById("heroRunScan");
    if (heroRunScan) {
      heroRunScan.addEventListener("click", () => {
        window.location.href = "/register/";
      });
    }
  }
});
