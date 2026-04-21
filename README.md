# Kecheng Jin — Personal Website

Personal academic / portfolio website for Kecheng Jin (HCI / Generative AI / Interactive Systems).

## Live site

Once deployed via GitHub Pages:

https://jkc1309-sudo.github.io/myweb/

## Structure

```
.
├── index.html          # Home
├── projects.html       # Selected projects
├── publications.html   # Publications, patents, awards
├── cv.html             # Embedded CV viewer
├── styles.css          # Global styles
├── script.js           # Nav toggle + reveal-on-scroll
├── Jin_CV.pdf          # CV file (download / embed)
└── assets/             # Images used across pages
```

## Local preview

No build step required. Just open `index.html` in a browser, or run a tiny static server:

```bash
# Python 3
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Deploying to GitHub Pages

1. Push this repository to GitHub (`main` branch).
2. In the repo **Settings → Pages**, set:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` / `/ (root)`
3. Wait ~1 min for the first build, then visit the URL above.
