import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import React from 'react';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type {
  OfflineLogEntry,
  OracleProposeRequest,
  OracleQueryPayload,
  OracleResponseChunk,
} from '../../types/domain';
import {
  enqueueErrorReport,
  enqueueOracleQuery,
  listUnsyncedEntries,
  markEntrySynced,
} from '../../lib/db';
import { readOracleStream } from './sse';
import './oracle-terminal.css';

type Locale = 'en' | 'es';
type StreamSegment = OracleResponseChunk & { key: string };

interface Exchange {
  id: string;
  query: string;
  contextTag?: string;
  segments: StreamSegment[];
  state: 'streaming' | 'complete' | 'queued' | 'error';
  notice?: string;
  proposalState?: 'saving' | 'saved' | 'error';
}

interface Props {
  locale: Locale;
}

function sameCitations(left?: string[], right?: string[]): boolean {
  return (left ?? []).join('\u0000') === (right ?? []).join('\u0000');
}

export function appendChunk(segments: StreamSegment[], chunk: OracleResponseChunk): StreamSegment[] {
  const previous = segments.at(-1);
  if (previous && previous.mode === chunk.mode && sameCitations(previous.citedQuoteIds, chunk.citedQuoteIds)) {
    return [...segments.slice(0, -1), { ...previous, text: previous.text + chunk.text }];
  }
  return [...segments, { ...chunk, key: identifier() }];
}

const COPY = {
  en: {
    eyebrow: 'Local oracle', title: 'Ask the Tao', open: 'Open oracle', close: 'Close oracle',
    placeholder: 'Ask about your development practice…', submit: 'Ask', streaming: 'Listening…',
    grounded: 'Grounded in the TTOD corpus', creative: 'Creative reflection — not sourced from a TTOD quote',
    queued: 'The oracle is unreachable. Your query is safely queued on this device.',
    queueError: 'The oracle is unreachable and this browser could not open its offline queue.',
    syncing: 'Retrying queued queries…', propose: 'Save as a draft proposal', proposing: 'Saving draft…',
    proposed: 'Saved as a draft proposal. The current human acceptance path is not yet operational.',
    proposalError: 'The draft proposal could not be saved.', retryError: 'A queued query could not be retried yet.',
    context: 'Context tag', hint: 'Alt+Shift+O opens · Ctrl/⌘+Enter asks · Esc closes',
  },
  es: {
    eyebrow: 'Oráculo local', title: 'Pregunta al Tao', open: 'Abrir oráculo', close: 'Cerrar oráculo',
    placeholder: 'Pregunta sobre tu práctica de desarrollo…', submit: 'Preguntar', streaming: 'Escuchando…',
    grounded: 'Fundamentado en el corpus TTOD', creative: 'Reflexión creativa — no procede de una cita TTOD',
    queued: 'El oráculo no está disponible. Tu consulta queda guardada en este dispositivo.',
    queueError: 'El oráculo no está disponible y el navegador no pudo abrir la cola sin conexión.',
    syncing: 'Reintentando consultas guardadas…', propose: 'Guardar como borrador de propuesta', proposing: 'Guardando borrador…',
    proposed: 'Guardada como borrador de propuesta. La vía actual de aceptación humana aún no está operativa.',
    proposalError: 'No se pudo guardar el borrador.', retryError: 'Todavía no se pudo reintentar una consulta guardada.',
    context: 'Etiqueta de contexto', hint: 'Alt+Mayús+O abre · Ctrl/⌘+Intro pregunta · Esc cierra',
  },
} as const;

const identifier = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;

class UnreachableOracleError extends Error {}

function currentContextTag(): string | undefined {
  if (typeof window === 'undefined') return undefined;
  const value = new URL(window.location.href).searchParams.get('tag')?.trim();
  return value || undefined;
}

function historyFrom(exchanges: Exchange[]): string[] {
  return exchanges
    .filter((exchange) => exchange.state === 'complete')
    .flatMap((exchange) => [
      `Human: ${exchange.query}`,
      `Oracle: ${exchange.segments.map((segment) => segment.text).join('')}`,
    ])
    .slice(-50);
}

