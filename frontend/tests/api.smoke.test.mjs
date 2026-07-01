/** Frontend API client smoke tests (Node, no browser). */
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(fileURLToPath(import.meta.url));
const apiSource = readFileSync(join(root, '../src/api.js'), 'utf8');

assert.match(apiSource, /export const rankCandidates/);
assert.match(apiSource, /export const exportRankingsUrl/);
assert.match(apiSource, /VITE_API_BASE/);

console.log('frontend api smoke tests passed');
