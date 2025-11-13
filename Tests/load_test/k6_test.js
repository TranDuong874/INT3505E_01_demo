import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

/*
  k6 load test for the generated Flask server.

  Usage examples (pwsh):
    $env:TARGET = 'http://127.0.0.1:8080'
    $env:VUS = '50'
    $env:DURATION = '30s'
    k6 run Tests/load_test/k6_test.js

  Or with Docker (when running server on host):
    docker run --rm -i -v ${PWD}:/scripts -w /scripts loadimpact/k6 run Tests/load_test/k6_test.js

  The script loads sample payloads from ../integration_test/mock-data.json and performs a mix of
  list (GET /api/books), create (POST /api/books) and read-by-isbn (GET /api/books/{isbn}).
*/

// Configurable via environment variables
export let options = {
  vus: __ENV.VUS ? parseInt(__ENV.VUS) : 20,
  duration: __ENV.DURATION || '30s',
  thresholds: {
    // expect 95th percentile request time under 1s
    http_req_duration: ['p(95)<1000'],
    // expect error rate less than 5%
    http_req_failed: ['rate<0.05']
  }
};

const TARGET = __ENV.TARGET || 'http://127.0.0.1:8080';

// Load mock data once per test run
const mockData = new SharedArray('mockData', function () {
  // Path is relative to the repo root when running k6 from project folder
  return JSON.parse(open('../integration_test/mock-data.json'));
});

export default function () {
  // pick a random sample and make a unique ISBN to avoid 409 on duplicate runs
  const sample = mockData[Math.floor(Math.random() * mockData.length)];
  const uniqueIsbn = `${sample.test_bookISBN}-${Date.now()}-${Math.floor(Math.random() * 100000)}`;

  const createPayload = JSON.stringify({
    isbn: uniqueIsbn,
    book_name: sample.test_bookTitle,
    author: sample.test_bookAuthor
  });

  const useCache = (__ENV.USE_CACHE || 'false').toLowerCase() === 'true';
  const params = { headers: { 'Content-Type': 'application/json', 'X-Use-Cache': useCache ? 'true' : 'false' } };

  // 1) list books
  const listRes = http.get(`${TARGET}/api/books`, params);
  check(listRes, {
    'list returned 200': (r) => r.status === 200
  });

  // 2) create a book
  const createRes = http.post(`${TARGET}/api/books`, createPayload, params);
  check(createRes, {
    'create returned 201 or 409': (r) => r.status === 201 || r.status === 409
  });

  // 3) read by isbn
  const getRes = http.get(`${TARGET}/api/books/${encodeURIComponent(uniqueIsbn)}`, params);
  check(getRes, {
    'get by isbn returned 200 or 404': (r) => r.status === 200 || r.status === 404
  });

  // small pause
  sleep(1);
}
