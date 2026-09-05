import type { OfflineLogEntry, OracleQueryPayload } from '../types/domain';

const DATABASE_NAME = 'ttod-oracle';
const DATABASE_VERSION = 1;
const STORE_NAME = 'offline-log';

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('IndexedDB is unavailable in this browser context'));
  }

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(STORE_NAME)) {
        const store = database.createObjectStore(STORE_NAME, { keyPath: 'id' });
        store.createIndex('synced', 'synced', { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error('Could not open the offline queue'));
    request.onblocked = () => reject(new Error('Offline queue upgrade was blocked'));
  });
}

async function transact<T>(
  mode: IDBTransactionMode,
  operation: (store: IDBObjectStore, resolve: (value: T) => void, reject: (reason?: unknown) => void) => void,
): Promise<T> {
  const database = await openDatabase();
  return new Promise<T>((resolve, reject) => {
    const transaction = database.transaction(STORE_NAME, mode);
    const store = transaction.objectStore(STORE_NAME);
    transaction.oncomplete = () => database.close();
    transaction.onerror = () => {
      database.close();
      reject(transaction.error ?? new Error('Offline queue transaction failed'));
    };
    transaction.onabort = transaction.onerror;
    operation(store, resolve, reject);
  });
}

function createEntry(
  kind: OfflineLogEntry['kind'],
  payload: OfflineLogEntry['payload'],
): OfflineLogEntry {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    timestamp: new Date().toISOString(),
    kind,
    payload,
    synced: false,
  };
}

export async function enqueueOracleQuery(payload: OracleQueryPayload): Promise<OfflineLogEntry> {
  return putEntry(createEntry('oracle-query', payload));
}

export async function enqueueErrorReport(errorLog: string): Promise<OfflineLogEntry> {
  return putEntry(createEntry('error-report', { errorLog }));
}

export async function putEntry(entry: OfflineLogEntry): Promise<OfflineLogEntry> {
  return transact('readwrite', (store, resolve, reject) => {
    const request = store.put(entry);
    request.onsuccess = () => resolve(entry);
    request.onerror = () => reject(request.error);
  });
}

export async function listUnsyncedEntries(): Promise<OfflineLogEntry[]> {
  return transact('readonly', (store, resolve, reject) => {
    const request = store.getAll();
    request.onsuccess = () => {
      const entries = (request.result as OfflineLogEntry[])
        .filter((entry) => entry.synced === false)
        .sort((left, right) => left.timestamp.localeCompare(right.timestamp));
      resolve(entries);
    };
    request.onerror = () => reject(request.error);
  });
}

export async function markEntrySynced(entry: OfflineLogEntry): Promise<void> {
  await putEntry({ ...entry, synced: true });
}

