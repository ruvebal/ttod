// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mount, unmount, type Component } from 'svelte';
import GraphIsland from './GraphIsland.svelte';

// F32 (AA3, A20): on /es/ the 2D plano speaks Spanish; without `lang` it keeps its English (the e2e specs).
const nodes = [{ id: 'arch-060', section: 'architecture', origin: 'human', status: 'active', text: 'Un límite.', lang: 'es' }];
const wisdom = [{ ...nodes[0], level: 'beginner', teaches: '', tags: ['koan'], related: [], rights: { license: 'CC-BY-NC-SA-4.0' } }];
afterEach(() => { vi.unstubAllGlobals(); document.body.replaceChildren(); });
const mountWith = async (props: Record<string, unknown>) => {
  vi.stubGlobal('fetch', vi.fn()
    .mockResolvedValueOnce(new Response(JSON.stringify({ nodes, edges: [] }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify(wisdom), { status: 200 })));
  const target = document.createElement('div'); document.body.append(target);
  const island = mount(GraphIsland as unknown as Component, { target, props });
  await vi.waitFor(() => expect(target.querySelectorAll('[data-node-id]')).toHaveLength(1));
  return { target, island };
};

describe('GraphIsland i18n', () => {
  it('speaks Spanish with lang="es"', async () => {
    const { target, island } = await mountWith({ lang: 'es' });
    const text = target.textContent ?? '';
    expect(target.querySelector('h1')?.textContent).toBe('Grafo de conocimiento de TTOD');
    expect(text).toContain('Filtrar por etiqueta');
    expect(text).toContain('Todas las etiquetas');
    expect(text).toContain('Nodo seleccionado');
    expect(text).toContain('Arquitectura');
    expect(target.querySelector('svg')?.getAttribute('aria-label')).toBe('Grafo de conocimiento con 1 nodos y 0 relaciones');
    for (const en of ['All tags', 'Selected node', 'Filter by tag', 'Knowledge graph']) expect(text).not.toContain(en);
    unmount(island);
  });
  it('keeps English without lang', async () => {
    const { target, island } = await mountWith({});
    expect(target.querySelector('h1')?.textContent).toBe('TTOD knowledge graph');
    unmount(island);
  });
});
