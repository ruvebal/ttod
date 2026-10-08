<script lang="ts">
  import { onMount, tick } from 'svelte';
  import type { GraphLink, GraphNode, WisdomEntry } from '../../types/domain';
  import { filterGraph, joinTags, radialLayout, type PositionedNode } from './layout';
  import { parseUrlState, resolveUrlState, writeUrlState } from './urlState';

  let allNodes = $state<Array<GraphNode & { tags: string[] }>>([]);
  let allEdges = $state<GraphLink[]>([]);
  let activeTag = $state('');
  let selected = $state<PositionedNode | null>(null);
  let loading = $state(true);
  let error = $state('');
  let graphRoot: SVGSVGElement | undefined = $state();
  let tagFilter: HTMLSelectElement | undefined = $state();

  const tags = $derived([...new Set(allNodes.flatMap((node) => node.tags))].sort());
  const filtered = $derived(filterGraph(allNodes, allEdges, activeTag));
  const nodes = $derived(radialLayout(filtered.nodes));
  const positioned = $derived(new Map(nodes.map((node) => [node.id, node])));
  const edges = $derived(filtered.edges.filter((edge) => positioned.has(edge.source) && positioned.has(edge.target)));

  async function applyTag(tag: string) {
    const focusedNode = document.activeElement instanceof Element
      && document.activeElement.matches('[data-node-id]')
      ? document.activeElement
      : null;
    activeTag = tag;
    if (selected && !filtered.nodes.some((node) => node.id === selected?.id)) selected = null;
    await tick();
    if (focusedNode && !focusedNode.isConnected) tagFilter?.focus();
  }

  let loaded = false;

  function setTag(tag: string) {
    const keepNode = selected && filterGraph(allNodes, allEdges, tag).nodes.some((node) => node.id === selected?.id);
    writeUrlState({ tag, node: keepNode ? selected?.id : '' });
    void applyTag(tag);
  }

  async function syncFromUrl() {
    if (!loaded) return;
    const requested = parseUrlState(window.location.search);
    const next = resolveUrlState(requested, tags, (tag) => filterGraph(allNodes, allEdges, tag).nodes.map((node) => node.id));
    if (next.tag !== requested.tag || next.node !== requested.node) writeUrlState(next, 'replace');
    await applyTag(next.tag);
    selected = next.node ? positioned.get(next.node) ?? null : null;
  }

  function selectNode(node: PositionedNode) {
    selected = node;
    writeUrlState({ node: node.id });
  }

  const arrowSteps: Record<string, number> = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };

  function handleNodeKeydown(event: KeyboardEvent, node: PositionedNode) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectNode(node);
      return;
    }
    const step = arrowSteps[event.key];
    if (step === undefined) return;
    event.preventDefault();
    const currentIndex = nodes.findIndex((candidate) => candidate.id === node.id);
    if (currentIndex === -1) return;
    const nextNode = nodes[(currentIndex + step + nodes.length) % nodes.length];
    (graphRoot?.querySelector(`[data-node-id="${CSS.escape(nextNode.id)}"]`) as SVGCircleElement | null)?.focus();
  }

  onMount(() => {
    const onPopState = () => void syncFromUrl();
    window.addEventListener('popstate', onPopState);
    void (async () => {
      try {
        // Data flow: API response -> joinTags -> radialLayout -> SVG render -> selectNode -> <aside>.
        const [graphResponse, wisdomResponse] = await Promise.all([
          fetch('/api/v1/graph', { cache: 'no-store' }),
          fetch('/api/v1/wisdom/sample', { cache: 'no-store' })
        ]);
        if (!graphResponse.ok || !wisdomResponse.ok) throw new Error('The live graph is unavailable.');
        const graph: { nodes: GraphNode[]; edges: GraphLink[] } = await graphResponse.json();
        const wisdom: WisdomEntry[] = await wisdomResponse.json();
        allNodes = joinTags(graph.nodes, wisdom);
        allEdges = graph.edges;
        loaded = true;
        await syncFromUrl();
      } catch (reason) {
        error = reason instanceof Error ? reason.message : 'The live graph is unavailable.';
      } finally {
        loading = false;
      }
    })();
    return () => window.removeEventListener('popstate', onPopState);
  });
