'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  HardDrive,
  Shield,
  Search,
  PenTool,
  Cpu,
  Layers,
  Activity,
  AlertTriangle,
  RefreshCw,
  WifiOff,
  Wifi,
  Sparkles,
  FileText,
  Sliders,
  Database,
  ArrowRight,
} from 'lucide-react';

import {
  KnowledgeEntry,
  ConflictRecord,
  DeviceMemoryStats,
  ActivityEvent,
  CloudStats,
} from '../lib/types';
import {
  getEdgeStatus,
  toggleNetworkOffline,
  switchEdgeDevice,
  inspectDeviceMemory,
  getLocalEntries,
  triggerEdgeSync,
  getEdgeActivity,
  getCloudStats,
  getCloudEntries,
  getConflicts,
  getCloudActivity,
  getDevices,
} from '../lib/api';

import { NavigationHeader } from '../components/NavigationHeader';
import { KioskSearch } from '../components/KioskSearch';
import { KioskWrite } from '../components/KioskWrite';
import { DeviceMemoryInspector } from '../components/DeviceMemoryInspector';
import { SyncControl } from '../components/SyncControl';
import { ActivityFeed } from '../components/ActivityFeed';
import { CloudConflictReconciliation } from '../components/CloudConflictReconciliation';
import { CloudKnowledgeExplorer } from '../components/CloudKnowledgeExplorer';

