import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import React from 'react';
import { useCallback, useMemo, useRef, useState } from 'react';

import type { Locale, OracleQueryPayload, OracleResponseChunk } from '../../types/domain';
import { readOracleStream } from './sse';
import './oracle-terminal.css';

type StreamSegment = OracleResponseChunk & { key: string };

interface Exchange {
  id: string;
  query: string;
  contextTag?: string;
  segments: StreamSegment[];
  state: 'streaming' | 'complete' | 'error';
  notice?: string;
}

interface Props {
  locale: Locale;
}

function sameList(left?: string[], right?: string[]): boolean {
  return (left ?? []).join('\u0000') === (right ?? []).join('\u0000');
}

export function appendChunk(segments: StreamSegment[], chunk: OracleResponseChunk): StreamSegment[] {
  const previous = segments.at(-1);
  if (
    previous &&
    previous.mode === chunk.mode &&
    sameList(previous.citedQuoteIds, chunk.citedQuoteIds) &&
    sameList(previous.themes, chunk.themes) &&
    sameList(previous.tags, chunk.tags)
  ) {
    return [...segments.slice(0, -1), { ...previous, text: previous.text + chunk.text }];
  }
  return [...segments, { ...chunk, key: identifier() }];
}

const COPY = {
  en: {
    eyebrow: 'Local oracle', title: 'Ask the Tao',
    placeholder: 'Bring a practice question — the Oracle answers with wisdom, not fixes…', submit: 'Ask', streaming: 'Listening…',
    grounded: 'Grounded in the TTOD corpus', creative: 'Oracular voice — no strong TTOD match',
    context: 'Context tag', hint: 'Ctrl/⌘+Enter asks',
  },
  es: {
    eyebrow: 'Oráculo local', title: 'Pregunta al Tao',
    placeholder: 'Trae una pregunta de práctica — el Oráculo responde con sabiduría, no con parches…', submit: 'Preguntar', streaming: 'Escuchando…',
    grounded: 'Fundamentado en el corpus TTOD', creative: 'Voz oracular — sin coincidencia fuerte en TTOD',
    context: 'Etiqueta de contexto', hint: 'Ctrl/⌘+Intro pregunta',
  },
} as const;

const identifier = () => globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;

function currentContextTag(): string | undefined {
  if (typeof window === 'undefined') return undefined;
  const value = new URL(window.location.href).searchParams.get('tag')?.trim();
  return value || undefined;
}

export default function OracleTerminal({ locale }: Props) {
  const copy = COPY[locale];
  const reduceMotion = useReducedMotion();
  const [query, setQuery] = useState('');
  const [exchange, setExchange] = useState<Exchange | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const sendPayload = useCallback(async (payload: OracleQueryPayload) => {
    const id = identifier();
    setExchange({
      id, query: payload.query, contextTag: payload.contextTag, segments: [], state: 'streaming',
    });
    let received = 0;
    try {
      const response = await fetch('/api/v1/oracle/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Oracle stream failed (${response.status})`);
      }
      received = await readOracleStream(response, (chunk) => {
        setExchange((current) => {
          if (!current || current.id !== id) return current;
          return { ...current, segments: appendChunk(current.segments, chunk) };
        });
      });
      if (received === 0) throw new Error('Oracle stream completed without an answer');
      setExchange((current) => current?.id === id ? { ...current, state: 'complete' } : current);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setExchange((current) => current?.id === id ? { ...current, state: 'error', notice: message } : current);
    }
  }, []);

  const busy = useMemo(() => exchange?.state === 'streaming', [exchange]);

  const submit = async () => {
    const trimmed = query.trim();
    if (!trimmed || busy) return;
    const payload: OracleQueryPayload = {
      query: trimmed,
      contextTag: currentContextTag(),
      sessionHistory: [],
      locale,
    };
    setQuery('');
    await sendPayload(payload);
  };

  return (
    <section className="oracle-shell" aria-label={copy.title}>
      <motion.div
        className="oracle-terminal"
        initial={reduceMotion ? false : { opacity: 0, y: 18, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: reduceMotion ? 0 : 0.22 }}
      >
        <header><span>{copy.eyebrow}</span><h1>{copy.title}</h1></header>
        <div className="oracle-log" aria-live="polite" aria-busy={busy}>
          <AnimatePresence initial={false}>
            {exchange && (
              <motion.article
                key={exchange.id}
                className="oracle-exchange"
                initial={reduceMotion ? false : { opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: reduceMotion ? 0 : 0.22 }}
              >
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
              </motion.article>
            )}
          </AnimatePresence>
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
    </section>
  );
}
