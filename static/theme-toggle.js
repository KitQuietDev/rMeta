document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("themeToggle");
  const label = document.getElementById("themeLabel");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");

  if (!btn || !label) {
    console.warn("⚠️ Theme toggle button or label not found.");
    return;
  }

  // Set "auto" on first visit if not set
  if (!localStorage.getItem("theme")) {
    localStorage.setItem("theme", "auto");
  }

  function getCurrentTheme() {
    return localStorage.getItem("theme") || "auto";
  }

  function applyTheme(mode) {
    switch (mode) {
      case "dark":
        document.body.classList.add("dark-mode");
        label.textContent = "Dark Mode";
        btn.textContent = "☀️";
        btn.title = "Toggle theme (Next: Light)";
        break;
      case "light":
        document.body.classList.remove("dark-mode");
        label.textContent = "Light Mode";
        btn.textContent = "🖥️";
        btn.title = "Toggle theme (Next: System)";
        break;
      case "auto":
      default:
        if (prefersDark.matches) {
          document.body.classList.add("dark-mode");
          label.textContent = "System (Dark)";
        } else {
          document.body.classList.remove("dark-mode");
          label.textContent = "System (Light)";
        }
        btn.textContent = "🌙";
        btn.title = "Toggle theme (Next: Dark)";
        break;
    }
  }

  function cycleTheme() {
    const current = getCurrentTheme();
    const next = current === "dark" ? "light" : current === "light" ? "auto" : "dark";
    localStorage.setItem("theme", next);
    applyTheme(next);
  }

  btn.addEventListener("click", cycleTheme);
  applyTheme(getCurrentTheme());
});
