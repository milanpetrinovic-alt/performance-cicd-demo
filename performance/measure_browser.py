"""Measure browser-observed click-to-results visibility in both UI modes.

Usage:
    python performance/measure_browser.py
    python performance/measure_browser.py --headed --runs 6

A locator becoming visible is NOT a standard paint or Core Web Vitals metric.
"""

import argparse
import json
import math
import os
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

DEFAULT_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_OUTPUT = Path("performance/browser-results.json")


def percentile_nearest_rank(values, percentage):
    numbers = sorted(values)
    if not numbers:
        raise ValueError("Cannot calculate a percentile without samples")
    index = max(0, math.ceil((percentage / 100) * len(numbers)) - 1)
    return round(numbers[index], 2)


def browser_sample(page, base_url: str, mode: str):
    slow = mode == "slow"
    page.goto(f"{base_url}/protocol-demo?slow={1 if slow else 0}", wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Search products").fill("laptop")
    started = time.perf_counter()
    page.get_by_role("button", name="Search").click()
    page.get_by_test_id("search-results").wait_for(state="visible", timeout=8_000)
    visible_ms = (time.perf_counter() - started) * 1_000
    assert "Laptop Pro 14" in page.get_by_test_id("search-results").inner_text()

    timing = page.evaluate("window.__lastSearchTiming")
    if not timing or timing.get("resultCount") != 3 or timing.get("mode") != mode:
        raise RuntimeError(f"UI did not complete the intended {mode} search")
    return {
        "click_to_visible_ms": round(visible_ms, 2),
        "browser_fetch_and_json_ms": round(timing["fetchAndJsonMs"], 2),
        "deliberate_frontend_work_ms": round(timing["frontendWorkMs"], 2),
        "click_to_dom_update_ms": round(timing["clickToDomUpdateMs"], 2),
    }


def run(base_url: str, runs: int, headed: bool, output: Path):
    if runs < 3:
        raise ValueError("Use at least 3 measured runs per mode")

    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "method": "One Chromium browser; fresh page per observation; first sample per mode is warm-up and excluded.",
        "warning": "Click-to-visible is a Playwright observation, not a standardized browser paint metric.",
        "modes": {},
    }

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=not headed,
            executable_path=os.getenv("CHROMIUM_EXECUTABLE") or None,
        )
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        try:
            for mode in ("normal", "slow"):
                # Warm up browser resources, connection and JS cache.
                warmup = context.new_page()
                try:
                    browser_sample(warmup, base_url, mode)
                finally:
                    warmup.close()

                samples = []
                for index in range(runs):
                    page = context.new_page()
                    try:
                        result = browser_sample(page, base_url, mode)
                        samples.append(result)
                        print(f"{mode:6} run {index + 1}/{runs}: {result['click_to_visible_ms']:7.1f} ms")
                    except PlaywrightTimeoutError as exc:
                        raise RuntimeError(f"Browser search did not finish in {mode} mode") from exc
                    finally:
                        page.close()

                click_samples = [sample["click_to_visible_ms"] for sample in samples]
                frontend_samples = [sample["deliberate_frontend_work_ms"] for sample in samples]
                report["modes"][mode] = {
                    "sample_count": len(samples),
                    "median_click_to_visible_ms": round(statistics.median(click_samples), 2),
                    "p95_click_to_visible_ms": percentile_nearest_rank(click_samples, 95),
                    "median_frontend_work_ms": round(statistics.median(frontend_samples), 2),
                    "samples": samples,
                }
        finally:
            browser.close()

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {output}")
    for mode, result in report["modes"].items():
        print(f"{mode.title():6} median click-to-visible: {result['median_click_to_visible_ms']:7.1f} ms")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Playwright browser timing for protocol-level workshop")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--runs", type=int, default=7, help="measured samples per mode (plus one warm-up)")
    parser.add_argument("--headed", action="store_true", help="show a Chromium window")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.base_url.rstrip("/"), args.runs, args.headed, args.output)
