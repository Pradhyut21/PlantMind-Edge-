import {
  KnowledgeEntry,
  ConflictRecord,
  DeviceMemoryStats,
  ActivityEvent,
  SyncResponse,
  CloudStats,
} from './types';

export const EDGE_API_URL = process.env.NEXT_PUBLIC_EDGE_API || 'http://127.0.0.1:8000';
export const CLOUD_API_URL = process.env.NEXT_PUBLIC_CLOUD_API || 'http://127.0.0.1:8001';

// --- EDGE API CLIENT (PORT 8000) ---

export async function getEdgeStatus(deviceId?: string): Promise<{
  device_id: string;
  is_offline_simulation: boolean;
  last_sync_time?: string;
  pending_queue_count: number;
  cloud_api_url: string;
}> {
  const url = new URL(`${EDGE_API_URL}/api/status`);
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Edge status failed: ${res.statusText}`);
  return res.json();
}

export async function toggleNetworkOffline(
  isOffline: boolean,
  deviceId?: string
): Promise<{ device_id: string; is_offline: boolean; status: string }> {
  const url = new URL(`${EDGE_API_URL}/api/network/toggle`);
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_offline: isOffline }),
  });
  if (!res.ok) throw new Error(`Network toggle failed: ${res.statusText}`);
  return res.json();
}

export async function switchEdgeDevice(
  deviceId: string
): Promise<{ active_device_id: string; storage_path: string }> {
  const res = await fetch(`${EDGE_API_URL}/api/device/switch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device_id: deviceId }),
  });
  if (!res.ok) throw new Error(`Device switch failed: ${res.statusText}`);
  return res.json();
}

export async function searchLocalEdge(
  query: string,
  options: {
    machineId?: string;
    areaTag?: string;
    entryType?: string;
    limit?: number;
    deviceId?: string;
  } = {}
): Promise<KnowledgeEntry[]> {
  const url = new URL(`${EDGE_API_URL}/api/search`);
  url.searchParams.set('q', query);
  if (options.machineId && options.machineId !== 'ALL')
    url.searchParams.set('machine_id', options.machineId);
  if (options.areaTag && options.areaTag !== 'ALL')
    url.searchParams.set('area_tag', options.areaTag);
  if (options.entryType && options.entryType !== 'ALL')
    url.searchParams.set('entry_type', options.entryType);
  if (options.limit) url.searchParams.set('limit', options.limit.toString());
  if (options.deviceId) url.searchParams.set('device_id', options.deviceId);

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Offline search failed: ${res.statusText}`);
  return res.json();
}

export async function getLocalEntries(
  options: {
    machineId?: string;
    entryType?: string;
    syncStatus?: string;
    deviceId?: string;
    limit?: number;
  } = {}
): Promise<KnowledgeEntry[]> {
  const url = new URL(`${EDGE_API_URL}/api/entries`);
  if (options.machineId && options.machineId !== 'ALL')
    url.searchParams.set('machine_id', options.machineId);
  if (options.entryType && options.entryType !== 'ALL')
    url.searchParams.set('entry_type', options.entryType);
  if (options.syncStatus && options.syncStatus !== 'ALL')
    url.searchParams.set('sync_status', options.syncStatus);
  if (options.deviceId) url.searchParams.set('device_id', options.deviceId);
  if (options.limit) url.searchParams.set('limit', options.limit.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to load local entries: ${res.statusText}`);
  return res.json();
}

export async function createLocalEntry(
  entryData: {
    type: string;
    title: string;
    body: string;
    machine_id: string;
    area_tag: string;
    created_by: string;
    tags: string[];
    keep_local_until_reviewed: boolean;
  },
  deviceId?: string
): Promise<KnowledgeEntry> {
  const url = new URL(`${EDGE_API_URL}/api/entries`);
  if (deviceId) url.searchParams.set('device_id', deviceId);

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entryData),
  });
  if (!res.ok) throw new Error(`Failed to write local entry: ${res.statusText}`);
  return res.json();
}

