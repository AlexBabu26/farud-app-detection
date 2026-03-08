document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const username = fd.get("username");
    const password = fd.get("password");

    try {
      await Auth.login(username, password);
      window.location.href = "/dashboard/";
    } catch (err) {
      UI.showAlert(err.message || "Login failed.");
    }
  });
});

