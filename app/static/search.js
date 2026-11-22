/* Browser-only demo. The slow flag is never sent to the API. */
const params = new URLSearchParams(window.location.search);
const slowMode = params.get('slow') === '1';
const EXTRA_CLIENT_WORK_MS = 900;

const form = document.getElementById('search-form');
const input = document.getElementById('search-input');
const button = document.getElementById('search-button');
const status = document.getElementById('status');
const output = document.getElementById('search-results');
const list = document.getElementById('results-list');

const activeLink = document.getElementById(slowMode ? 'slow-link' : 'normal-link');
activeLink.classList.add('active');
activeLink.setAttribute('aria-current', 'page');

function blockBrowserMainThread(milliseconds) {
  // Intentional long task. No network or server-side delay is introduced.
  const until = performance.now() + milliseconds;
  while (performance.now() < until) {
    Math.sqrt(144); // representative, deliberately wasteful client-side work
  }
}

function renderResults(results) {
  list.replaceChildren();
  for (const product of results) {
    const row = document.createElement('article');
    row.className = 'result-row';
    const details = document.createElement('div');
    const name = document.createElement('strong');
    name.textContent = product.name;
    const category = document.createElement('small');
    category.textContent = product.category;
    details.append(name, category);
    const price = document.createElement('span');
    price.className = 'price';
    price.textContent = `$${product.price}`;
    row.append(details, price);
    list.append(row);
  }
  document.getElementById('result-count').textContent = `${results.length} items`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (!query) return;

  const start = performance.now();
  button.disabled = true;
  status.textContent = 'Searching…';
  output.hidden = true;
  window.__lastSearchTiming = null;

  try {
    const response = await fetch(`/protocol-demo/api/search?q=${encodeURIComponent(query)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const responseReceived = performance.now();

    if (slowMode) blockBrowserMainThread(EXTRA_CLIENT_WORK_MS);
    const clientWorkFinished = performance.now();

    renderResults(data.results);
    const domUpdated = performance.now();
    document.getElementById('fetch-time').textContent = `${(responseReceived - start).toFixed(1)} ms`;
    document.getElementById('frontend-time').textContent = `${(clientWorkFinished - responseReceived).toFixed(1)} ms`;
    document.getElementById('total-time').textContent = `${(domUpdated - start).toFixed(1)} ms`;
    output.hidden = false;
    status.textContent = `Completed: ${data.total} matching items.`;

    // Intentionally not a paint metric; this timestamp marks the DOM update.
    window.__lastSearchTiming = {
      mode: slowMode ? 'slow' : 'normal',
      fetchAndJsonMs: responseReceived - start,
      frontendWorkMs: clientWorkFinished - responseReceived,
      clickToDomUpdateMs: domUpdated - start,
      resultCount: data.total,
    };
  } catch (error) {
    status.textContent = `Search failed: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});
