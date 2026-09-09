// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import OracleTerminal from './OracleTerminal';

const queueMocks = vi.hoisted(() => ({
  enqueueErrorReport: vi.fn(async () => undefined),
  enqueueOracleQuery: vi.fn(async () => undefined),
  listUnsyncedEntries: vi.fn(async () => []),
  markEntrySynced: vi.fn(async () => undefined),
}));

vi.mock('../../lib/db', () => queueMocks);
vi.mock('framer-motion', async () => {
  const React = await import('react');
  const component = React.forwardRef<HTMLElement, React.PropsWithChildren<Record<string, unknown>>>((props, ref) => {
    const { children, initial: _initial, animate: _animate, exit: _exit, transition: _transition, ...rest } = props;
    return React.createElement('div', { ...rest, ref }, children as React.ReactNode);
  });
  return { AnimatePresence: ({ children }: { children: React.ReactNode }) => children, motion: { div: component, article: component }, useReducedMotion: () => true };
});

function sseResponse(chunks: unknown[]): Response {
  return new Response(chunks.map((chunk) => `data: ${JSON.stringify(chunk)}\n\n`).join(''), {
    status: 200, headers: { 'Content-Type': 'text/event-stream' },
  });
}

describe('OracleTerminal governance and URL context', () => {
  afterEach(() => cleanup());
  beforeEach(() => {
    vi.clearAllMocks();
    window.history.replaceState({}, '', '/en/oracle?tag=simplicity');
  });

  it('discloses creative mode, reads tag at submission, and proposes only after an explicit click', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(sseResponse([{
        mode: 'creative', text: 'A new reflection.', themes: ['wisdom'], tags: ['simplicity'],
      }]))
      .mockResolvedValueOnce(new Response(JSON.stringify({ status: 'proposed' }), { status: 201 }));
    vi.stubGlobal('fetch', fetchMock);
    render(<OracleTerminal locale="en" />);

    fireEvent.change(screen.getByPlaceholderText(/practice question/), { target: { value: 'How should I simplify?' } });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));

    expect(await screen.findByText('Oracular voice — no strong TTOD match')).toBeVisible();
    expect(screen.getByText(/Thematic anchors/)).toBeVisible();
    expect(screen.getByText('wisdom')).toBeVisible();
    expect(screen.queryByLabelText('Grounded in the TTOD corpus')).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toMatchObject({
      contextTag: 'simplicity', locale: 'en',
    });

    fireEvent.click(screen.getByRole('button', { name: 'Save as a draft proposal' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({
      query: 'How should I simplify?',
      creativeAnswer: 'A new reflection.',
      locale: 'en',
      suggestedTags: ['simplicity'],
      suggestedSection: 'wisdom',
    });
    expect(await screen.findByText(/Saved as a draft proposal/)).toHaveTextContent('acceptance path is not yet operational');
  });

  it('renders grounded citations without exposing the proposal action', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(sseResponse([
      { mode: 'grounded', citedQuoteIds: ['wis-001'], text: 'Grounded answer.', themes: ['wisdom'], tags: ['simplicity'] },
    ])));
    render(<OracleTerminal locale="en" />);
    fireEvent.change(screen.getByPlaceholderText(/practice question/), { target: { value: 'A grounded question' } });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText('Grounded in the TTOD corpus')).toBeVisible();
    expect(screen.getByRole('link', { name: 'wis-001' })).toHaveAttribute('href', '/en/wisdom/wis-001');
    expect(screen.queryByRole('button', { name: /draft proposal/ })).not.toBeInTheDocument();
  });

  it('queues an unreachable query instead of using an alternate inference path', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network unavailable')));
    render(<OracleTerminal locale="en" />);
    fireEvent.change(screen.getByPlaceholderText(/practice question/), { target: { value: 'Queue this' } });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText(/safely queued on this device/)).toBeVisible();
    expect(queueMocks.enqueueOracleQuery).toHaveBeenCalledWith(expect.objectContaining({
      query: 'Queue this', contextTag: 'simplicity', sessionHistory: [], locale: 'en',
    }));
  });
});
