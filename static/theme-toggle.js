// theme-toggle.js
// Handles the light/dark/system theme toggle in the UI

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("themeToggle");   // Toggle button
  const label = document.getElementById("themeLabel");  // Label to show current theme mode
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)");  // System preference

  // Abort if elements aren't present (defensive check)
  if (!btn || !label) {
    console.warn("⚠️ Theme toggle button or label not found.");
    return;
  }

  // Set default theme to "auto" if not set yet (first visit)
  if (!localStorage.getItem("theme")) {
    localStorage.setItem("theme", "auto");
  }

  // Helper: Get the stored theme from localStorage
  function getCurrentTheme() {
    return localStorage.getItem("theme") || "auto";
  }

  // Apply the correct class/text/icon based on theme mode
  function applyTheme(mode) {
    switch (mode) {
      case "dark":
        document.body.classList.add("dark-mode");
        label.textContent = "Dark Mode";
        btn.textContent = "☀️"; // Icon indicates *next* mode
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

  // Cycle through modes: dark → light → auto → dark...
  function cycleTheme() {
    const current = getCurrentTheme();
    const next = current === "dark"
      ? "light"
      : current === "light"
      ? "auto"
      : "dark";

    localStorage.setItem("theme", next);
    applyTheme(next);
  }

  // Hook up click listener and apply current theme on load
  btn.addEventListener("click", cycleTheme);
  applyTheme(getCurrentTheme());
});
