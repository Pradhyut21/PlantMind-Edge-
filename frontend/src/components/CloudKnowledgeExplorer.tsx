'use client';

import React, { useState } from 'react';
import {
  Database,
  Search,
  Server,
  Layers,
  Shield,
  BookOpen,
  User,
  AlertOctagon,
  HardDrive,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { KnowledgeEntry, KnowledgeType, CloudStats } from '../lib/types';

interface CloudKnowledgeExplorerProps {
  entries: KnowledgeEntry[];
  stats: CloudStats | null;
  devices: Record<string, { name: string; status: string; last_sync?: string }>;
}

export const CloudKnowledgeExplorer: React.FC<CloudKnowledgeExplorerProps> = ({
  entries,
  stats,
  devices,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [machineFilter, setMachineFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const filteredEntries = entries.filter((e) => {
    const matchSearch =
      searchTerm === '' ||
      e.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.body.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.tags.some((t) => t.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchMachine = machineFilter === 'ALL' || e.machine_id === machineFilter;
    const matchType = typeFilter === 'ALL' || e.type === typeFilter;

    return matchSearch && matchMachine && matchType;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Cloud Header Stats Cards */}
      {stats && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
          }}
        >
          <div className="industrial-card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Master Knowledge Entries</span>
              <Database size={15} color="#38bdf8" />
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem', fontFamily: 'var(--font-mono)' }}>
              {stats.total_entries}
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Qdrant Server: {stats.qdrant_target}
            </div>
          </div>

          <div className="industrial-card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Active Kiosks Registered</span>
              <Server size={15} color="#10b981" />
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#34d399', marginTop: '0.35rem', fontFamily: 'var(--font-mono)' }}>
              {stats.active_devices} Devices
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Kiosk-1, Kiosk-2, Kiosk-3
            </div>
          </div>

          <div className="industrial-card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Open Safety Conflicts</span>
              <Shield size={15} color={stats.open_conflicts > 0 ? '#ef4444' : '#10b981'} />
            </div>
            <div
              style={{
                fontSize: '1.6rem',
                fontWeight: 800,
                color: stats.open_conflicts > 0 ? '#f87171' : '#34d399',
                marginTop: '0.35rem',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {stats.open_conflicts} Pending
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              {stats.total_conflicts} Total Historical
            </div>
          </div>

          <div className="industrial-card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Vector Shard Spec</span>
              <Layers size={15} color="#a855f7" />
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#c084fc', marginTop: '0.35rem', fontFamily: 'var(--font-mono)' }}>
              {stats.vector_dimension}d Dense
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              Qdrant Snapshot Compatible
            </div>
          </div>
        </div>
      )}

      {/* Connected Kiosks Bar */}
      <div className="industrial-card" style={{ padding: '1rem 1.25rem' }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginBottom: '0.75rem' }}>
          Registered Plant Floor Edge Nodes
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem' }}>
          {Object.entries(devices).map(([devId, info]) => (
            <div
              key={devId}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                padding: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.65rem',
              }}
            >
              <span className="status-dot green" />
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#fff' }}>
                  {info.name}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  ID: {devId} • Last Sync: {info.last_sync ? new Date(info.last_sync).toLocaleTimeString() : 'Recent'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="industrial-card" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
            <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '0.85rem', top: '0.75rem' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search master procedures, authors, tags..."
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.6rem 0.85rem 0.6rem 2.4rem',
                color: '#fff',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <select
              value={machineFilter}
              onChange={(e) => setMachineFilter(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
              }}
            >
              <option value="ALL">All Machines</option>
              <option value="PRESS-03">PRESS-03 (Line 3)</option>
              <option value="CNC-01">CNC-01 (Mori Seiki)</option>
              <option value="CONV-04">CONV-04 (Packaging)</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
              }}
            >
              <option value="ALL">All Types</option>
              <option value="manual_section">OEM Manuals</option>
              <option value="tribal_note">Tribal Notes</option>
              <option value="safety_procedure">Safety Procedures</option>
              <option value="incident_log">Incident Logs</option>
            </select>
          </div>
        </div>

        {/* Entries Table */}
        <div style={{ marginTop: '1.25rem', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                <th style={{ padding: '0.65rem 0.5rem' }}>Type</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Title</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Machine</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Author</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Origin Device</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Version</th>
                <th style={{ padding: '0.65rem 0.5rem' }}>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map((e) => (
                <tr key={e.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                  <td style={{ padding: '0.65rem 0.5rem' }}>
                    <span style={{ fontSize: '0.72rem', textTransform: 'capitalize', color: 'var(--text-secondary)' }}>
                      {e.type.replace('_', ' ')}
                    </span>
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontWeight: 600, color: '#fff', maxWidth: '340px' }}>
                    {e.title}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                    {e.machine_id}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-secondary)' }}>
                    {e.created_by}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                    {e.device_id}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', fontFamily: 'var(--font-mono)', color: '#10b981' }}>
                    v{e.version}
                  </td>
                  <td style={{ padding: '0.65rem 0.5rem', color: 'var(--text-muted)' }}>
                    {new Date(e.updated_at).toLocaleDateString()}
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
