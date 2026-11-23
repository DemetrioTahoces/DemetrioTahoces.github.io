#!/usr/bin/env python3
"""Regenera los dos CV en PDF (completo y profesional ATS) en Linux, macOS y Windows.

Uso (desde cualquier directorio del repo, solo stdlib + Chrome/Chromium/Edge):
    python3 scripts/build_cv_pdfs.py                 # genera ambos PDF en assets/ y valida
    python3 scripts/build_cv_pdfs.py --only pro      # solo el CV resumido de una página
    python3 scripts/build_cv_pdfs.py --only full     # solo el CV completo desde index.html
    python3 scripts/build_cv_pdfs.py --out-dir /tmp  # escribe en otro directorio (omite check_cv_pdf)
    python3 scripts/build_cv_pdfs.py --no-check      # no lanza scripts/check_cv_pdf.py al final

Busca automáticamente CHROME_PATH, google-chrome, chromium o msedge. Levanta un servidor
HTTP efímero local para imprimir index.html sin dejar procesos abiertos.
"""

from __future__ import annotations

import argparse
import glob
import http.server
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FULL_NAME = "CV-Demetrio-Tahoces.pdf"
PRO_NAME = "CV-Demetrio-Tahoces-Profesional.pdf"
PRO_HTML = ROOT / "CV/cv-profesional.html"


def find_browser() -> str:
    env_path = os.environ.get("CHROME_PATH")
    if env_path and Path(env_path).is_file():
        return env_path
    for cmd in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"):
        found = shutil.which(cmd)
        if found:
            return found
    candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome")),
    ]
    for path in candidates:
        if Path(path).is_file():
            return path
    raise SystemExit("No se encontró Chrome, Chromium ni Edge. Instálalo o define CHROME_PATH.")


def print_pdf(browser: str, url: str, out_pdf: Path, profile_dir: Path) -> None:
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--virtual-time-budget=8000",
        f"--user-data-dir={profile_dir}",
        f"--print-to-pdf={out_pdf}",
    ]
    if sys.platform.startswith("linux"):
        cmd.insert(2, "--no-sandbox")
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out_pdf.is_file():
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"Error generando {out_pdf.name} (exit {result.returncode})")


def pdf_pages(pdf: Path) -> int | None:
    exe = shutil.which("pdfinfo")
    if not exe:
        return None
    out = subprocess.run([exe, str(pdf)], capture_output=True, text=True, check=True).stdout
    match = re.search(r"^Pages:\s+(\d+)", out, re.M)
    return int(match.group(1)) if match else None


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args) -> None:
        return


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Regenera los CV en PDF.")
    parser.add_argument("--only", choices=("full", "pro"), help="Genera solo uno de los dos PDF.")
    parser.add_argument("--out-dir", type=Path, default=ASSETS, help="Directorio de salida (por defecto assets/).")
    parser.add_argument("--no-check", action="store_true", help="Omite la validación final con check_cv_pdf.py.")
    args = parser.parse_args(argv)

    browser = find_browser()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    do_full = args.only in (None, "full")
    do_pro = args.only in (None, "pro")

    with tempfile.TemporaryDirectory(prefix="cv-pdf-") as tmp:
        tmp_path = Path(tmp)
        if do_full:
            with http.server.ThreadingHTTPServer(("127.0.0.1", 0), _QuietHandler) as srv:
                port = srv.server_address[1]
                thread = threading.Thread(target=srv.serve_forever, daemon=True)
                thread.start()
                try:
                    full_pdf = out_dir / FULL_NAME
                    print_pdf(browser, f"http://127.0.0.1:{port}/", full_pdf, tmp_path / "full-profile")
                finally:
                    srv.shutdown()
            pages = pdf_pages(full_pdf)
            extra = f", {pages} págs." if pages is not None else ""
            print(f"generado: {full_pdf} ({full_pdf.stat().st_size // 1024} KB{extra})")

        if do_pro:
            pro_pdf = out_dir / PRO_NAME
            print_pdf(browser, PRO_HTML.as_uri(), pro_pdf, tmp_path / "pro-profile")
            pages = pdf_pages(pro_pdf)
            extra = f", {pages} pág." if pages is not None else ""
            print(f"generado: {pro_pdf} ({pro_pdf.stat().st_size // 1024} KB{extra})")
            if pages is not None and pages != 1:
                print(f"ERROR: {PRO_NAME} ocupa {pages} páginas; el CV profesional debe caber en 1 página.", file=sys.stderr)
                return 1

    if not args.no_check and out_dir == ASSETS.resolve():
        return subprocess.run([sys.executable, str(ROOT / "scripts/check_cv_pdf.py")], cwd=ROOT).returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
