"""Capture a screenshot of the Streamlit margin dashboard.

Usage:
    pip install playwright
    playwright install chromium
    python -m scripts.capture_dashboard

The database must be running and populated before capture.
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "app" / "module_a_margin" / "dashboard.py"
URL = "http://127.0.0.1:8501"
OUTPUT = ROOT / "docs" / "screenshots" / "dashboard.png"
VIEWPORT = {"width": 1600, "height": 1000}
READY_TIMEOUT_S = 60


def _wait_streamlit_ready(
    process: subprocess.Popen[bytes], log_file, timeout_s: int = READY_TIMEOUT_S
) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if process.poll() is not None:
            log_file.seek(0)
            output = log_file.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Streamlit encerrou antes de iniciar:\n{output}")
        try:
            response = httpx.get(URL, timeout=2)
            if response.status_code == 200:
                return
        except httpx.RequestError:
            pass
        time.sleep(1)
    raise TimeoutError(f"Streamlit não respondeu em {timeout_s}s ({URL})")


async def _capture() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            page = await browser.new_page(
                viewport=VIEWPORT,
                device_scale_factor=2,
            )
            await page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
            await page.locator('[data-testid="stMetric"]').nth(3).wait_for(
                timeout=30_000
            )
            await page.wait_for_timeout(2_500)
            await page.screenshot(path=str(OUTPUT), full_page=True)
        finally:
            await browser.close()


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    print("Subindo Streamlit…")
    with tempfile.TemporaryFile() as log_file:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(DASHBOARD),
                "--server.headless",
                "true",
                "--server.port",
                "8501",
            ],
            cwd=ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
        try:
            _wait_streamlit_ready(process, log_file)
            print("Aguardando renderização e capturando…")
            asyncio.run(_capture())
            print(f"Screenshot salvo em: {OUTPUT.relative_to(ROOT)}")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
