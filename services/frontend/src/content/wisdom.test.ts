import { describe, expect, it } from 'vitest';

import { frequencies } from './wisdom';
import type { WisdomEntry } from '../types/domain';

// frequencies() never had its own unit test before this file — it was only ever exercised
// indirectly through route-level integration tests (and only in task branches not yet merged).
// This closes that gap directly, as a pure function with no DOM/network involved.

const entry = (id: string, section: string, level: WisdomEntry['level'], tags: string[]): WisdomEntry => ({
  id, section, level, tags,
  text: `Aphorism ${id}`, teaches: `What ${id} teaches`, related: [],
  origin: 'human', lang: 'en',
  rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
});

describe('frequencies', () => {
  it('counts by section', () => {
    const entries = [
      entry('a-1', 'architecture', 'beginner', []),
      entry('a-2', 'architecture', 'advanced', []),
      entry('w-1', 'wisdom', 'master', []),
    ];
    expect(frequencies(entries, 'section')).toEqual([['architecture', 2], ['wisdom', 1]]);
  });

  it('counts by level', () => {
    const entries = [
      entry('a-1', 'architecture', 'beginner', []),
      entry('a-2', 'architecture', 'beginner', []),
      entry('a-3', 'architecture', 'master', []),
    ];
    expect(frequencies(entries, 'level')).toEqual([['beginner', 2], ['master', 1]]);
  });

  it('counts by tags, crediting an entry with several tags to each one', () => {
    const entries = [
      entry('a-1', 'architecture', 'beginner', ['boundaries', 'coupling']),
      entry('a-2', 'architecture', 'advanced', ['boundaries']),
    ];
    expect(frequencies(entries, 'tags')).toEqual([['boundaries', 2], ['coupling', 1]]);
  });

  it('returns an empty list for an empty payload', () => {
    expect(frequencies([], 'section')).toEqual([]);
  });

  it('sorts results alphabetically, not by insertion or count order', () => {
    const entries = [
      entry('w-1', 'wisdom', 'beginner', []),
      entry('a-1', 'architecture', 'beginner', []),
      entry('c-1', 'code-craft', 'beginner', []),
    ];
    expect(frequencies(entries, 'section').map(([value]) => value)).toEqual(['architecture', 'code-craft', 'wisdom']);
  });

  it('handles repeated values across many entries, not just two', () => {
    const entries = Array.from({ length: 5 }, (_, i) => entry(`a-${i}`, 'architecture', 'beginner', []));
    expect(frequencies(entries, 'section')).toEqual([['architecture', 5]]);
  });
});
