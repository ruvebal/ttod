import type { OfflineLogEntry, OracleQueryPayload } from '../types/domain';

const DATABASE_NAME = 'ttod-oracle';
const DATABASE_VERSION = 2;
const STORE_NAME = 'offline-log';

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('IndexedDB is unavailable in this browser context'));
  }

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    let blocked = false;

    request.onupgradeneeded = () => {
      const database = request.result;
      const transaction = request.transaction!;
      const store = database.objectStoreNames.contains(STORE_NAME)
        ? transaction.objectStore(STORE_NAME)
        : database.createObjectStore(STORE_NAME, { keyPath: 'id' });

      if (!store.indexNames.contains('synced')) {
        store.createIndex('synced', 'synced', { unique: false });
      }

      if (!store.indexNames.contains('queueOrder')) {
        store.createIndex('queueOrder', 'queueOrder', { unique: true });
        const entriesRequest = store.getAll();
        entriesRequest.onsuccess = () => {
          const entries = (entriesRequest.result as OfflineLogEntry[]).sort(
            (left, right) =>
              left.timestamp.localeCompare(right.timestamp)
              || left.id.localeCompare(right.id),
          );
          entries.forEach((entry, index) => {
            store.put({ ...entry, queueOrder: index + 1 });
          });
        };
      }
    };

    request.onsuccess = () => {
      const database = request.result;
      // Release this connection when another tab requests a future upgrade.
      database.onversionchange = () => database.close();
      if (blocked) database.close();
      else resolve(database);
    };
    request.onerror = () => reject(request.error ?? new Error('Could not open the offline queue'));
    request.onblocked = () => {
      blocked = true;
      reject(new Error('Offline queue upgrade was blocked; close other TTOD tabs and reload'));
    };
  });
}

async function transact<T>(
  mode: IDBTransactionMode,
  operation: (store: IDBObjectStore, resolve: (value: T) => void, reject: (reason?: unknown) => void) => void,
): Promise<T> {
  const database = await openDatabase();
  return new Promise<T>((resolve, reject) => {
    let transaction: IDBTransaction;
    try {
      transaction = database.transaction(STORE_NAME, mode);
    } catch (error) {
      database.close();
      reject(error);
      return;
    }

    let result: T;
    let hasResult = false;

    transaction.oncomplete = () => {
      database.close();
      if (hasResult) resolve(result);
      else reject(new Error('Offline queue operation completed without a result'));
    };
    transaction.onerror = () => {
      reject(transaction.error ?? new Error('Offline queue transaction failed'));
    };
    transaction.onabort = () => {
      database.close();
      reject(transaction.error ?? new Error('Offline queue transaction was aborted'));
    };

    try {
      operation(transaction.objectStore(STORE_NAME), (value) => {
        result = value;
        hasResult = true;
      }, reject);
    } catch (error) {
      transaction.abort();
      reject(error);
    }
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
    const save = (queueOrder: number) => {
      const saved = { ...entry, queueOrder };
      const request = store.put(saved);
      request.onsuccess = () => resolve(saved);
      request.onerror = () => reject(request.error);
    };

    const existingRequest = store.get(entry.id);
    existingRequest.onerror = () => reject(existingRequest.error);
    existingRequest.onsuccess = () => {
      const existing = existingRequest.result as OfflineLogEntry | undefined;
      if (existing?.queueOrder !== undefined) {
        save(existing.queueOrder);
        return;
      }

      const lastRequest = store.index('queueOrder').openCursor(null, 'prev');
      lastRequest.onerror = () => reject(lastRequest.error);
      lastRequest.onsuccess = () => {
        const last = lastRequest.result?.value as OfflineLogEntry | undefined;
        save((last?.queueOrder ?? 0) + 1);
      };
    };
  });
}

export async function listUnsyncedEntries(): Promise<OfflineLogEntry[]> {
  return transact('readonly', (store, resolve, reject) => {
    const request = store.getAll();
    request.onsuccess = () => {
      const entries = (request.result as OfflineLogEntry[])
        .filter((entry) => entry.synced === false)
        .sort((left, right) => (left.queueOrder ?? 0) - (right.queueOrder ?? 0));
      resolve(entries);
    };
    request.onerror = () => reject(request.error);
  });
}

export async function markEntrySynced(entry: OfflineLogEntry): Promise<void> {
  await putEntry({ ...entry, synced: true });
}