export default function PlantMindDashboard() {
  const [currentView, setCurrentView] = useState<'kiosk' | 'cloud'>('kiosk');
  const [activeDeviceId, setActiveDeviceId] = useState<string>('kiosk-1');
  const [isOffline, setIsOffline] = useState<boolean>(false);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [lastSyncResult, setLastSyncResult] = useState<any>(null);

  // Kiosk sub-tabs
  const [kioskTab, setKioskTab] = useState<'search' | 'write' | 'memory'>('search');

  // Cloud sub-tabs
  const [cloudTab, setCloudTab] = useState<'reconcile' | 'explorer'>('reconcile');

  // Data states
  const [edgeStats, setEdgeStats] = useState<DeviceMemoryStats | null>(null);
  const [edgeEntries, setEdgeEntries] = useState<KnowledgeEntry[]>([]);
  const [cloudStats, setCloudStats] = useState<CloudStats | null>(null);
  const [cloudEntries, setCloudEntries] = useState<KnowledgeEntry[]>([]);
  const [conflicts, setConflicts] = useState<ConflictRecord[]>([]);
  const [activityEvents, setActivityEvents] = useState<ActivityEvent[]>([]);
  const [devices, setDevices] = useState<Record<string, any>>({});

  // Register PWA Service Worker
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => console.log('PlantMind PWA Service Worker registered:', reg.scope))
        .catch((err) => console.warn('Service Worker registration skipped:', err));
    }
  }, []);

  // Fetch Edge Data
  const fetchEdgeData = useCallback(async () => {
    try {
      const [status, mem, entries, act] = await Promise.all([
        getEdgeStatus(activeDeviceId).catch(() => null),
        inspectDeviceMemory(activeDeviceId).catch(() => null),
        getLocalEntries({ deviceId: activeDeviceId, limit: 100 }).catch(() => []),
        getEdgeActivity(activeDeviceId, 40).catch(() => []),
      ]);

      if (status) {
        setIsOffline(status.is_offline_simulation);
      }
      if (mem) {
        setEdgeStats(mem);
      }
      setEdgeEntries(entries);
      setActivityEvents(act);
    } catch (err) {
      console.warn('Error fetching edge data:', err);
    }
  }, [activeDeviceId]);

  // Fetch Cloud Data
  const fetchCloudData = useCallback(async () => {
    try {
      const [cStats, cEntries, cConflicts, cAct, cDevices] = await Promise.all([
        getCloudStats().catch(() => null),
        getCloudEntries({ limit: 150 }).catch(() => []),
        getConflicts('open').catch(() => []),
        getCloudActivity(40).catch(() => []),
        getDevices().catch(() => ({})),
      ]);

      if (cStats) setCloudStats(cStats);
      setCloudEntries(cEntries);
      setConflicts(cConflicts);
      setDevices(cDevices);
      if (currentView === 'cloud') {
        setActivityEvents(cAct);
      }
    } catch (err) {
      console.warn('Error fetching cloud data:', err);
    }
  }, [currentView]);

  // Initial load and periodic polling
  useEffect(() => {
    fetchEdgeData();
    fetchCloudData();

    const interval = setInterval(() => {
      if (currentView === 'kiosk') {
        fetchEdgeData();
      } else {
        fetchCloudData();
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [fetchEdgeData, fetchCloudData, currentView]);

  // Handle Airplane Mode Toggle (Section 5 requirement: network severed vs connected)
  const handleToggleOffline = async () => {
    const nextOffline = !isOffline;
    setIsOffline(nextOffline);
    try {
      await toggleNetworkOffline(nextOffline, activeDeviceId);
      await fetchEdgeData();

      // AUTO-SYNC TRIGGER (Requirement 3):
      // When transitioning from offline back to online, automatically trigger sync!
      if (!nextOffline) {
        console.log('LAN Connectivity re-established. Automatically kicking off sync session...');
        await handleTriggerSync();
      }
    } catch (err) {
      console.error('Failed to toggle network mode:', err);
    }
  };

  // Handle Device Switch
  const handleDeviceChange = async (newDeviceId: string) => {
    setActiveDeviceId(newDeviceId);
    try {
      await switchEdgeDevice(newDeviceId);
      await fetchEdgeData();
    } catch (err) {
      console.error('Failed to switch device:', err);
    }
  };

  // Handle Manual / Auto Sync Trigger
  const handleTriggerSync = async () => {
    if (isOffline) {
      alert('Kiosk is currently in Airplane Mode. Please reconnect network before syncing.');
      return;
    }
    setIsSyncing(true);
    try {
      const result = await triggerEdgeSync(activeDeviceId);
      setLastSyncResult(result);
      await Promise.all([fetchEdgeData(), fetchCloudData()]);
    } catch (err: any) {
      setLastSyncResult({
        success: false,
        entries_pushed: 0,
        entries_pulled: 0,
        conflicts_raised: 0,
        message: err.message || 'Sync failed',
      });
    } finally {
      setIsSyncing(false);
    }
  };

  const openConflictsCount = conflicts.length;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Universal Navigation Header */}
      <NavigationHeader
        currentView={currentView}
        onViewChange={setCurrentView}
        activeDeviceId={activeDeviceId}
        onDeviceChange={handleDeviceChange}
        isOffline={isOffline}
        onToggleOffline={handleToggleOffline}
        openConflictsCount={openConflictsCount}
        lastSyncTime={edgeStats?.last_sync_time}
        isSyncing={isSyncing}
        onTriggerSync={handleTriggerSync}
      />

      {/* Main Body Content */}
      <main className="container" style={{ flex: 1, padding: '1.5rem 1.25rem 3rem' }}>
        {currentView === 'kiosk' ? (
          /* ======================================================== */
          /* TECHNICIAN KIOSK / TABLET VIEW (EDGE NODE)               */
          /* ======================================================== */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Kiosk Mode Sub-Navigation Bar */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid var(--border-color)',
                paddingBottom: '0.85rem',
                flexWrap: 'wrap',
                gap: '0.75rem',
              }}
            >
              {/* Tabs */}
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setKioskTab('search')}
                  style={{
                    backgroundColor: kioskTab === 'search' ? 'rgba(255, 123, 0, 0.15)' : 'transparent',
                    color: kioskTab === 'search' ? '#ff7b00' : 'var(--text-secondary)',
                    border: kioskTab === 'search' ? '1px solid #ff7b00' : '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                  }}
                >
                  <Search size={15} />
                  <span>Offline Semantic Search</span>
                </button>

                <button
                  onClick={() => setKioskTab('write')}
                  style={{
                    backgroundColor: kioskTab === 'write' ? 'rgba(255, 123, 0, 0.15)' : 'transparent',
                    color: kioskTab === 'write' ? '#ff7b00' : 'var(--text-secondary)',
                    border: kioskTab === 'write' ? '1px solid #ff7b00' : '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                  }}
                >
                  <PenTool size={15} />
                  <span>Log Observation (Append-Only)</span>
                </button>

                <button
                  onClick={() => setKioskTab('memory')}
                  style={{
                    backgroundColor: kioskTab === 'memory' ? 'rgba(255, 123, 0, 0.15)' : 'transparent',
                    color: kioskTab === 'memory' ? '#ff7b00' : 'var(--text-secondary)',
                    border: kioskTab === 'memory' ? '1px solid #ff7b00' : '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                  }}
                >
                  <Cpu size={15} />
                  <span>Device Memory Inspector</span>
                  {edgeStats && (
                    <span
                      style={{
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        padding: '0.1rem 0.4rem',
                        borderRadius: '999px',
                        fontSize: '0.7rem',
                      }}
                    >
                      {edgeStats.total_entries}
                    </span>
                  )}
                </button>
              </div>

              {/* Edge Node Telemetry Badge */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span className="status-dot green" />
                <span>Node: <strong style={{ color: '#fff' }}>{activeDeviceId}</strong></span>
                <span>•</span>
                <span>FastEmbed ONNX 384d</span>
                <span>•</span>
                <span>Port 8000</span>
              </div>
            </div>

            {/* Layout: Main Work Area + Side Telemetry Panel */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1fr) 340px',
                gap: '1.25rem',
                alignItems: 'start',
              }}
            >
              {/* Left Column: Active Kiosk Tab */}
              <div>
                {kioskTab === 'search' && (
                  <KioskSearch
                    deviceId={activeDeviceId}
                    isOffline={isOffline}
                    onRefreshEntries={fetchEdgeData}
                  />
                )}
                {kioskTab === 'write' && (
                  <KioskWrite
                    deviceId={activeDeviceId}
                    isOffline={isOffline}
                    onEntryCreated={fetchEdgeData}
                  />
                )}
                {kioskTab === 'memory' && (
                  <DeviceMemoryInspector
                    stats={edgeStats}
                    entries={edgeEntries}
                    deviceId={activeDeviceId}
                    onRefresh={fetchEdgeData}
                  />
                )}
              </div>

              {/* Right Column: Sync Controller & Activity Feed */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <SyncControl
                  isOffline={isOffline}
                  onToggleOffline={handleToggleOffline}
                  isSyncing={isSyncing}
                  onTriggerSync={handleTriggerSync}
                  lastSyncResult={lastSyncResult}
                  pendingCount={edgeStats?.pending_sync_count || 0}
                />

                <ActivityFeed
                  events={activityEvents}
                  title={`Activity Feed (${activeDeviceId})`}
                />
              </div>
            </div>
          </div>
        ) : (
          /* ======================================================== */
          /* CENTRAL OFFICE ADMIN / CLOUD DASHBOARD VIEW              */
          /* ======================================================== */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Cloud Sub-Navigation Bar */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid var(--border-color)',
                paddingBottom: '0.85rem',
                flexWrap: 'wrap',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setCloudTab('reconcile')}
                  style={{
                    backgroundColor: cloudTab === 'reconcile' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    color: cloudTab === 'reconcile' ? '#60a5fa' : 'var(--text-secondary)',
                    border: cloudTab === 'reconcile' ? '1px solid #3b82f6' : '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                  }}
                >
                  <Shield size={15} />
                  <span>Conflict Reconciliation Queue</span>
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

                <button
                  onClick={() => setCloudTab('explorer')}
                  style={{
                    backgroundColor: cloudTab === 'explorer' ? 'rgba(59, 130, 246, 0.15)' : 'transparent',
                    color: cloudTab === 'explorer' ? '#60a5fa' : 'var(--text-secondary)',
                    border: cloudTab === 'explorer' ? '1px solid #3b82f6' : '1px solid var(--border-color)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.45rem',
                  }}
                >
                  <Database size={15} />
                  <span>Central Knowledge Explorer</span>
                </button>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span className="status-dot green" />
                <span>Qdrant Server: <strong style={{ color: '#fff' }}>Central-Master</strong></span>
                <span>•</span>
                <span>Groq LLaMA-3.3-70b</span>
                <span>•</span>
                <span>Port 8001</span>
              </div>
            </div>

            {/* Cloud Content View */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'minmax(0, 1fr) 340px',
                gap: '1.25rem',
                alignItems: 'start',
              }}
            >
              {/* Left Column: Conflict Reconciler or Explorer */}
              <div>
                {cloudTab === 'reconcile' ? (
                  <CloudConflictReconciliation
                    conflicts={conflicts}
                    onRefresh={fetchCloudData}
                  />
                ) : (
                  <CloudKnowledgeExplorer
                    entries={cloudEntries}
                    stats={cloudStats}
                    devices={devices}
                  />
                )}
              </div>

              {/* Right Column: Central Activity Stream */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <ActivityFeed
                  events={activityEvents}
                  title="Central Audit & Sync Log"
                />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          padding: '1rem 0',
          backgroundColor: 'rgba(10, 13, 20, 0.8)',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
        }}
      >
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <strong>PlantMind Edge</strong> — Offline-First Industrial Knowledge Continuity • Built with Qdrant Edge, FastAPI & Next.js
          </div>
          <div style={{ fontFamily: 'var(--font-mono)' }}>
            github.com/Pradhyut21 • Active Node: {activeDeviceId}
          </div>
        </div>
      </footer>
    </div>
  );
}
