document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".primary-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });
  }

  document.querySelectorAll(".nav-drop-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const menu = btn.nextElementSibling;
      const expanded = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!expanded));
      menu.classList.toggle("show", !expanded);
    });
  });

  document.querySelectorAll(".flash-close").forEach(btn => {
    btn.addEventListener("click", () => btn.closest(".flash")?.remove());
  });

  document.querySelectorAll("form[data-confirm]").forEach(form => {
    form.addEventListener("submit", event => {
      if (!window.confirm(form.dataset.confirm || "Are you sure?")) event.preventDefault();
    });
  });

  const imageInput = document.querySelector("[data-image-input]");
  const preview = document.querySelector("[data-image-preview]");
  if (imageInput && preview) {
    imageInput.addEventListener("change", () => {
      const file = imageInput.files && imageInput.files[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        preview.textContent = "Please select an image file.";
        imageInput.value = "";
        return;
      }
      const reader = new FileReader();
      reader.onload = e => { preview.innerHTML = ""; const img = document.createElement("img"); img.src = e.target.result; img.alt = "Selected product preview"; preview.appendChild(img); };
      reader.readAsDataURL(file);
    });
  }

  document.querySelectorAll("input, textarea, select").forEach(el => {
    el.addEventListener("invalid", () => el.classList.add("invalid"));
    el.addEventListener("input", () => el.classList.remove("invalid"));
  });
});