import type { GraphLink, GraphNode, WisdomEntry } from '../../types/domain';

export interface PositionedNode extends GraphNode {
  x: number;
  y: number;
  tags: string[];
}

export function joinTags(nodes: GraphNode[], wisdom: WisdomEntry[]): Array<GraphNode & { tags: string[] }> {
  const tagsById = new Map(wisdom.map((entry) => [entry.id, entry.tags]));
  return nodes.map((node) => ({ ...node, tags: tagsById.get(node.id) ?? [] }));
}

export function filterGraph(
  nodes: Array<GraphNode & { tags: string[] }>,
  edges: GraphLink[],
  tag: string
): { nodes: Array<GraphNode & { tags: string[] }>; edges: GraphLink[] } {
  const visible = tag ? nodes.filter((node) => node.tags.includes(tag)) : nodes;
  const ids = new Set(visible.map((node) => node.id));
  return { nodes: visible, edges: edges.filter((edge) => ids.has(edge.source) && ids.has(edge.target)) };
}

export function radialLayout(
  nodes: Array<GraphNode & { tags: string[] }>,
  width = 960,
  height = 620
): PositionedNode[] {
  const groups = new Map<string, Array<GraphNode & { tags: string[] }>>();
  for (const node of nodes) groups.set(node.section, [...(groups.get(node.section) ?? []), node]);
  const sections = [...groups.keys()].sort();
  const centerX = width / 2;
  const centerY = height / 2;
  const sectionRadius = Math.min(width, height) * 0.31;
  const clusterRadius = Math.max(24, Math.min(90, sectionRadius * 0.34));
  return sections.flatMap((section, sectionIndex) => {
    const angle = (sectionIndex / Math.max(sections.length, 1)) * Math.PI * 2 - Math.PI / 2;
    const clusterX = centerX + Math.cos(angle) * sectionRadius;
    const clusterY = centerY + Math.sin(angle) * sectionRadius;
    const group = groups.get(section)!.slice().sort((a, b) => a.id.localeCompare(b.id));
    return group.map((node, index) => {
      const nodeAngle = (index / Math.max(group.length, 1)) * Math.PI * 2;
      const ring = clusterRadius * (0.35 + 0.65 * ((index % 4) + 1) / 4);
      return { ...node, x: clusterX + Math.cos(nodeAngle) * ring, y: clusterY + Math.sin(nodeAngle) * ring };
    });
  });
}

export function selectedTag(search: string): string {
  return new URLSearchParams(search).get('tag') ?? '';
}