</script>

<section class="graph-island" aria-labelledby="graph-title">
  <header>
    <div><h1 id="graph-title">TTOD knowledge graph</h1><p>{nodes.length} nodes · {edges.length} edges</p></div>
    <label for="tag-filter">Filter by tag
      <select id="tag-filter" bind:this={tagFilter} value={activeTag} onchange={(event) => setTag(event.currentTarget.value)}>
        <option value="">All tags</option>
        {#each tags as tag}<option value={tag}>{tag}</option>{/each}
      </select>
    </label>
  </header>
  <div class="legend" aria-label="Origin legend">
    <span class="human">Human</span><span class="studio">Studio</span><span class="blackbox">AI proposal</span><span class="mixed">Mixed</span><span class="legacy-unknown">Legacy</span>
  </div>
  <p class="sr-only" aria-live="polite" aria-atomic="true">{activeTag ? `Filtered to tag: ${activeTag}` : 'Showing all tags'}</p>
  {#if loading}<p>Loading live graph…</p>{:else if error}<p role="alert">{error}</p>{:else if nodes.length === 0}<p>{activeTag ? 'No nodes carry this tag.' : 'No graph nodes are available.'}</p>{:else}
    <svg bind:this={graphRoot} viewBox="0 0 960 620" role="group" aria-label={`Knowledge graph with ${nodes.length} nodes and ${edges.length} edges`}>
      <g class="edges">{#each edges as edge}<line x1={positioned.get(edge.source)?.x} y1={positioned.get(edge.source)?.y} x2={positioned.get(edge.target)?.x} y2={positioned.get(edge.target)?.y}><title>{edge.rel}</title></line>{/each}</g>
      <g>{#each nodes as node (node.id)}<circle data-node-id={node.id} class:deprecated={node.status === 'deprecated'} class={`node ${node.origin}`} cx={node.x} cy={node.y} r="5" tabindex="0" role="button" aria-label={`${node.id}: ${node.text}${node.tags[0] ? `, tag: ${node.tags[0]}` : ''}`} onclick={() => selectNode(node)} onkeydown={(event) => handleNodeKeydown(event, node)}><title>{node.id} · {node.origin} · {node.text}</title></circle>{/each}</g>
    </svg>
  {/if}
  <aside aria-labelledby="graph-node-details-title" aria-live="polite" aria-atomic="true">
    <h2 id="graph-node-details-title">Selected node</h2>
    {#if selected}
      <strong>{selected.id}</strong>
      <p>{selected.text}</p>
      <small>{selected.section} · {selected.origin}</small>
    {:else}
      <p>Select a node to view its details.</p>
    {/if}
  </aside>
</section>

<style>
  .graph-island { font-family: ui-sans-serif, system-ui, sans-serif; }
  header { align-items: end; display: flex; justify-content: space-between; gap: 1rem; }
  h1 { margin-bottom: 0; } header p { margin-top: .25rem; opacity: .7; }
  select { display: block; padding: .45rem; min-width: 12rem; }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
  svg { background: color-mix(in srgb, Canvas 96%, #9c7a31); border: 1px solid #7775; border-radius: 1rem; width: 100%; }
  line { stroke: #7776; stroke-width: .65; }
  circle { cursor: pointer; fill: #678; stroke: Canvas; stroke-width: 1.5; }
  circle.human { fill: #208a58; } circle.studio { fill: #3178c6; } circle.blackbox { fill: #d33; stroke: #ffda00; stroke-width: 2.5; } circle.mixed { fill: #d3a11f; } circle.legacy-unknown { fill: #777; }
  circle.deprecated { opacity: .35; stroke-dasharray: 2 2; }
  .legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-block: 1rem; }
  .legend span::before { background: #678; border-radius: 50%; content: ''; display: inline-block; height: .7rem; margin-right: .35rem; width: .7rem; }
  .legend .human::before { background: #208a58; } .legend .studio::before { background: #3178c6; } .legend .blackbox::before { background: #d33; outline: 2px solid #ffda00; } .legend .mixed::before { background: #d3a11f; } .legend .legacy-unknown::before { background: #777; }
  aside { margin-block: 1rem; border-inline-start: .25rem solid #9c7a31; padding: .75rem 1rem; }
</style>
