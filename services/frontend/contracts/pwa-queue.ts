// Compile-only consumer contract. These snapshots protect existing Team 3 callers;
// they are not a second set of application domain types.
import type { enqueueOracleQuery, listUnsyncedEntries, markEntrySynced } from '../src/lib/db';
import type { OfflineLogEntry, OracleQueryPayload } from '../src/types/domain';

type Assert<T extends true> = T;
type Equal<A, B> =
  (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2)
    ? (<T>() => T extends B ? 1 : 2) extends (<T>() => T extends A ? 1 : 2) ? true : false
    : false;

type ExistingCallerPayload = {
  query: string;
  contextTag?: string;
  sessionHistory: string[];
  locale?: 'en' | 'es';
};
type ExistingCallerEntry = {
  id: string;
  timestamp: string;
  kind: 'oracle-query' | 'error-report';
  payload: OracleQueryPayload | { errorLog: string };
  synced: boolean;
};

// Permit new optional fields, but preserve existing fields and old constructions.
export type PayloadFieldsRemainCompatible = Assert<Equal<
  Pick<OracleQueryPayload, keyof ExistingCallerPayload>, ExistingCallerPayload
>>;
export type OldPayloadsRemainAccepted = Assert<ExistingCallerPayload extends OracleQueryPayload ? true : false>;
export type EntryFieldsRemainCompatible = Assert<Equal<
  Pick<OfflineLogEntry, keyof ExistingCallerEntry>, ExistingCallerEntry
>>;
export type OldEntriesRemainAccepted = Assert<ExistingCallerEntry extends OfflineLogEntry ? true : false>;
export type QueueOrderRemainsOptional = Assert<Equal<Pick<OfflineLogEntry, 'queueOrder'>, { queueOrder?: number }>>;
export type EnqueueRemainsCompatible = Assert<Equal<
  typeof enqueueOracleQuery, (payload: OracleQueryPayload) => Promise<OfflineLogEntry>
>>;
export type ListRemainsCompatible = Assert<Equal<typeof listUnsyncedEntries, () => Promise<OfflineLogEntry[]>>>;
export type MarkSyncedRemainsCompatible = Assert<Equal<typeof markEntrySynced, (entry: OfflineLogEntry) => Promise<void>>>;
