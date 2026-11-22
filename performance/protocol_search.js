import http from 'k6/http';
import { check, sleep } from 'k6';

// This is only a protocol test: it never opens a web browser or runs search.js.
const BASE_URL = (__ENV.BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export const options = {
  vus: 5,
  duration: '12s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
    http_req_duration: ['p(95)<2000'],
  },
};

export default function () {
  const response = http.get(`${BASE_URL}/protocol-demo/api/search?q=laptop`, {
    tags: { business_action: 'search' },
  });
  check(response, {
    'HTTP 200': (r) => r.status === 200,
    'correct search results': (r) => {
      try {
        const body = r.json();
        return body.query === 'laptop' && body.total === 3 && body.results.length === 3;
      } catch (_error) {
        return false;
      }
    },
  });
  sleep(0.2);
}
