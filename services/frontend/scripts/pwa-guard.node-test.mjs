// Explicit Node runner; the filename deliberately avoids Vitest's *.test glob.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';
import { changedFiles, checkContract, normalizeEnding } from './pwa-guard-core.mjs';

const frontend = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const domainPath = resolve(frontend, 'src/types/domain.ts');

test('accepts existing callers and additive optional domain fields', async () => {
  const source = await readFile(domainPath, 'utf8');
  const extended = source.replace('export interface OracleQueryPayload {', 'export interface OracleQueryPayload {\n  optionalFutureField?: string;');
  assert.deepEqual(checkContract(frontend, new Map([[domainPath, extended]])), []);
});

test('rejects a new required payload field even when current senders might compile', async () => {
  const source = await readFile(domainPath, 'utf8');
  const broken = source.replace('export interface OracleQueryPayload {', 'export interface OracleQueryPayload {\n  requiredFutureField: string;');
  assert(checkContract(frontend, new Map([[domainPath, broken]])).some((item) => item.file === 'contracts/pwa-queue.ts'));
});

test('rejects replacing the synced boolean and removing a public helper', async () => {
  const source = await readFile(domainPath, 'utf8');
  assert(checkContract(frontend, new Map([[domainPath, source.replace('synced: boolean;', 'synced: string;')]])).length > 0);
  const dbPath = resolve(frontend, 'src/lib/db.ts');
  const db = await readFile(dbPath, 'utf8');
  assert(checkContract(frontend, new Map([[dbPath, db.replace('export async function markEntrySynced', 'async function markEntrySynced')]])).length > 0);
});

test('format repair preserves literal whitespace and refuses malformed source', () => {
  const source = 'const message = `keep these spaces  \n  and these  `;\n\n  ';
  assert.equal(normalizeEnding('example.ts', source), 'const message = `keep these spaces  \n  and these  `;\n');
  const invalid = 'const message = `unfinished  \n\n';
  assert.equal(normalizeEnding('example.ts', invalid), invalid);
});

test('watch comparison detects additions, deletions and edits', () => {
  const before = new Map([['old.ts', 'a'], ['edit.ts', 'b'], ['same.ts', 'c']]);
  const after = new Map([['new.ts', 'd'], ['edit.ts', 'e'], ['same.ts', 'c']]);
  assert.deepEqual(changedFiles(before, after), ['edit.ts', 'new.ts', 'old.ts']);
});
