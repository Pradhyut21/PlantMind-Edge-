'use client';

import React from 'react';
import {
  Wifi,
  WifiOff,
  HardDrive,
  Cpu,
  Layers,
  AlertTriangle,
  RefreshCw,
  Sliders,
  Shield,
} from 'lucide-react';

interface NavigationHeaderProps {
  currentView: 'kiosk' | 'cloud';
  onViewChange: (view: 'kiosk' | 'cloud') => void;
  activeDeviceId: string;
  onDeviceChange: (deviceId: string) => void;
  isOffline: boolean;
  onToggleOffline: () => void;
  openConflictsCount: number;
  lastSyncTime?: string;
  isSyncing: boolean;
  onTriggerSync: () => void;
}

export const NavigationHeader: React.FC<NavigationHeaderProps> = ({
  currentView,
  onViewChange,
  activeDeviceId,
  onDeviceChange,
  isOffline,
  onToggleOffline,
  openConflictsCount,
  lastSyncTime,
  isSyncing,
  onTriggerSync,
}) => {
  return (
    <header
      style={{
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'rgba(10, 13, 20, 0.95)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Top Banner if in Airplane Mode */}
      {isOffline && (
        <div
          style={{
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            borderBottom: '1px solid rgba(239, 68, 68, 0.4)',
            padding: '0.4rem 1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.6rem',
            color: '#f87171',
            fontSize: '0.82rem',
            fontWeight: 600,
            letterSpacing: '0.02em',
          }}
        >
          <WifiOff size={16} />
          <span>AIRPLANE MODE SIMULATED — Network severed. All reads & writes served 100% locally via Qdrant Edge (EdgeShard).</span>
          <button
            onClick={onToggleOffline}
            style={{
              marginLeft: '0.75rem',
              backgroundColor: '#ef4444',
              color: '#fff',
              border: 'none',
              padding: '0.2rem 0.6rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Reconnect LAN
          </button>
        </div>
      )}

      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '68px',
          gap: '1rem',
        }}
      >
        {/* Left: Branding & Tagline */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #ff7b00 0%, #b45309 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(255, 123, 0, 0.35)',
            }}
          >
            <Cpu size={22} color="#fff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#fff' }}>
                PlantMind
              </span>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 800,
                  backgroundColor: 'rgba(255, 123, 0, 0.2)',
                  color: '#ff7b00',
                  border: '1px solid rgba(255, 123, 0, 0.4)',
                  padding: '0.15rem 0.45rem',
                  borderRadius: '4px',
                  fontFamily: 'var(--font-mono)',
                }}
              >
                EDGE
              </span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Offline-First Industrial Knowledge Continuity • Qdrant Edge
            </div>
          </div>
        </div>

        {/* Center: Mode Switcher (Kiosk vs Central Office) */}
        <div
          style={{
            display: 'flex',
            backgroundColor: 'var(--bg-secondary)',
            padding: '3px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
          }}
        >
          <button
            onClick={() => onViewChange('kiosk')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: 'none',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              backgroundColor: currentView === 'kiosk' ? '#ff7b00' : 'transparent',
              color: currentView === 'kiosk' ? '#fff' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            <HardDrive size={15} />
            <span>Technician Kiosk (Edge)</span>
          </button>

          <button
            onClick={() => onViewChange('cloud')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '8px',
              border: 'none',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              backgroundColor: currentView === 'cloud' ? '#3b82f6' : 'transparent',
              color: currentView === 'cloud' ? '#fff' : 'var(--text-secondary)',
              transition: 'all 0.15s ease',
            }}
          >
            <Shield size={15} />
            <span>Central Office (Cloud)</span>
            {openConflictsCount > 0 && (
              <span
                style={{
                  backgroundColor: '#ef4444',
                  color: '#fff',
                  fontSize: '0.68rem',
                  padding: '0.1rem 0.4rem',
                  borderRadius: '999px',
                  fontWeight: 700,
                }}
              >
                {openConflictsCount}
              </span>
            )}
          </button>
        </div>

        {/* Right: Hardware Telemetry, Device Select & Airplane Mode Switch */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {/* Device Switcher (Simulation) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Device:</span>
            <select
              value={activeDeviceId}
              onChange={(e) => onDeviceChange(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-color)',
                padding: '0.4rem 0.65rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontFamily: 'var(--font-mono)',
                cursor: 'pointer',
              }}
            >
              <option value="kiosk-1">Kiosk-1 (Stamping Bay 3)</option>
              <option value="kiosk-2">Kiosk-2 (Machining Cell A)</option>
              <option value="kiosk-3">Kiosk-3 (Packaging Bay)</option>
            </select>
          </div>

          {/* Airplane Mode Toggle Button */}
          <button
            onClick={onToggleOffline}
            style={{
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              border: isOffline ? '1px solid #ef4444' : '1px solid #10b981',
              backgroundColor: isOffline ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              color: isOffline ? '#f87171' : '#34d399',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
            }}
            title={isOffline ? 'Click to connect network' : 'Click to simulate airplane mode'}
          >
            {isOffline ? <WifiOff size={15} /> : <Wifi size={15} />}
            <span>{isOffline ? 'OFFLINE (Airplane)' : 'ONLINE (LAN)'}</span>
          </button>

          {/* Sync Trigger Button */}
          <button
            onClick={onTriggerSync}
            disabled={isSyncing || isOffline}
            style={{
              padding: '0.45rem 0.85rem',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-tertiary)',
              color: isOffline ? 'var(--text-muted)' : 'var(--text-primary)',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: isOffline || isSyncing ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              opacity: isOffline ? 0.6 : 1,
            }}
            title={isOffline ? 'Connect network to sync' : 'Sync pending writes with cloud'}
          >
            <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
            <span>{isSyncing ? 'Syncing...' : 'Sync'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
