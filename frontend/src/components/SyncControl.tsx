'use client';

import React from 'react';
import {
  RefreshCw,
  Wifi,
  WifiOff,
  ArrowUpRight,
  ArrowDownLeft,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Layers,
  Send,
} from 'lucide-react';

interface SyncControlProps {
  isOffline: boolean;
  onToggleOffline: () => void;
  isSyncing: boolean;
  onTriggerSync: () => void;
  lastSyncResult: {
    success: boolean;
    entries_pushed: number;
    entries_pulled: number;
    conflicts_raised: number;
    last_sync_time?: string;
    held_local_count?: number;
    message?: string;
  } | null;
  pendingCount: number;
}

export const SyncControl: React.FC<SyncControlProps> = ({
  isOffline,
  onToggleOffline,
  isSyncing,
  onTriggerSync,
  lastSyncResult,
  pendingCount,
}) => {
  return (
    <div className="industrial-card" style={{ padding: '1.25rem' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1rem',
          flexWrap: 'wrap',
          gap: '0.75rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '6px',
              backgroundColor: isOffline ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {isOffline ? <WifiOff size={18} color="#ef4444" /> : <Wifi size={18} color="#10b981" />}
          </div>
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>
              Qdrant Edge ↔ Cloud Sync Protocol
            </h3>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Snapshot & delta exchange. Automatically fires when network re-establishes.
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '0.65rem' }}>
          <button
            onClick={onToggleOffline}
            className="btn-secondary"
            style={{
              fontSize: '0.78rem',
              borderColor: isOffline ? 'rgba(239, 68, 68, 0.4)' : 'rgba(16, 185, 129, 0.4)',
              color: isOffline ? '#f87171' : '#34d399',
            }}
          >
            {isOffline ? <Wifi size={14} /> : <WifiOff size={14} />}
            <span>{isOffline ? 'Disable Airplane Mode' : 'Simulate Offline Floor'}</span>
          </button>

          <button
            onClick={onTriggerSync}
            disabled={isSyncing || isOffline}
            className="btn-primary"
            style={{
              fontSize: '0.78rem',
              opacity: isOffline || isSyncing ? 0.6 : 1,
              cursor: isOffline || isSyncing ? 'not-allowed' : 'pointer',
            }}
          >
            <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
            <span>{isSyncing ? 'Exchanging Delta...' : 'Trigger Sync Now'}</span>
          </button>
        </div>
      </div>

      {/* Sync Status Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: '0.75rem',
          padding: '0.85rem',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}
      >
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Pending Local Queue</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: pendingCount > 0 ? '#ff7b00' : '#10b981', fontFamily: 'var(--font-mono)' }}>
            {pendingCount}
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            <ArrowUpRight size={12} color="#38bdf8" />
            <span>Last Pushed</span>
          </div>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
            {lastSyncResult ? lastSyncResult.entries_pushed : 0}
          </div>
        </div>

        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            <ArrowDownLeft size={12} color="#34d399" />
            <span>Last Pulled</span>
          </div>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
            {lastSyncResult ? lastSyncResult.entries_pulled : 0}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Conflicts Raised</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 800, color: (lastSyncResult?.conflicts_raised || 0) > 0 ? '#ef4444' : '#64748b', fontFamily: 'var(--font-mono)' }}>
            {lastSyncResult ? lastSyncResult.conflicts_raised : 0}
          </div>
        </div>
      </div>

      {lastSyncResult?.message && (
        <div style={{ marginTop: '0.65rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Status: <strong>{lastSyncResult.message}</strong>
        </div>
      )}
    </div>
  );
};
