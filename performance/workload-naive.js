import {
    browseJourney,
    searchJourney,
    checkoutJourney,
} from './workload-common.js';


export const options = {
    scenarios: {
        browse: {
            executor: 'constant-vus',
            exec: 'browse',
            vus: 7,
            duration: '60s',
            gracefulStop: '0s',
        },

        search: {
            executor: 'constant-vus',
            exec: 'search',
            vus: 2,
            duration: '60s',
            gracefulStop: '0s',
        },

        checkout: {
            executor: 'constant-vus',
            exec: 'checkout',
            vus: 1,
            duration: '60s',
            gracefulStop: '0s',
        },
    },
};


export function browse() {
    browseJourney();
}

export function search() {
    searchJourney();
}

export function checkout() {
    checkoutJourney();
}