export default function OracleTerminal({ locale }: Props) {
  const copy = COPY[locale];
  const reduceMotion = useReducedMotion();
  const [open, setOpen] = useState(true);
  const [query, setQuery] = useState('');
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [syncing, setSyncing] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const exchangesRef = useRef(exchanges);
  const syncingRef = useRef(false);
  exchangesRef.current = exchanges;

  const updateExchange = useCallback((id: string, update: (exchange: Exchange) => Exchange) => {
    setExchanges((current) => current.map((exchange) => exchange.id === id ? update(exchange) : exchange));
  }, []);

  const sendPayload = useCallback(async (payload: OracleQueryPayload, queuedEntry?: OfflineLogEntry) => {
    const id = identifier();
    setExchanges((current) => [...current, {
      id, query: payload.query, contextTag: payload.contextTag, segments: [], state: 'streaming',
    }]);
    let received = 0;
    try {
      const response = await fetch('/api/v1/oracle/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const message = `Oracle stream failed (${response.status})`;
        if (response.status >= 500) throw new UnreachableOracleError(message);
        throw new Error(message);
      }
      received = await readOracleStream(response, (chunk) => {
        updateExchange(id, (exchange) => ({
          ...exchange,
          segments: appendChunk(exchange.segments, chunk),
        }));
      });
      if (received === 0) throw new Error('Oracle stream completed without an answer');
      updateExchange(id, (exchange) => ({ ...exchange, state: 'complete' }));
      if (queuedEntry) await markEntrySynced(queuedEntry);
      return true;
    } catch (error) {
      const unreachable = error instanceof UnreachableOracleError || error instanceof TypeError;
      if (received === 0 && !queuedEntry && unreachable) {
        try {
          await enqueueOracleQuery(payload);
          updateExchange(id, (exchange) => ({ ...exchange, state: 'queued', notice: copy.queued }));
        } catch {
          updateExchange(id, (exchange) => ({ ...exchange, state: 'error', notice: copy.queueError }));
        }
      } else {
        const message = error instanceof Error ? error.message : String(error);
        await enqueueErrorReport(message).catch(() => undefined);
        updateExchange(id, (exchange) => ({
          ...exchange, state: 'error', notice: queuedEntry ? copy.retryError : message,
        }));
      }
      return false;
    }
  }, [copy.queueError, copy.queued, copy.retryError, updateExchange]);

  const flushQueue = useCallback(async () => {
    if (syncingRef.current || typeof navigator === 'undefined' || !navigator.onLine) return;
    syncingRef.current = true;
    setSyncing(true);
    try {
      const entries = await listUnsyncedEntries();
      for (const entry of entries) {
        if (entry.kind === 'oracle-query') {
          const succeeded = await sendPayload(entry.payload as OracleQueryPayload, entry);
          if (!succeeded) break;
        }
      }
    } catch {
      // A private-mode/browser IndexedDB failure must not break the terminal or online requests.
    } finally {
      syncingRef.current = false;
      setSyncing(false);
    }
  }, [sendPayload]);

  useEffect(() => {
    const onOnline = () => void flushQueue();
    window.addEventListener('online', onOnline);
    if (navigator.onLine) void flushQueue();
    return () => window.removeEventListener('online', onOnline);
  }, []); // The online listener deliberately binds once; flushQueue reads the durable queue.

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.altKey && event.shiftKey && !event.ctrlKey && !event.metaKey && event.key.toLowerCase() === 'o') {
        event.preventDefault();
        setOpen(true);
        requestAnimationFrame(() => inputRef.current?.focus());
      } else if (event.key === 'Escape' && open) {
        setOpen(false);
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [open]);

  const busy = useMemo(() => exchanges.some((exchange) => exchange.state === 'streaming'), [exchanges]);

  const submit = async () => {
    const trimmed = query.trim();
    if (!trimmed || busy) return;
    const payload: OracleQueryPayload = {
      query: trimmed,
      contextTag: currentContextTag(),
      sessionHistory: historyFrom(exchangesRef.current),
    };
    setQuery('');
    await sendPayload(payload);
  };

  const propose = async (exchange: Exchange) => {
    const creativeAnswer = exchange.segments
      .filter((segment) => segment.mode === 'creative')
      .map((segment) => segment.text)
      .join('');
    if (!creativeAnswer || exchange.proposalState === 'saving') return;
    updateExchange(exchange.id, (item) => ({ ...item, proposalState: 'saving' }));
    const body: OracleProposeRequest = { query: exchange.query, creativeAnswer };
    try {
      const response = await fetch('/api/v1/oracle/propose', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error(`Proposal request failed (${response.status})`);
      updateExchange(exchange.id, (item) => ({ ...item, proposalState: 'saved' }));
    } catch (error) {
      await enqueueErrorReport(error instanceof Error ? error.message : String(error)).catch(() => undefined);
      updateExchange(exchange.id, (item) => ({ ...item, proposalState: 'error' }));
    }
  };

  return (
    <section className="oracle-shell" aria-label={copy.title}>
      <button className="oracle-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        {open ? copy.close : copy.open}
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className="oracle-terminal"
            initial={reduceMotion ? false : { opacity: 0, y: 18, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={reduceMotion ? { opacity: 0 } : { opacity: 0, y: 12, scale: 0.99 }}
            transition={{ duration: reduceMotion ? 0 : 0.22 }}
          >
            <header><span>{copy.eyebrow}</span><h1>{copy.title}</h1></header>
            <div className="oracle-log" aria-live="polite" aria-busy={busy}>
              <AnimatePresence initial={false}>
                {exchanges.map((exchange) => (
                  <motion.article key={exchange.id} className="oracle-exchange" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <p className="oracle-query"><strong>›</strong> {exchange.query}</p>
                    {exchange.contextTag && <p className="oracle-context">{copy.context}: <code>{exchange.contextTag}</code></p>}
                    {exchange.segments.map((segment) => (
                      <div key={segment.key} className={`oracle-segment oracle-${segment.mode}`}>
                        <strong className="oracle-mode">{segment.mode === 'grounded' ? copy.grounded : copy.creative}</strong>
                        <p>{segment.text}</p>
                        {segment.mode === 'grounded' && segment.citedQuoteIds?.length ? (
                          <ul className="oracle-citations" aria-label={copy.grounded}>
                            {segment.citedQuoteIds.map((id) => <li key={id}><a href={`/${locale}/wisdom/${id}`}>{id}</a></li>)}
                          </ul>
                        ) : null}
                      </div>
                    ))}
                    {exchange.state === 'streaming' && <p className="oracle-status">{copy.streaming}</p>}
                    {exchange.notice && <p className="oracle-notice" role="status">{exchange.notice}</p>}
                    {exchange.state === 'complete' && exchange.segments.some((segment) => segment.mode === 'creative') && (
                      <div className="oracle-proposal">
                        <button type="button" onClick={() => void propose(exchange)} disabled={exchange.proposalState === 'saving' || exchange.proposalState === 'saved'}>
                          {exchange.proposalState === 'saving' ? copy.proposing : copy.propose}
                        </button>
                        {exchange.proposalState === 'saved' && <p role="status">{copy.proposed}</p>}
                        {exchange.proposalState === 'error' && <p role="alert">{copy.proposalError}</p>}
                      </div>
                    )}
                  </motion.article>
                ))}
              </AnimatePresence>
              {syncing && <p className="oracle-status">{copy.syncing}</p>}
            </div>
            <form onSubmit={(event) => { event.preventDefault(); void submit(); }}>
              <label className="sr-only" htmlFor="oracle-query">{copy.placeholder}</label>
              <textarea
                id="oracle-query" ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => {
                  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                    event.preventDefault();
                    void submit();
                  }
                }}
                placeholder={copy.placeholder} rows={3} maxLength={8000}
              />
              <button type="submit" disabled={!query.trim() || busy}>{copy.submit}</button>
            </form>
            <p className="oracle-hint">{copy.hint}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