export async function inspectDeviceMemory(deviceId?: string): Promise<DeviceMemoryStats> {
  const url = new URL(`${EDGE_API_URL}/api/memory/inspect`);
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Memory inspect failed: ${res.statusText}`);
  return res.json();
}

export async function triggerEdgeSync(deviceId?: string): Promise<{
  success: boolean;
  offline: boolean;
  message: string;
  entries_pushed: number;
  entries_pulled: number;
  conflicts_raised: number;
  last_sync_time?: string;
  held_local_count?: number;
}> {
  const url = new URL(`${EDGE_API_URL}/api/sync/trigger`);
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString(), { method: 'POST' });
  if (!res.ok) throw new Error(`Sync trigger failed: ${res.statusText}`);
  return res.json();
}

export async function getEdgeActivity(deviceId?: string, limit = 40): Promise<ActivityEvent[]> {
  const url = new URL(`${EDGE_API_URL}/api/activity`);
  url.searchParams.set('limit', limit.toString());
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString());
  if (!res.ok) return [];
  return res.json();
}

export async function toggleKeepLocalPolicy(
  entryId: string,
  deviceId?: string
): Promise<{ entry_id: string; keep_local_until_reviewed: boolean; sync_status: string }> {
  const url = new URL(`${EDGE_API_URL}/api/policy/toggle_local`);
  if (deviceId) url.searchParams.set('device_id', deviceId);
  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ entry_id: entryId }),
  });
  if (!res.ok) throw new Error(`Policy toggle failed: ${res.statusText}`);
  return res.json();
}

// --- CLOUD API CLIENT (PORT 8001) ---

export async function getCloudStats(): Promise<CloudStats> {
  const res = await fetch(`${CLOUD_API_URL}/api/stats`);
  if (!res.ok) throw new Error(`Cloud stats failed: ${res.statusText}`);
  return res.json();
}

export async function getCloudEntries(
  options: {
    machineId?: string;
    entryType?: string;
    syncStatus?: string;
    limit?: number;
  } = {}
): Promise<KnowledgeEntry[]> {
  const url = new URL(`${CLOUD_API_URL}/api/entries`);
  if (options.machineId && options.machineId !== 'ALL')
    url.searchParams.set('machine_id', options.machineId);
  if (options.entryType && options.entryType !== 'ALL')
    url.searchParams.set('entry_type', options.entryType);
  if (options.syncStatus && options.syncStatus !== 'ALL')
    url.searchParams.set('sync_status', options.syncStatus);
  if (options.limit) url.searchParams.set('limit', options.limit.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Cloud entries failed: ${res.statusText}`);
  return res.json();
}

export async function getConflicts(status: string = 'open'): Promise<ConflictRecord[]> {
  const url = new URL(`${CLOUD_API_URL}/api/conflicts`);
  if (status && status !== 'ALL') url.searchParams.set('status', status);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Conflicts fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getConflictById(id: string): Promise<ConflictRecord> {
  const res = await fetch(`${CLOUD_API_URL}/api/conflicts/${id}`);
  if (!res.ok) throw new Error(`Conflict fetch failed: ${res.statusText}`);
  return res.json();
}

export async function resolveConflict(
  id: string,
  resolution: {
    resolution_type: 'winner_picked' | 'merged' | 'both_annotated';
    winner_version_index?: number;
    merged_title?: string;
    merged_body?: string;
    merged_tags?: string[];
    resolution_note?: string;
    resolved_by?: string;
  }
): Promise<ConflictRecord> {
  const res = await fetch(`${CLOUD_API_URL}/api/conflicts/${id}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(resolution),
  });
  if (!res.ok) throw new Error(`Conflict resolution failed: ${res.statusText}`);
  return res.json();
}

export async function rerunConflictReasoning(
  id: string
): Promise<{ conflict_id: string; ai_summary: string }> {
  const res = await fetch(`${CLOUD_API_URL}/api/conflicts/${id}/reason`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`Reasoning request failed: ${res.statusText}`);
  return res.json();
}

export async function getCloudActivity(limit = 40): Promise<ActivityEvent[]> {
  const res = await fetch(`${CLOUD_API_URL}/api/activity?limit=${limit}`);
  if (!res.ok) return [];
  return res.json();
}

export async function getDevices(): Promise<Record<string, { name: string; status: string; last_sync?: string }>> {
  const res = await fetch(`${CLOUD_API_URL}/api/devices`);
  if (!res.ok) return {};
  return res.json();
}
