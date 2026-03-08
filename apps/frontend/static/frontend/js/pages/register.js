document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(form);

    const payload = {
      username: fd.get("username"),
      email: fd.get("email") || "",
      password: fd.get("password"),
      password2: fd.get("password2"),
    };

    try {
      await Api.post("/api/auth/register/", payload, { auth: false });
      UI.showAlert("Registration successful. Please login.", "success", 4000);
      window.location.href = "/login/";
    } catch (err) {
      UI.showAlert(err.message || "Registration failed.");
    }
  });
});

