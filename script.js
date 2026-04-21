const currentPage = document.body.dataset.page;
const navLinks = document.querySelectorAll(".site-nav a");
const menuButton = document.querySelector(".menu-toggle");
const header = document.querySelector(".site-header");

navLinks.forEach((link) => {
  const href = link.getAttribute("href");
  if (!href) return;

  const pageName = href.replace(".html", "").replace("./", "");
  if ((currentPage === "home" && href === "index.html") || pageName === currentPage) {
    link.classList.add("active");
  }

  link.addEventListener("click", () => {
    header?.classList.remove("is-open");
    menuButton?.setAttribute("aria-expanded", "false");
  });
});

menuButton?.addEventListener("click", () => {
  const isOpen = header?.classList.toggle("is-open");
  menuButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll(".reveal").forEach((section, index) => {
  section.style.transitionDelay = `${index * 60}ms`;
  observer.observe(section);
});
