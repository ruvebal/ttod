// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import OracleTerminal from './OracleTerminal';

vi.mock('framer-motion', async () => {
  const React = await import('react');
  const component = React.forwardRef<HTMLElement, React.PropsWithChildren<Record<string, unknown>>>((props, ref) => {
    const { children, initial: _initial, animate: _animate, exit: _exit, transition: _transition, ...rest } = props;
    return React.createElement('div', { ...rest, ref }, children as React.ReactNode);
  });
  return {
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
    motion: { div: component, article: component },
    useReducedMotion: () => true,
  };
});

function sseResponse(chunks: unknown[]): Response {
  return new Response(chunks.map((chunk) => `data: ${JSON.stringify(chunk)}\n\n`).join(''), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

describe('OracleTerminal hello-world stream', () => {
  afterEach(() => cleanup());
  beforeEach(() => {
    vi.clearAllMocks();
    window.history.replaceState({}, '', '/en/oracle?tag=simplicity');
  });

  it('streams a creative answer and sends the URL context tag once', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(
      sseResponse([{
        mode: 'creative',
        text: 'A new reflection.',
        themes: ['wisdom'],
        tags: ['simplicity'],
      }]),
    );
    vi.stubGlobal('fetch', fetchMock);
    render(<OracleTerminal locale="en" />);

    fireEvent.change(screen.getByPlaceholderText(/practice question/), {
      target: { value: 'How should I simplify?' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));

    expect(await screen.findByText('Oracular voice — no strong TTOD match')).toBeVisible();
    expect(screen.getByText('A new reflection.')).toBeVisible();
    expect(screen.getByText(/Context tag/)).toBeVisible();
    expect(screen.getByText('simplicity')).toBeVisible();
    expect(screen.queryByRole('button', { name: /draft proposal/ })).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toMatchObject({
      contextTag: 'simplicity',
      locale: 'en',
      query: 'How should I simplify?',
    });
  });

  it('renders grounded citations without a proposal action', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        sseResponse([
          {
            mode: 'grounded',
            citedQuoteIds: ['wis-001'],
            text: 'Grounded answer.',
            themes: ['wisdom'],
            tags: ['simplicity'],
          },
        ]),
      ),
    );
    render(<OracleTerminal locale="en" />);
    fireEvent.change(screen.getByPlaceholderText(/practice question/), {
      target: { value: 'A grounded question' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByText('Grounded in the TTOD corpus')).toBeVisible();
    expect(screen.getByRole('link', { name: 'wis-001' })).toHaveAttribute('href', '/en/wisdom/wis-001');
    expect(screen.queryByRole('button', { name: /draft proposal/ })).not.toBeInTheDocument();
  });

  it('surfaces a stream error instead of queuing offline', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('network unavailable')));
    render(<OracleTerminal locale="en" />);
    fireEvent.change(screen.getByPlaceholderText(/practice question/), {
      target: { value: 'Fail this' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Ask' }));
    expect(await screen.findByRole('status')).toHaveTextContent('network unavailable');
    expect(screen.queryByText(/safely queued/)).not.toBeInTheDocument();
  });
});
