<script lang="ts">
  import { onMount, tick } from 'svelte';
  import type { GraphLink, GraphNode, WisdomEntry } from '../../types/domain';
  import { filterGraph, joinTags, radialLayout, sectionColor, sectionColorKey, type PositionedNode } from './layout';
  import { parseUrlState, resolveUrlState, writeUrlState } from './urlState';
  import { copiaPlano, rotuloDeSeccion, type Lang } from './graphIslandCopy';

  // F32 (AA3): el plano habla el idioma de la página. Sin `lang`, inglés (como antes).
  const { lang = 'en' }: { lang?: Lang } = $props();
  const t = copiaPlano[lang];
  import './GraphIsland.css';

  let allNodes = $state<Array<GraphNode & { tags: string[] }>>([]);
  let allEdges = $state<GraphLink[]>([]);
  let activeTag = $state('');
  let selected = $state<PositionedNode | null>(null);
  let loading = $state(true);
  let error = $state('');
  let graphRoot: SVGSVGElement | undefined = $state();
  let tagFilter: HTMLSelectElement | undefined = $state();

  const tags = $derived([...new Set(allNodes.flatMap((node) => node.tags))].sort());
  const sections = $derived([...new Set(allNodes.map((node) => node.section))].sort());
  const filtered = $derived(filterGraph(allNodes, allEdges, activeTag));
  const nodes = $derived(radialLayout(filtered.nodes));
  const positioned = $derived(new Map(nodes.map((node) => [node.id, node])));
  const edges = $derived(filtered.edges.filter((edge) => positioned.has(edge.source) && positioned.has(edge.target)));

  async function applyTag(tag: string) {
    const focusedNode = document.activeElement instanceof Element
      && document.activeElement.matches('[data-node-id]')
      ? document.activeElement
      : null;
    const nextFiltered = filterGraph(allNodes, allEdges, tag);
    activeTag = tag;
    if (selected && !nextFiltered.nodes.some((node) => node.id === selected.id)) selected = null;
    await tick();
    if (focusedNode && !focusedNode.isConnected) tagFilter?.focus();
  }

  let loaded = false;

  function setTag(tag: string) {
    const keepNode = selected && filterGraph(allNodes, allEdges, tag).nodes.some((node) => node.id === selected?.id);
    void syncFromUrl({ tag, node: keepNode ? selected?.id ?? '' : '' }, 'push');
  }

  async function syncFromUrl(requested = parseUrlState(window.location.search), mode: 'push' | 'replace' = 'replace') {
    if (!loaded) return;
    const next = resolveUrlState(requested, tags, (tag) => filterGraph(allNodes, allEdges, tag).nodes.map((node) => node.id));
    if (next.tag !== requested.tag || next.node !== requested.node || mode === 'push') writeUrlState(next, mode);
    await applyTag(next.tag);
    selected = next.node ? positioned.get(next.node) ?? null : null;
  }

  function selectNode(node: PositionedNode) {
    const current = parseUrlState(window.location.search);
    void syncFromUrl({ ...current, node: node.id }, 'push');
  }

  const arrowDirections = {
    ArrowRight: { x: 1, y: 0 },
    ArrowDown: { x: 0, y: 1 },
    ArrowLeft: { x: -1, y: 0 },
    ArrowUp: { x: 0, y: -1 }
  } as const;

  function focusNode(id: string) {
    const target = graphRoot?.querySelector<SVGCircleElement>(`[data-node-id="${CSS.escape(id)}"]`);
    target?.focus();
  }

  function handleNodeKeydown(event: KeyboardEvent, node: PositionedNode) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      selectNode(node);
      return;
    }
    const direction = arrowDirections[event.key as keyof typeof arrowDirections];
    if (!direction) return;
    event.preventDefault();
    const currentIndex = nodes.findIndex((candidate) => candidate.id === node.id);
    if (currentIndex === -1) return;
    const currentNode = nodes[currentIndex];
    const candidates = nodes.filter((candidate) => candidate.id !== node.id).map((candidate) => {
      const deltaX = candidate.x - currentNode.x;
      const deltaY = candidate.y - currentNode.y;
      return {
        candidate,
        primary: deltaX * direction.x + deltaY * direction.y,
        perpendicular: Math.abs(deltaX * direction.y - deltaY * direction.x),
        distance: deltaX ** 2 + deltaY ** 2
      };
    });
    const directed = candidates.filter(({ primary }) => primary > 0);
    const ranked = directed.length > 0 ? directed : candidates;
    ranked.sort((a, b) => {
      const distanceDifference = directed.length > 0
        ? a.distance - b.distance
        : a.perpendicular - b.perpendicular;
      return distanceDifference || a.distance - b.distance || a.candidate.id.localeCompare(b.candidate.id);
    });
    if (ranked[0]) focusNode(ranked[0].candidate.id);
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
        if (!graphResponse.ok || !wisdomResponse.ok) throw new Error(t.unavailable);
        const graph: { nodes: GraphNode[]; edges: GraphLink[] } = await graphResponse.json();
        const wisdom: WisdomEntry[] = await wisdomResponse.json();
        allNodes = joinTags(graph.nodes, wisdom);
        allEdges = graph.edges;
        loaded = true;
        await syncFromUrl();
      } catch (reason) {
        error = t.unavailable;
      } finally {
        loading = false;
      }
    })();
    return () => window.removeEventListener('popstate', onPopState);
  });
