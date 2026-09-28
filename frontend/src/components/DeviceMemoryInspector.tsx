'use client';

import React from 'react';
import {
  HardDrive,
  Database,
  Cpu,
  Clock,
  Lock,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Sliders,
  Shield,
  Layers,
} from 'lucide-react';
import { DeviceMemoryStats, KnowledgeEntry, SyncStatus } from '../lib/types';
import { toggleKeepLocalPolicy } from '../lib/api';

interface DeviceMemoryInspectorProps {
  stats: DeviceMemoryStats | null;
  entries: KnowledgeEntry[];
  deviceId: string;
  onRefresh: () => void;
}

export const DeviceMemoryInspector: React.FC<DeviceMemoryInspectorProps> = ({
  stats,
  entries,
  deviceId,
  onRefresh,
}) => {
  if (!stats) {
    return (
      <div className="industrial-card" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>Querying on-device memory metrics...</p>
      </div>
    );
  }

  const handlePolicyToggle = async (entryId: string) => {
    try {
      await toggleKeepLocalPolicy(entryId, deviceId);
      onRefresh();
    } catch (err) {
      console.error('Failed to toggle policy:', err);
    }
  };

  const total = stats.total_entries || 1;
  const syncedPct = Math.round((stats.synced_count / total) * 100);
  const pendingPct = Math.round((stats.pending_sync_count / total) * 100);
  const localPct = Math.round((stats.local_only_count / total) * 100);
  const conflictPct = Math.round((stats.conflict_count / total) * 100);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Metric Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* Metric 1: Total Entries */}
        <div className="industrial-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>Total Local Entries</span>
            <Database size={16} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            {stats.total_entries}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#38bdf8', marginTop: '0.2rem' }}>
            Stored in Qdrant Edge collection
          </div>
        </div>

        {/* Metric 2: Storage Size */}
        <div className="industrial-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>On-Device Storage</span>
            <HardDrive size={16} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            {stats.storage_formatted}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            HNSW vectors + payload WAL
          </div>
        </div>

        {/* Metric 3: Synced vs Pending */}
        <div className="industrial-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>Synced with Cloud</span>
            <CheckCircle2 size={16} color="#10b981" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#34d399', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            {stats.synced_count}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {stats.pending_sync_count} pending in write queue
          </div>
        </div>

        {/* Metric 4: Deliberate Local Only */}
        <div className="industrial-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>Local Only (Policy)</span>
            <Lock size={16} color="#facc15" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#facc15', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            {stats.local_only_count}
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Excluded from sync until reviewed
          </div>
        </div>

        {/* Metric 5: Vector Index Metrics */}
        <div className="industrial-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>HNSW Vector Specs</span>
            <Cpu size={16} color="#a855f7" />
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#c084fc', marginTop: '0.4rem', fontFamily: 'var(--font-mono)' }}>
            {stats.vector_dim}d
          </div>
          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Cosine metric • FastEmbed BGE
          </div>
        </div>
      </div>

      {/* Memory Breakdown Gauge */}
      <div className="industrial-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
            Device Memory Breakdown ({deviceId})
          </h3>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Last Sync: {stats.last_sync_time ? new Date(stats.last_sync_time).toLocaleTimeString() : 'Never'}
          </div>
        </div>

        {/* Multi-colored Progress Bar */}
        <div
          style={{
            height: '14px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '999px',
            overflow: 'hidden',
            display: 'flex',
            marginBottom: '0.85rem',
          }}
        >
          <div style={{ width: `${syncedPct}%`, backgroundColor: '#10b981' }} title={`Synced: ${syncedPct}%`} />
          <div style={{ width: `${pendingPct}%`, backgroundColor: '#ff7b00' }} title={`Pending: ${pendingPct}%`} />
          <div style={{ width: `${localPct}%`, backgroundColor: '#facc15' }} title={`Local Only: ${localPct}%`} />
          <div style={{ width: `${conflictPct}%`, backgroundColor: '#ef4444' }} title={`Conflict: ${conflictPct}%`} />
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', fontSize: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '10px', height: '10px', backgroundColor: '#10b981', borderRadius: '2px' }} />
            <span>Synced ({stats.synced_count})</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '10px', height: '10px', backgroundColor: '#ff7b00', borderRadius: '2px' }} />
            <span>Pending Sync ({stats.pending_sync_count})</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '10px', height: '10px', backgroundColor: '#facc15', borderRadius: '2px' }} />
            <span>Local Only ({stats.local_only_count})</span>
          </div>
          {stats.conflict_count > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '10px', height: '10px', backgroundColor: '#ef4444', borderRadius: '2px' }} />
              <span>Conflict ({stats.conflict_count})</span>
            </div>
          )}
        </div>
      </div>

      {/* Local Entries Table & Policy Controller */}
      <div className="industrial-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
              Local Shard Catalog & Data Policy Controller
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Directly control which tribal knowledge notes sync vs remain on-device only.
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.65rem 0.5rem' }}>Type</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Title</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Machine</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Author</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Sync Status</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Data Policy</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((item) => (
                <tr
                  key={item.id}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                    transition: 'background-color 0.15s ease',
                  }}
                >
                  <td style={{ padding: '0.65rem 0.5rem' }}>
                    <span style={{ fontSize: '0.72rem', textTransform: 'capitalize', color: 'var(--text-secondary)' }}>
                      {item.type.replace('_', ' ')}
                    </span>
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600, color: '#fff', maxWidth: '300px' }}>
                    {item.title}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                    {item.machine_id}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-secondary)' }}>
                    {item.created_by}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem' }}>
                    {item.sync_status === SyncStatus.SYNCED && (
                      <span className="badge badge-synced">Synced</span>
                    )}
                    {item.sync_status === SyncStatus.PENDING_SYNC && (
                      <span className="badge badge-tribal">Pending Sync</span>
                    )}
                    {item.sync_status === SyncStatus.LOCAL_ONLY && (
                      <span className="badge badge-local-only">Local Only</span>
                    )}
                    {item.sync_status === SyncStatus.CONFLICT && (
                      <span className="badge badge-conflict">Conflict</span>
                    )}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem' }}>
                    <button
                      onClick={() => handlePolicyToggle(item.id)}
                      style={{
                        backgroundColor: item.keep_local_until_reviewed
                          ? 'rgba(234, 179, 8, 0.15)'
                          : 'rgba(255, 255, 255, 0.05)',
                        color: item.keep_local_until_reviewed ? '#facc15' : 'var(--text-muted)',
                        border: item.keep_local_until_reviewed
                          ? '1px solid rgba(234, 179, 8, 0.4)'
                          : '1px solid var(--border-color)',
                        padding: '0.25rem 0.6rem',
                        borderRadius: '6px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                      }}
                    >
                      <Lock size={12} />
                      <span>{item.keep_local_until_reviewed ? 'Keep Local' : 'Allow Sync'}</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
