# Workshop 03 — Protocol-level scripting vs browser automation

**Point of the demo:** A successful API load test does not prove that the frontend feels fast. One user Search action can be executed at different layers, and each layer observes a different time interval.

## One-time integration into your existing repository

The overlay files are **additive**: they do not replace your existing `app/main.py`, `requirements.txt`, GitHub workflows or earlier workshop scripts.

1. In your existing `performance-cicd-demo` repository, branch from `main`:

   ```bash
   git switch main
   git pull origin main
   git switch -c protocol-vs-browser
   ```

2. Copy all the overlay files into the repository root, preserving subfolders.

3. In your existing `app/main.py`, insert these **two lines immediately after `app = FastAPI(...)` has been initialized** (after the whole constructor call, if multiline):

   ```python
   from app.protocol_demo import router as protocol_demo_router
   app.include_router(protocol_demo_router)
   ```

   This adds `/protocol-demo` and `/protocol-demo/api/search` while preserving your original `/api/search` contract.

4. Recommended `.gitignore` additions:

   ```gitignore
   # Protocol vs Browser workshop measurements
   performance/browser-results.json
   performance/api-summary.json
   performance/protocol-browser-report.html
   ```

   Add the snippet **to** your existing `.gitignore`; do not overwrite that file.

5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   python -m pip install -r requirements-protocol-demo.txt
   python -m playwright install chromium
   ```

   k6 must also be installed locally to run the HTTP measurements.

## Local live demonstration

Open one terminal and start FastAPI:

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/protocol-demo** in Chrome.

**Part A — Discover the request.** In DevTools → Network, clear the log and filter Fetch/XHR. Search for `laptop`. Inspect `GET /protocol-demo/api/search?q=laptop`: method, query string, status, response JSON and timing. Notice the frontend's result cards appear only after JavaScript handles the response.

**Part B — Same operation, different layer.** Open `tests/test_protocol_demo.py` (HTTP functional checks), `performance/measure_browser.py` (Playwright in Chromium), and `performance/protocol_search.js` (k6 HTTP). Explain that Playwright observes Search + visible results, while k6 sees only the HTTP response.

**Part C — Reveal the blind spot.** Change the UI mode using the Normal / Slow buttons. Run the same search. In Slow UI mode, `search.js` deliberately blocks the main thread **after** receiving exactly the same JSON; the API has no artificial delay. DevTools Network timing stays focused on the request; the visible page is slower. Chrome DevTools → Performance can show the long JavaScript task.

**Measure and report:** With the server running, in another terminal run:

```bash
python performance/measure_browser.py --runs 7
k6 run --summary-export=performance/api-summary.json performance/protocol_search.js
python performance/compare_layers.py
```

Open `performance/protocol-browser-report.html` in a browser. It shows a **single** k6 HTTP measurement (the API endpoint is identical for both modes), and independent browser click-to-visible measurements in normal and slow UI modes.

Optional: `python performance/measure_browser.py --headed --runs 3` makes browser automation visible. You can inspect the operating system's Task Manager or Chrome Task Manager for browser processes. Do **not** claim a universal browser-to-k6 RAM/CPU ratio without a controlled experiment.

To run the synthetic demo endpoint checks while FastAPI is running:

```bash
python -m pytest -q tests/test_protocol_demo.py
```

## GitHub Actions

The `protocol-vs-browser` branch includes `.github/workflows/protocol-demo.yml`. Commit and push your branch:

```bash
 git add .
 git commit -m "Add browser vs protocol performance workshop demo"
 git push -u origin protocol-vs-browser
```

If the workflow does not show under **Actions**, GitHub requires a workflow with `workflow_dispatch` to be present on the repository's default branch. Follow the approach we used for workshop 02: create a tiny **placeholder with the same workflow filename** on `main` (example below). **Do not merge the new branch into main.** Then open Actions → Protocol vs Browser Demo → Run workflow → choose `protocol-vs-browser` → Run workflow.

Placeholder for **main only**:

```yaml
name: Protocol vs Browser Demo
on:
  workflow_dispatch:
jobs:
  instructions:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Choose protocol-vs-browser branch to run the complete workshop demo."
```

On the **protocol-vs-browser** branch, the workflow is complete: installs Chromium, starts FastAPI, runs tests, collects browser measurements, runs k6, generates an HTML report, and uploads `protocol-vs-browser-report` (HTML plus raw JSON data). The existing `main` CI/CD regression workflow is unaffected.

## What the numbers mean

- k6 HTTP request duration measures time at the protocol boundary, not rendering.
- Playwright click-to-visible measures how long this automation waited for the result element to become visible after the Search click. It is **not** a standardized browser paint or Core Web Vitals metric.
- The UI slow mode's +900 ms is deliberate **client-side** work. Browser-observed timings will vary depending on runner and machine, but the API route remains unchanged.
- Both UI modes should still show the same correct product data. Functional correctness, API latency and frontend responsiveness are three different questions.

**Safety:** All product data is synthetic; no authentication, real user records, private endpoints or recorded cookies are needed.
