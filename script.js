const currentPage = document.body.dataset.page;
const navKey = document.body.dataset.nav;
const navLinks = document.querySelectorAll(".site-nav a");
const menuButton = document.querySelector(".menu-toggle");
const header = document.querySelector(".site-header");

function closeMenu() {
  header?.classList.remove("is-open");
  menuButton?.setAttribute("aria-expanded", "false");
}

navLinks.forEach((link) => {
  const href = link.getAttribute("href") || "";
  const section = link.dataset.section;
  const fileName = href.split("#")[0].split("/").pop();

  if (navKey && section === navKey) {
    link.classList.add("active");
  } else if (!navKey && currentPage === "home" && fileName === "index.html") {
    link.classList.add("active");
  } else if (!navKey && currentPage && currentPage !== "home") {
    const pageName = fileName.replace(".html", "");
    if (pageName === currentPage) {
      link.classList.add("active");
    }
  }

  link.addEventListener("click", () => {
    closeMenu();
  });
});

menuButton?.addEventListener("click", () => {
  const isOpen = header?.classList.toggle("is-open");
  menuButton.setAttribute("aria-expanded", isOpen ? "true" : "false");
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll(".reveal").forEach((section, index) => {
  section.style.transitionDelay = `${index * 60}ms`;
  revealObserver.observe(section);
});

const sectionNodes = document.querySelectorAll("[data-section-id]");
const sectionLinks = document.querySelectorAll(".site-nav a[data-section]");

if (sectionNodes.length && sectionLinks.length) {
  const spy = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = entry.target.dataset.sectionId;
        sectionLinks.forEach((link) => {
          if (link.dataset.section === "cv") return;
          link.classList.toggle("active", link.dataset.section === id);
        });
      });
    },
    { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
  );

  sectionNodes.forEach((section) => spy.observe(section));
}

const backButton = document.querySelector(".back-to-top");
const footerBackLinks = document.querySelectorAll(".js-back-to-top");

function scrollToTop(event) {
  event?.preventDefault();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateBackButton() {
  if (!backButton) return;
  backButton.classList.toggle("is-visible", window.scrollY > window.innerHeight * 0.8);
}

backButton?.addEventListener("click", scrollToTop);
footerBackLinks.forEach((link) => link.addEventListener("click", scrollToTop));
window.addEventListener("scroll", updateBackButton, { passive: true });
updateBackButton();

const cvRoot = document.querySelector("[data-cv-root]");
if (cvRoot) {
  const files = {
    zh: cvRoot.dataset.cvZh,
    en: cvRoot.dataset.cvEn,
  };
  const titles = {
    zh: "金可成中文简历",
    en: "English CV of Kecheng Jin",
  };
  const frame = cvRoot.querySelector("[data-cv-frame]");
  const downloadLink = cvRoot.querySelector("[data-cv-download]");
  const openLink = cvRoot.querySelector("[data-cv-open]");
  const tabs = cvRoot.querySelectorAll("[data-cv-lang]");

  function fileName(path) {
    return (path || "").split("/").pop();
  }

  function setCvLang(lang) {
    const src = files[lang];
    if (!src) return;

    tabs.forEach((tab) => {
      tab.setAttribute("aria-selected", tab.dataset.cvLang === lang ? "true" : "false");
    });

    if (frame) {
      frame.src = `${src}#view=FitH`;
      frame.title = titles[lang];
    }

    if (downloadLink) {
      downloadLink.href = src;
      downloadLink.setAttribute("download", fileName(src));
    }

    if (openLink) {
      openLink.href = src;
    }

    if (window.location.hash !== `#${lang}`) {
      history.replaceState(null, "", `#${lang}`);
    }
  }

  const fromHash = window.location.hash.replace("#", "");
  const initial = files[fromHash] ? fromHash : cvRoot.dataset.cvDefault || "zh";
  setCvLang(initial);

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => setCvLang(tab.dataset.cvLang));
  });
}

const awardCarousel = document.querySelector("[data-award-carousel]");
if (awardCarousel) {
  const cards = [...awardCarousel.querySelectorAll(".award-card")];
  const dotsRoot = awardCarousel.querySelector(".award-dots");
  const caption = awardCarousel.querySelector(".award-caption");
  const kickerNode = caption?.querySelector("[data-award-kicker]");
  const titleNode = caption?.querySelector("[data-award-title]");
  const bodyNode = caption?.querySelector("[data-award-body]");
  const total = cards.length;
  let current = 0;

  cards.forEach((_, index) => {
    const dot = document.createElement("button");
    dot.type = "button";
    dot.setAttribute("role", "tab");
    dot.setAttribute("aria-label", `第 ${index + 1} 件作品`);
    dot.addEventListener("click", () => goTo(index));
    dotsRoot?.append(dot);
  });

  const dots = [...(dotsRoot?.querySelectorAll("button") || [])];

  function wrappedOffset(index) {
    let offset = index - current;
    const half = total / 2;
    if (offset > half) offset -= total;
    if (offset < -half) offset += total;
    return offset;
  }

  function goTo(index) {
    current = ((index % total) + total) % total;
    render();
  }

  function render() {
    const spread = Math.min(236, Math.max(132, awardCarousel.clientWidth * 0.28));
    cards.forEach((card, index) => {
      const offset = wrappedOffset(index);
      const far = Math.abs(offset) >= 2;
      card.style.setProperty("--tx", `${offset * spread}px`);
      card.style.setProperty("--tz", `${offset === 0 ? 72 : far ? -180 : -36}px`);
      card.style.setProperty("--ry", `${offset * -34}deg`);
      card.style.setProperty("--sc", offset === 0 ? "1" : far ? "0.68" : "0.82");
      card.style.opacity = far ? "0.42" : "1";
      card.style.zIndex = String(20 - Math.abs(offset) * 4);
      card.classList.toggle("is-active", offset === 0);
      card.setAttribute("aria-current", offset === 0 ? "true" : "false");
    });

    const active = cards[current];
    if (kickerNode) kickerNode.textContent = active?.dataset.awardKicker || "";
    if (titleNode) titleNode.textContent = active?.dataset.awardTitle || "";
    if (bodyNode) bodyNode.textContent = active?.dataset.awardBody || "";
    dots.forEach((dot, index) => dot.classList.toggle("is-active", index === current));
  }

  awardCarousel.querySelector(".award-nav--prev")?.addEventListener("click", () => goTo(current - 1));
  awardCarousel.querySelector(".award-nav--next")?.addEventListener("click", () => goTo(current + 1));

  cards.forEach((card, index) => {
    card.addEventListener("click", () => {
      if (index !== current) goTo(index);
    });
  });

  awardCarousel.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") goTo(current - 1);
    if (event.key === "ArrowRight") goTo(current + 1);
  });

  let touchStartX = 0;
  awardCarousel.addEventListener(
    "touchstart",
    (event) => {
      touchStartX = event.changedTouches[0]?.clientX || 0;
    },
    { passive: true }
  );
  awardCarousel.addEventListener(
    "touchend",
    (event) => {
      const delta = (event.changedTouches[0]?.clientX || 0) - touchStartX;
      if (Math.abs(delta) > 40) goTo(current + (delta < 0 ? 1 : -1));
    },
    { passive: true }
  );

  window.addEventListener("resize", render, { passive: true });
  render();
}
