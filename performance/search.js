import http from 'k6/http';
import { check } from 'k6';


export const options = {
    vus: 5,
    duration: '10s',

    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.01'],
    },
};


export default function () {
    const response = http.get('http://127.0.0.1:8000/api/search');

    check(response, {
        'status is 200': (r) => r.status === 200,
    });
}