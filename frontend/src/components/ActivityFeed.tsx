'use client';

import React from 'react';
import {
  Activity,
  Zap,
  PenTool,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Wifi,
  WifiOff,
  Clock,
  Shield,
} from 'lucide-react';
import { ActivityEvent } from '../lib/types';

interface ActivityFeedProps {
  events: ActivityEvent[];
  title?: string;
}

export const ActivityFeed: React.FC<ActivityFeedProps> = ({
  events,
  title = 'System Telemetry & Activity Feed',
}) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'search':
        return <Zap size={14} color="#38bdf8" />;
      case 'write':
        return <PenTool size={14} color="#f59e0b" />;
      case 'sync_start':
      case 'sync_complete':
        return <RefreshCw size={14} color="#10b981" />;
      case 'conflict_raised':
        return <AlertTriangle size={14} color="#ef4444" />;
      case 'conflict_resolved':
        return <CheckCircle size={14} color="#10b981" />;
      case 'network_toggle':
        return <Wifi size={14} color="#f59e0b" />;
      default:
        return <Activity size={14} color="#94a3b8" />;
    }
  };

  return (
    <div className="industrial-card" style={{ padding: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
        <Activity size={18} color="#38bdf8" />
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff' }}>{title}</h3>
      </div>

      {events.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '1.5rem', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
          No recorded activity yet.
        </div>
      ) : (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '0.65rem',
            maxHeight: '420px',
            overflowY: 'auto',
          }}
        >
          {events.map((evt) => (
            <div
              key={evt.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem',
                padding: '0.65rem 0.85rem',
                backgroundColor: 'rgba(255, 255, 255, 0.02)',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.04)',
              }}
            >
              <div
                style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '6px',
                  backgroundColor: 'var(--bg-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginTop: '0.1rem',
                  flexShrink: 0,
                }}
              >
                {getIcon(evt.event_type)}
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#fff', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {evt.title}
                  </span>
                  <span
                    style={{
                      fontSize: '0.68rem',
                      fontFamily: 'var(--font-mono)',
                      color: 'var(--text-muted)',
                      flexShrink: 0,
                    }}
                  >
                    {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>

                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  {evt.description}
                </div>

                <div style={{ marginTop: '0.3rem', display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                  <span
                    style={{
                      fontSize: '0.65rem',
                      fontFamily: 'var(--font-mono)',
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      padding: '0.1rem 0.35rem',
                      borderRadius: '3px',
                      color: '#94a3b8',
                    }}
                  >
                    {evt.device_id}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
