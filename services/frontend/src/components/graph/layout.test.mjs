import assert from 'node:assert/strict';
import test from 'node:test';
import { filterGraph, joinTags, radialLayout, selectedTag } from './layout.ts';

const nodes = [{ id: 'a-001', section: 'a', origin: 'blackbox', status: 'active', text: 'A', lang: 'en' }, { id: 'b-001', section: 'b', origin: 'human', status: 'active', text: 'B', lang: 'en' }];
const wisdom = [{ ...nodes[0], level: 'beginner', teaches: '', tags: ['focus'], related: [], rights: { license: 'CC-BY-NC-SA-4.0' } }];
const edges = [{ source: 'a-001', target: 'b-001', rel: 'related' }];

test('joins tags and filters the induced edge set', () => {
  const joined = joinTags(nodes, wisdom);
  const filtered = filterGraph(joined, edges, 'focus');
  assert.deepEqual(filtered.nodes.map((node) => node.id), ['a-001']);
  assert.equal(filtered.edges.length, 0);
});

test('layout is deterministic and URL state reads only tag', () => {
  const joined = joinTags(nodes, wisdom);
  assert.deepEqual(radialLayout(joined), radialLayout(joined));
  assert.equal(selectedTag('?tag=focus&ignored=yes'), 'focus');
});
