#!/usr/bin/env python3
"""Local-only content admin for the Chinese portfolio site."""

from __future__ import annotations

import json
import mimetypes
import posixpath
import re
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError as exc:
    raise SystemExit("请先安装依赖：python3 -m pip install -r requirements-admin.txt") from exc

ROOT = Path(__file__).resolve().parent.parent
ADMIN_DIR = ROOT / "admin"
CONTENT_DIR = ROOT / "content"
TEMPLATES_DIR = ROOT / "templates"
PROJECTS_DIR = ROOT / "projects"
ASSETS_DIR = ROOT / "assets"
HOST = "127.0.0.1"
PORT = 8787
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
UPLOAD_KINDS = {
    "portrait": {".png", ".jpg", ".jpeg", ".webp"},
    "cover": {".png", ".jpg", ".jpeg", ".webp"},
    "cv_zh": {".pdf"},
    "cv_en": {".pdf"},
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_site(site: dict[str, Any], works: list[dict[str, Any]]) -> list[str]:
    jinja = env()
    projects = [item for item in works if item.get("type") != "research"]
    research = [item for item in works if item.get("type") == "research"]

    index_html = jinja.get_template("index.html.j2").render(
        site=site, projects=projects, research=research
    )
    (ROOT / "index.html").write_text(index_html + "\n", encoding="utf-8")

    PROJECTS_DIR.mkdir(exist_ok=True)
    kept: set[str] = set()
    count = len(works)
    for index, work in enumerate(works):
        slug = work.get("slug") or ""
        if not SLUG_RE.match(slug):
            raise ValueError(f"无效 slug：{slug}")
        kept.add(slug)
        prev_item = works[index - 1] if count > 1 else None
        next_item = works[(index + 1) % count] if count > 1 else None
        page = jinja.get_template("project.html.j2").render(
            site=site, work=work, prev=prev_item, next=next_item
        )
        (PROJECTS_DIR / f"{slug}.html").write_text(page + "\n", encoding="utf-8")

    removed: list[str] = []
    for path in PROJECTS_DIR.glob("*.html"):
        if path.stem not in kept:
            path.unlink()
            removed.append(path.name)
    return removed


def parse_multipart(header: str, body: bytes) -> dict[str, Any]:
    match = re.search(r'boundary="?([^";]+)"?', header or "", flags=re.I)
    if not match:
        raise ValueError("缺少 multipart boundary")
    boundary = match.group(1).encode()
    parts = body.split(b"--" + boundary)
    fields: dict[str, Any] = {}
    for raw in parts:
        chunk = raw.strip()
        if not chunk or chunk == b"--":
            continue
        if b"\r\n\r\n" in chunk:
            head, data = chunk.split(b"\r\n\r\n", 1)
        elif b"\n\n" in chunk:
            head, data = chunk.split(b"\n\n", 1)
        else:
            continue
        if data.endswith(b"\r\n"):
            data = data[:-2]
        elif data.endswith(b"\n"):
            data = data[:-1]
        disp = ""
        for line in head.decode("utf-8", errors="replace").splitlines():
            if line.lower().startswith("content-disposition:"):
                disp = line
        name_match = re.search(r'name="([^"]+)"', disp)
        if not name_match:
            continue
        name = name_match.group(1)
        file_match = re.search(r'filename="([^"]*)"', disp)
        if file_match:
            fields[name] = {"filename": file_match.group(1), "data": data}
        else:
            fields[name] = data.decode("utf-8")
    return fields


def safe_filename(name: str) -> str:
    base = Path(name).name
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip(".-")
    return base or f"upload-{uuid.uuid4().hex[:8]}"


class AdminHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        print(f"[admin] {args[0]}")

    def _json(self, payload: Any, status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _text(self, body: str, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in {"/admin", "/admin/"}:
            html = (ADMIN_DIR / "index.html").read_text(encoding="utf-8")
            self._text(html)
            return
        if path == "/api/content":
            self._json(
                {
                    "site": load_json(CONTENT_DIR / "site.json"),
                    "works": load_json(CONTENT_DIR / "works.json"),
                }
            )
            return
        if path.startswith("/api/"):
            self._json({"error": "未找到接口"}, 404)
            return
        super().do_GET()

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/content":
            self._json({"error": "未找到接口"}, 404)
            return
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
            site = payload["site"]
            works = payload["works"]
            if not isinstance(works, list):
                raise ValueError("works 必须是数组")
            slugs = [item.get("slug", "") for item in works]
            if any(not SLUG_RE.match(str(slug)) for slug in slugs):
                raise ValueError("slug 只能包含小写字母、数字和连字符")
            if len(slugs) != len(set(slugs)):
                raise ValueError("slug 不能重复")
            site["css_version"] = str(int(time.time()))
            save_json(CONTENT_DIR / "site.json", site)
            save_json(CONTENT_DIR / "works.json", works)
            removed = generate_site(site, works)
            self._json({"ok": True, "removed": removed})
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, 400)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/upload":
            self._json({"error": "未找到接口"}, 404)
            return
        try:
            fields = parse_multipart(self.headers.get("Content-Type", ""), self._read_body())
            kind = str(fields.get("kind") or "")
            upload = fields.get("file")
            if kind not in UPLOAD_KINDS or not isinstance(upload, dict):
                raise ValueError("请选择有效文件")
            filename = safe_filename(upload.get("filename") or "upload.bin")
            suffix = Path(filename).suffix.lower()
            if suffix == ".jpeg":
                suffix = ".jpg"
            if suffix not in UPLOAD_KINDS[kind]:
                raise ValueError(f"{kind} 不支持 {suffix or '无扩展名'} 文件")
            data = upload["data"]
            if not data:
                raise ValueError("文件是空的")

            if kind == "cv_zh":
                dest = ROOT / "Jin_CV_zh.pdf"
                dest.write_bytes(data)
                path = "Jin_CV_zh.pdf"
            elif kind == "cv_en":
                dest = ROOT / "Jin_CV.pdf"
                dest.write_bytes(data)
                path = "Jin_CV.pdf"
            elif kind == "portrait":
                dest = ASSETS_DIR / f"portrait{suffix}"
                dest.write_bytes(data)
                path = f"assets/{dest.name}"
            else:
                slug = str(fields.get("slug") or "cover")
                slug = slug if SLUG_RE.match(slug) else "cover"
                dest = ASSETS_DIR / f"{slug}-cover{suffix}"
                dest.write_bytes(data)
                path = f"assets/{dest.name}"
            self._json({"ok": True, "path": path})
        except Exception as exc:  # noqa: BLE001
            self._json({"error": str(exc)}, 400)

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        rel = posixpath.normpath(unquote(parsed.path)).lstrip("/")
        if rel.startswith("admin/") and not rel.startswith("admin/index"):
            candidate = ROOT / rel
            if candidate.is_file():
                return str(candidate)
        return super().translate_path(path)

    def guess_type(self, path: str) -> str:
        guessed, _ = mimetypes.guess_type(path)
        return guessed or "application/octet-stream"


def main() -> None:
    import sys

    ASSETS_DIR.mkdir(exist_ok=True)
    CONTENT_DIR.mkdir(exist_ok=True)
    if "--generate" in sys.argv:
        site = load_json(CONTENT_DIR / "site.json")
        works = load_json(CONTENT_DIR / "works.json")
        removed = generate_site(site, works)
        print("已生成静态页", f"（删除 {', '.join(removed)}）" if removed else "")
        return
    server = ThreadingHTTPServer((HOST, PORT), AdminHandler)
    print(f"管理后台：http://{HOST}:{PORT}/admin")
    print(f"站点预览：http://{HOST}:{PORT}/")
    print("只监听本机。按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        server.server_close()


if __name__ == "__main__":
    main()