</script>

<section class="graph-island" aria-labelledby="graph-title">
  <header>
    <div><h1 id="graph-title">{t.title}</h1><p>{t.counts(nodes.length, edges.length)}</p></div>
    <label for="tag-filter">{t.filter}
      <select id="tag-filter" bind:this={tagFilter} value={activeTag} onchange={(event) => setTag(event.currentTarget.value)}>
        <option value="">{t.allTags}</option>
        {#each tags as tag}<option value={tag}>{tag}</option>{/each}
      </select>
    </label>
  </header>
  <p class="sr-only" aria-live="polite" aria-atomic="true">{activeTag ? t.filtered(activeTag) : t.showingAll}</p>
  <!-- F60 (AA3): the stage keeps the graph's 960:620 box from the first paint, so the data's arrival
       does not push the page down (CLS 0.47 measured on /es/graph/plano/ before). -->
  <div class="graph-stage">
  {#if loading}<p>{t.loading}</p>{:else if error}<p role="alert">{error}</p>{:else if nodes.length === 0}<p>{activeTag ? t.noTagNodes : t.noNodes}</p>{:else}
    <svg bind:this={graphRoot} viewBox="0 0 960 620" role="group" aria-label={t.graphLabel(nodes.length, edges.length)}>
      <g class="edges">{#each edges as edge}<line x1={positioned.get(edge.source)?.x} y1={positioned.get(edge.source)?.y} x2={positioned.get(edge.target)?.x} y2={positioned.get(edge.target)?.y}><title>{edge.rel}</title></line>{/each}</g>
      <g>{#each nodes as node (node.id)}<circle data-node-id={node.id} data-section-color={sectionColorKey(node.section)} data-origin={node.origin} style={`--section-color: ${sectionColor(node.section)}`} class:deprecated={node.status === 'deprecated'} class="node" cx={node.x} cy={node.y} r="5" tabindex="0" focusable="true" role="button" aria-label={t.nodeLabel(node.id, node.text, lang === 'es' ? rotuloDeSeccion(node.section, lang) : node.section, node.origin, node.tags)} onclick={() => selectNode(node)} onkeydown={(event) => handleNodeKeydown(event, node)}><title>{node.id} · {node.section} · {node.origin} · {node.text}</title></circle>{/each}</g>
    </svg>
  {/if}
  </div>
  <aside aria-labelledby="graph-node-details-title" aria-live="polite" aria-atomic="true">
    <h2 id="graph-node-details-title">{t.selected}</h2>
    {#if selected}
      <strong>{selected.id}</strong>
      <p>{selected.text}</p>
      <small>{lang === 'es' ? rotuloDeSeccion(selected.section, lang) : selected.section} · {selected.origin}</small>
    {:else}
      <p>{t.selectHint}</p>
    {/if}
  </aside>
  <!-- The legend grows with the data; below the details it shifts nothing on screen. -->
  <div class="legend" aria-label={t.legend}>
    {#each sections as section}
      <span data-section-color={sectionColorKey(section)} style={`--section-color: ${sectionColor(section)}`}>{rotuloDeSeccion(section, lang)}</span>
    {/each}
  </div>
</section>
