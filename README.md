# 金可成 · 个人网站

中文主站面向 AI 产品经理作品集；英文学术站在 `/en/`。

## 线上地址

https://jkc1309-sudo.github.io/myweb/

英文版：https://jkc1309-sudo.github.io/myweb/en/

## 结构

```
.
├── index.html                 # 中文首页（长滚动）
├── cv.html                    # 中文简历页
├── projects/                  # 中文项目详情
│   ├── ai-tour-guide.html
│   ├── iipms.html
│   ├── museum-narrative.html
│   └── simteaching.html
├── en/                        # 英文学术站
│   ├── index.html
│   ├── projects.html
│   ├── publications.html
│   └── cv.html
├── styles.css
├── script.js
├── Jin_CV.pdf                 # 英文简历
├── Jin_CV_zh.pdf              # 中文简历
└── assets/
```

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 部署 GitHub Pages

1. 推送到 `main`。
2. Settings → Pages：Deploy from a branch，`main` / `/ (root)`。
