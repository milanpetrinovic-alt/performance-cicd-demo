import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

// Count completed business operations separately.
const browseOperations = new Counter('browse_operations');
const searchOperations = new Counter('search_operations');
const checkoutOperations = new Counter('checkout_operations');


function runJourney(name, endpoint, method, cycleSeconds, counter) {
    const start = Date.now();

    // Execute the business operation.
    const response = method === 'POST'
        ? http.post(`${BASE_URL}${endpoint}`, null)
        : http.get(`${BASE_URL}${endpoint}`);

    const successful = check(response, {
        [`${name} returns 200`]: (r) => r.status === 200,
    });

    if (successful) {
        counter.add(1);
    }

    // Keep the complete iteration close to the target cycle time.
    const elapsed = (Date.now() - start) / 1000;
    const remaining = cycleSeconds - elapsed;

    if (remaining > 0) {
        sleep(remaining);
    }
}


export function browseJourney() {
    runJourney('Browse', '/api/browse', 'GET', 1, browseOperations);
}


export function searchJourney() {
    runJourney('Search', '/api/search', 'GET', 2, searchOperations);
}


export function checkoutJourney() {
    runJourney('Checkout', '/api/checkout', 'POST', 4, checkoutOperations);
}