<script lang="ts">
  import { onMount } from 'svelte';
  import { gsap } from 'gsap';
  import type { GraphLink, GraphNode, WisdomEntry } from '../../types/domain';
  import { filterGraph, joinTags, radialLayout, selectedTag, type PositionedNode } from './layout';

  let allNodes = $state<Array<GraphNode & { tags: string[] }>>([]);
  let allEdges = $state<GraphLink[]>([]);
  let activeTag = $state('');
  let selected = $state<PositionedNode | null>(null);
  let loading = $state(true);
  let error = $state('');
  let graphRoot: SVGSVGElement;

  const filtered = $derived(filterGraph(allNodes, allEdges, activeTag));
  const nodes = $derived(radialLayout(filtered.nodes));
  const positioned = $derived(new Map(nodes.map((node) => [node.id, node])));
  const edges = $derived(filtered.edges.filter((edge) => positioned.has(edge.source) && positioned.has(edge.target)));
  const tags = $derived([...new Set(allNodes.flatMap((node) => node.tags))].sort());

  function syncFromUrl() {
    activeTag = selectedTag(window.location.search);
  }

  function setTag(tag: string, clearSelection = true) {
    const url = new URL(window.location.href);
    if (tag) url.searchParams.set('tag', tag);
    else url.searchParams.delete('tag');
    history.pushState({}, '', url);
    activeTag = tag;
    if (clearSelection) selected = null;
    requestAnimationFrame(() => gsap.fromTo(graphRoot.querySelectorAll('.node'), { opacity: 0, scale: 0.6 }, { opacity: 1, scale: 1, duration: 0.45, stagger: 0.006, ease: 'back.out(1.5)' }));
  }

  function selectNode(node: PositionedNode) {
    selected = node;
    setTag(node.tags[0] ?? '', false);
  }

  function hover(event: MouseEvent, entering: boolean) {
    gsap.to(event.currentTarget, { scale: entering ? 1.7 : 1, duration: 0.18, transformOrigin: 'center' });
  }

  onMount(() => {
    syncFromUrl();
    window.addEventListener('popstate', syncFromUrl);
    void (async () => {
      try {
        const [graphResponse, wisdomResponse] = await Promise.all([
          fetch('/api/v1/graph', { cache: 'no-store' }),
          fetch('/api/v1/wisdom/sample', { cache: 'no-store' })
        ]);
        if (!graphResponse.ok || !wisdomResponse.ok) throw new Error('The live graph is unavailable.');
        const graph: { nodes: GraphNode[]; edges: GraphLink[] } = await graphResponse.json();
        const wisdom: WisdomEntry[] = await wisdomResponse.json();
        allNodes = joinTags(graph.nodes, wisdom);
        allEdges = graph.edges;
      } catch (reason) {
        error = reason instanceof Error ? reason.message : 'The live graph is unavailable.';
      } finally {
        loading = false;
      }
    })();
    return () => window.removeEventListener('popstate', syncFromUrl);
  });
</script>

<section class="graph-island" aria-labelledby="graph-title">
  <header>
    <div><h1 id="graph-title">TTOD knowledge graph</h1><p>{nodes.length} nodes · {edges.length} edges</p></div>
    <label>Tag
      <select value={activeTag} onchange={(event) => setTag(event.currentTarget.value)}>
        <option value="">All tags</option>
        {#each tags as tag}<option value={tag}>{tag}</option>{/each}
      </select>
    </label>
  </header>
  <div class="legend" aria-label="Origin legend">
    <span class="human">Human</span><span class="studio">Studio</span><span class="blackbox">AI proposal</span><span class="legacy-unknown">Legacy</span>
  </div>
  {#if loading}<p>Loading live graph…</p>{:else if error}<p role="alert">{error}</p>{:else if nodes.length === 0}<p>No nodes carry this tag.</p>{:else}
    <svg bind:this={graphRoot} viewBox="0 0 960 620" role="img" aria-label={`Knowledge graph with ${nodes.length} nodes and ${edges.length} edges`}>
      <g class="edges">{#each edges as edge}<line x1={positioned.get(edge.source)?.x} y1={positioned.get(edge.source)?.y} x2={positioned.get(edge.target)?.x} y2={positioned.get(edge.target)?.y}><title>{edge.rel}</title></line>{/each}</g>
      <g>{#each nodes as node (node.id)}<circle class:deprecated={node.status === 'deprecated'} class={`node ${node.origin}`} cx={node.x} cy={node.y} r="5" tabindex="0" role="button" aria-label={`${node.id}: ${node.text}`} onclick={() => selectNode(node)} onkeydown={(event) => (event.key === 'Enter' || event.key === ' ') && selectNode(node)} onmouseenter={(event) => hover(event, true)} onmouseleave={(event) => hover(event, false)}><title>{node.id} · {node.origin} · {node.text}</title></circle>{/each}</g>
    </svg>
  {/if}
  {#if selected}<aside><strong>{selected.id}</strong><p>{selected.text}</p><small>{selected.section} · {selected.origin}</small></aside>{/if}
</section>

<style>
  .graph-island { font-family: ui-sans-serif, system-ui, sans-serif; }
  header { align-items: end; display: flex; justify-content: space-between; gap: 1rem; }
  h1 { margin-bottom: 0; } header p { margin-top: .25rem; opacity: .7; }
  select { display: block; padding: .45rem; min-width: 12rem; }
  svg { background: color-mix(in srgb, Canvas 96%, #9c7a31); border: 1px solid #7775; border-radius: 1rem; width: 100%; }
  line { stroke: #7776; stroke-width: .65; }
  circle { cursor: pointer; fill: #678; stroke: Canvas; stroke-width: 1.5; transform-box: fill-box; }
  circle.human { fill: #208a58; } circle.studio { fill: #3178c6; } circle.blackbox { fill: #d33; stroke: #ffda00; stroke-width: 2.5; } circle.legacy-unknown { fill: #777; }
  circle.deprecated { opacity: .35; stroke-dasharray: 2 2; }
  .legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-block: 1rem; }
  .legend span::before { background: #678; border-radius: 50%; content: ''; display: inline-block; height: .7rem; margin-right: .35rem; width: .7rem; }
  .legend .human::before { background: #208a58; } .legend .studio::before { background: #3178c6; } .legend .blackbox::before { background: #d33; outline: 2px solid #ffda00; } .legend .legacy-unknown::before { background: #777; }
  aside { border-inline-start: .25rem solid #9c7a31; padding: .75rem 1rem; }
</style>
