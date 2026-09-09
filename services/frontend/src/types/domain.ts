// Wisdom & graph — the governed corpus and its relations
export interface WisdomEntry {
  id: string;
  section: string;
  subsection?: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'master';
  text: string;
  teaches: string;
  tags: string[];
  related: string[];
  origin: 'human' | 'studio' | 'blackbox' | 'mixed' | 'legacy-unknown';
  lang: string;
  rights: {
    license: string;
    holder?: string;
  };
}

export interface GraphNode {
  id: string;
  section: string;
  origin: WisdomEntry['origin'];
  status: 'active' | 'deprecated' | 'erased';
  text: string;
  lang: string;
}

export interface GraphLink {
  source: string;
  target: string;
  rel: 'related' | 'immediate_parent' | 'root_source' | 'deprecated_by' | 'superseded_by' | 'translation_of';
}

// Oracle — streamed retrieval-grounded chat
export type Locale = 'en' | 'es';

export interface OracleQueryPayload {
  query: string;
  contextTag?: string;
  sessionHistory: string[];
  locale?: Locale;
}

export interface OracleResponseChunk {
  mode: 'grounded' | 'creative';
  citedQuoteIds?: string[];
  themes?: string[];
  tags?: string[];
  text: string;
}

export interface OracleProposeRequest {
  query: string;
  creativeAnswer: string;
  suggestedSection?: string;
  suggestedTags?: string[];
  locale?: Locale;
}

// Offline — the local operations queue
export interface OfflineLogEntry {
  id: string;
  timestamp: string;
  kind: 'oracle-query' | 'error-report';
  payload: OracleQueryPayload | { errorLog: string };
  synced: boolean;
}
