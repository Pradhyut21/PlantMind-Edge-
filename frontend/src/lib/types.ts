export enum KnowledgeType {
  MANUAL_SECTION = 'manual_section',
  INCIDENT_LOG = 'incident_log',
  TRIBAL_NOTE = 'tribal_note',
  SAFETY_PROCEDURE = 'safety_procedure',
}

export enum SyncStatus {
  LOCAL_ONLY = 'local_only',
  PENDING_SYNC = 'pending_sync',
  SYNCED = 'synced',
  CONFLICT = 'conflict',
}

export interface KnowledgeEntry {
  id: string;
  type: KnowledgeType;
  title: string;
  body: string;
  machine_id: string;
  area_tag: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  device_id: string;
  version: number;
  sync_status: SyncStatus;
  keep_local_until_reviewed: boolean;
  tags: string[];
  similarity_score?: number;
}

export interface CompetingVersion {
  version: number;
  title: string;
  body: string;
  created_by: string;
  device_id: string;
  updated_at: string;
  tags: string[];
  label?: string;
}

export interface ConflictRecord {
  id: string;
  entry_id: string;
  entity_title: string;
  entity_type: KnowledgeType;
  machine_id: string;
  area_tag: string;
  status: 'open' | 'resolved';
  competing_versions: CompetingVersion[];
  created_at: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_type?: 'winner_picked' | 'merged' | 'both_annotated' | string;
  resolution_note?: string;
  resolved_content?: any;
  ai_summary?: string;
}

export interface DeviceMemoryStats {
  device_id: string;
  total_entries: number;
  local_only_count: number;
  pending_sync_count: number;
  synced_count: number;
  conflict_count: number;
  storage_bytes: number;
  storage_formatted: string;
  vector_dim: number;
  hnsw_indexed_vectors: number;
  last_sync_time?: string;
  collection_status: string;
  is_offline: boolean;
  pending_queue_size: number;
}

export interface ActivityEvent {
  id: string;
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  device_id: string;
  metadata?: Record<string, any>;
}

export interface SyncResponse {
  success: boolean;
  device_id: string;
  entries_pushed: number;
  entries_pulled: number;
  conflicts_raised: number;
  pulled_entries: KnowledgeEntry[];
  conflicts: ConflictRecord[];
  cloud_timestamp: string;
  message: string;
}

export interface CloudStats {
  total_entries: number;
  open_conflicts: number;
  total_conflicts: number;
  active_devices: number;
  total_sync_sessions: number;
  vector_dimension: number;
  qdrant_target: string;
}
