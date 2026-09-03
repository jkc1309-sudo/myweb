# 金可成 · 个人网站

中文主站面向 AI 产品经理作品集；英文学术站在 `/en/`。

## 线上地址

https://jkc1309-sudo.github.io/myweb/

英文版：https://jkc1309-sudo.github.io/myweb/en/

## 结构

```
.
├── index.html                 # 中文首页（长滚动）
├── publications.html          # 中文论文与专利列表
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
├── assets/
├── content/                   # 中文站可编辑内容
├── templates/                 # 生成首页 / 详情页的模板
└── admin/                     # 本机内容管理后台
```

## 本机内容管理

只监听本机，用来改中文站文案、增删作品、上传封面和简历。保存后会重写 `index.html` 和 `projects/*.html`。英文站需另改。

```bash
python3 -m pip install -r requirements-admin.txt
python3 admin/server.py
# 管理后台 http://127.0.0.1:8787/admin
# 站点预览 http://127.0.0.1:8787/
```

1. 在后台改内容或上传文件，点「保存并生成」。
2. 同一端口打开首页核对。
3. 确认后提交并推送到 `main`，GitHub Pages 照旧发布。

仅重新生成静态页、不启动服务：

```bash
python3 admin/server.py --generate
```

## 本地预览

```bash
python3 -m http.server 8000
# 打开 http://localhost:8000
```

## 部署 GitHub Pages

1. 推送到 `main`。
2. Settings → Pages：Deploy from a branch，`main` / `/ (root)`。
