import 'fake-indexeddb/auto';
import { IDBFactory } from 'fake-indexeddb';
import { beforeEach, describe, expect, it } from 'vitest';

import { enqueueOracleQuery, listUnsyncedEntries, markEntrySynced } from './db';

const query = (text: string) => ({ query: text, sessionHistory: [] });

describe('offline queue', () => {
  beforeEach(() => {
    // A new in-memory database per test, so no entry leaks between cases.
    globalThis.indexedDB = new IDBFactory();
  });

  it('stores an enqueued query as unsynced and lists it', async () => {
    const entry = await enqueueOracleQuery(query('first'));

    expect(entry).toMatchObject({ kind: 'oracle-query', payload: query('first'), synced: false });
    expect(await listUnsyncedEntries()).toEqual([entry]);
  });

  it('lists pending queries in the order they were enqueued', async () => {
    for (const text of ['first', 'second', 'third']) await enqueueOracleQuery(query(text));

    const pending = await listUnsyncedEntries();

    expect(pending.map((entry) => (entry.payload as { query: string }).query)).toEqual(['first', 'second', 'third']);
    expect(pending.map((entry) => entry.queueOrder)).toEqual([1, 2, 3]);
  });

  it('drops a synced entry from the pending list and keeps the rest in order', async () => {
    const first = await enqueueOracleQuery(query('first'));
    const second = await enqueueOracleQuery(query('second'));
    const third = await enqueueOracleQuery(query('third'));

    await markEntrySynced(second);

    expect(await listUnsyncedEntries()).toEqual([first, third]);
  });
});