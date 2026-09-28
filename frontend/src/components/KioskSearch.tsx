'use client';

import React, { useState, useEffect } from 'react';
import {
  Search,
  Mic,
  MicOff,
  Filter,
  Zap,
  CheckCircle2,
  Clock,
  User,
  Shield,
  BookOpen,
  AlertOctagon,
  FileText,
  Lock,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { KnowledgeEntry, KnowledgeType, SyncStatus } from '../lib/types';
import { searchLocalEdge, toggleKeepLocalPolicy } from '../lib/api';

interface KioskSearchProps {
  deviceId: string;
  isOffline: boolean;
  onRefreshEntries?: () => void;
}

export const KioskSearch: React.FC<KioskSearchProps> = ({
  deviceId,
  isOffline,
  onRefreshEntries,
}) => {
  const [query, setQuery] = useState('');
  const [machineId, setMachineId] = useState('ALL');
  const [entryType, setEntryType] = useState('ALL');
  const [results, setResults] = useState<KnowledgeEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchLatencyMs, setSearchLatencyMs] = useState<number | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Quick symptom chips
  const quickSymptoms = [
    { label: 'Hydraulic pressure drop Line 3', q: 'hydraulic pressure keeps dropping on line 3 press' },
    { label: 'CNC-01 high-RPM vibration', q: 'harmonic vibration and chattering at high rpm on CNC spindle' },
    { label: 'LOTO Line 3 Depressurization', q: 'lockout depressurize hydraulic pressure before die maintenance' },
    { label: 'Line 3 reed switch sticking', q: 'proximity reed switch sticking in humid conditions' },
  ];

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setSearchLatencyMs(null);
      return;
    }

    setIsLoading(true);
    const start = performance.now();
    try {
      const data = await searchLocalEdge(searchQuery, {
        machineId: machineId !== 'ALL' ? machineId : undefined,
        entryType: entryType !== 'ALL' ? entryType : undefined,
        deviceId,
        limit: 8,
      });
      const end = performance.now();
      setResults(data);
      setSearchLatencyMs(Math.round(end - start));
      if (data.length > 0 && !expandedId) {
        setExpandedId(data[0].id);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser. Please use keyboard input.');
      return;
    }

    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setIsListening(false);
      performSearch(transcript);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleTogglePolicy = async (entryId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await toggleKeepLocalPolicy(entryId, deviceId);
      // Refresh current results
      performSearch(query);
      if (onRefreshEntries) onRefreshEntries();
    } catch (err) {
      console.error('Policy toggle error:', err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Search Input Box */}
      <div className="industrial-card" style={{ padding: '1.5rem', border: '1px solid #2a3952' }}>
        <div style={{ display: 'flex', gap: '0.75rem', position: 'relative' }}>
          <div
            style={{
              position: 'relative',
              flex: 1,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <Search
              size={20}
              color="var(--text-muted)"
              style={{ position: 'absolute', left: '1rem', pointerEvents: 'none' }}
            />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && performSearch(query)}
              placeholder="Search fault symptoms or procedures (e.g. 'hydraulic pressure keeps dropping on line 3 press')..."
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '0.85rem 3.5rem 0.85rem 2.85rem',
                color: '#fff',
                fontSize: '0.98rem',
                outline: 'none',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)',
              }}
            />
            {/* Microphone Button */}
            <button
              onClick={handleVoiceInput}
              className={isListening ? 'voice-listening' : ''}
              style={{
                position: 'absolute',
                right: '0.75rem',
                background: isListening ? '#ff7b00' : 'var(--bg-tertiary)',
                color: isListening ? '#fff' : 'var(--text-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.45rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              title="Voice Input (Speech-to-Text for glove operation)"
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
            </button>
          </div>

          {/* Search Button */}
          <button
            onClick={() => performSearch(query)}
            className="btn-primary"
            style={{ padding: '0.85rem 1.5rem', fontSize: '0.95rem' }}
          >
            <Zap size={18} />
            <span>Search</span>
          </button>
        </div>

        {/* Quick Symptoms Chips */}
        <div style={{ marginTop: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Common Fault Symptoms:
          </span>
          {quickSymptoms.map((chip, i) => (
            <button
              key={i}
              onClick={() => {
                setQuery(chip.q);
                performSearch(chip.q);
              }}
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-color)',
                padding: '0.25rem 0.65rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#ff7b00')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-color)')}
            >
              {chip.label}
            </button>
          ))}
        </div>

        {/* Filter Controls Row */}
        <div
          style={{
            marginTop: '1.25rem',
            paddingTop: '1rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* Machine Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Machine:</span>
              <select
                value={machineId}
                onChange={(e) => {
                  setMachineId(e.target.value);
                  if (query) performSearch(query);
                }}
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-color)',
                  padding: '0.35rem 0.65rem',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  fontFamily: 'var(--font-mono)',
                  cursor: 'pointer',
                }}
              >
                <option value="ALL">All Machinery</option>
                <option value="PRESS-03">PRESS-03 (Line 3 Stamping)</option>
                <option value="CNC-01">CNC-01 (Mori Seiki 5-Axis)</option>
                <option value="CONV-04">CONV-04 (Packaging Bay)</option>
              </select>
            </div>

            {/* Entry Type Filter */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Type:</span>
              <select
                value={entryType}
                onChange={(e) => {
                  setEntryType(e.target.value);
                  if (query) performSearch(query);
                }}
                style={{
                  backgroundColor: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-color)',
                  padding: '0.35rem 0.65rem',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  cursor: 'pointer',
                }}
              >
                <option value="ALL">All Knowledge Types</option>
                <option value="tribal_note">Tribal Notes</option>
                <option value="safety_procedure">Safety Procedures</option>
                <option value="manual_section">OEM Manuals</option>
                <option value="incident_log">Incident Logs</option>
              </select>
            </div>
          </div>

          {/* Offline Engine Telemetry Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span className="status-dot cyan" />
            <span
              style={{
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)',
                color: '#38bdf8',
                fontWeight: 600,
              }}
            >
              Qdrant EdgeShard
            </span>
            {searchLatencyMs !== null && (
              <span
                style={{
                  backgroundColor: 'rgba(6, 182, 212, 0.15)',
                  color: '#06b6d4',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                }}
              >
                {searchLatencyMs}ms (Offline)
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '0.75rem',
          }}
        >
          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            {isLoading
              ? 'Querying local EdgeShard vectors...'
              : results.length > 0
              ? `Found ${results.length} Local Matches for "${query}"`
              : query
              ? 'No matching procedures found in local shard'
              : 'Enter a symptom or select a quick query above'}
          </div>
        </div>

        {/* Results List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {results.map((entry) => {
            const isExpanded = expandedId === entry.id;
            const matchPercent = entry.similarity_score
              ? Math.round(entry.similarity_score * 100)
              : null;

            return (
              <div
                key={entry.id}
                className="industrial-card"
                onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                style={{
                  cursor: 'pointer',
                  borderLeft:
                    entry.type === KnowledgeType.SAFETY_PROCEDURE
                      ? '4px solid #ef4444'
                      : entry.type === KnowledgeType.TRIBAL_NOTE
                      ? '4px solid #f59e0b'
                      : '4px solid #38bdf8',
                }}
              >
                {/* Header Row */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    gap: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      {/* Type Badge */}
                      {entry.type === KnowledgeType.MANUAL_SECTION && (
                        <span className="badge badge-manual">
                          <BookOpen size={11} /> OEM Manual
                        </span>
                      )}
                      {entry.type === KnowledgeType.TRIBAL_NOTE && (
                        <span className="badge badge-tribal">
                          <User size={11} /> Tribal Note
                        </span>
                      )}
                      {entry.type === KnowledgeType.SAFETY_PROCEDURE && (
                        <span className="badge badge-safety">
                          <Shield size={11} /> Safety Procedure
                        </span>
                      )}
                      {entry.type === KnowledgeType.INCIDENT_LOG && (
                        <span className="badge badge-incident">
                          <AlertOctagon size={11} /> Incident Log
                        </span>
                      )}

                      {/* Machine Tag */}
                      <span
                        style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.08)',
                          color: '#fff',
                          fontFamily: 'var(--font-mono)',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          padding: '0.15rem 0.5rem',
                          borderRadius: '4px',
                        }}
                      >
                        {entry.machine_id}
                      </span>

                      {/* Sync Status Badge */}
                      {entry.sync_status === SyncStatus.SYNCED && (
                        <span className="badge badge-synced">
                          <CheckCircle2 size={11} /> Synced
                        </span>
                      )}
                      {entry.sync_status === SyncStatus.LOCAL_ONLY && (
                        <span className="badge badge-local-only">
                          <Lock size={11} /> Local Only
                        </span>
                      )}
                      {entry.sync_status === SyncStatus.CONFLICT && (
                        <span className="badge badge-conflict">
                          <Shield size={11} /> Conflict Open
                        </span>
                      )}

                      {/* Policy Flag Pill */}
                      {entry.keep_local_until_reviewed && (
                        <span
                          style={{
                            fontSize: '0.68rem',
                            backgroundColor: 'rgba(234, 179, 8, 0.15)',
                            color: '#facc15',
                            padding: '0.15rem 0.45rem',
                            borderRadius: '4px',
                            border: '1px solid rgba(234, 179, 8, 0.3)',
                          }}
                        >
                          Held Local (Policy)
                        </span>
                      )}
                    </div>

                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginTop: '0.2rem' }}>
                      {entry.title}
                    </h3>
                  </div>

                  {/* Similarity Score & Toggle Button */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    {matchPercent !== null && (
                      <div
                        style={{
                          textAlign: 'right',
                          backgroundColor: 'rgba(6, 182, 212, 0.1)',
                          border: '1px solid rgba(6, 182, 212, 0.25)',
                          padding: '0.3rem 0.65rem',
                          borderRadius: '6px',
                        }}
                      >
                        <div
                          style={{
                            fontSize: '0.85rem',
                            fontWeight: 800,
                            color: '#38bdf8',
                            fontFamily: 'var(--font-mono)',
                          }}
                        >
                          {matchPercent}%
                        </div>
                        <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Semantic Match</div>
                      </div>
                    )}
                    {isExpanded ? <ChevronUp size={18} color="var(--text-muted)" /> : <ChevronDown size={18} color="var(--text-muted)" />}
                  </div>
                </div>

                {/* Author attribution & Area */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    fontSize: '0.78rem',
                    color: 'var(--text-secondary)',
                    marginTop: '0.4rem',
                  }}
                >
                  <span>By: <strong style={{ color: '#fff' }}>{entry.created_by}</strong></span>
                  <span>•</span>
                  <span>Area: {entry.area_tag}</span>
                  <span>•</span>
                  <span>Origin: <span style={{ fontFamily: 'var(--font-mono)' }}>{entry.device_id}</span></span>
                </div>

                {/* Body Content */}
                <div
                  style={{
                    marginTop: '0.85rem',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                    fontSize: '0.88rem',
                    lineHeight: '1.55',
                    color: '#e2e8f0',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {isExpanded ? entry.body : `${entry.body.slice(0, 180)}...`}
                </div>

                {/* Tags and Policy Control */}
                {isExpanded && (
                  <div
                    style={{
                      marginTop: '1rem',
                      paddingTop: '0.75rem',
                      borderTop: '1px dashed var(--border-color)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '0.75rem',
                    }}
                  >
                    <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                      {entry.tags.map((t, idx) => (
                        <span
                          key={idx}
                          style={{
                            fontSize: '0.72rem',
                            backgroundColor: 'rgba(255, 255, 255, 0.06)',
                            color: 'var(--text-secondary)',
                            padding: '0.15rem 0.5rem',
                            borderRadius: '4px',
                            fontFamily: 'var(--font-mono)',
                          }}
                        >
                          #{t}
                        </span>
                      ))}
                    </div>

                    {/* Data Policy Button */}
                    <button
                      onClick={(e) => handleTogglePolicy(entry.id, e)}
                      style={{
                        backgroundColor: entry.keep_local_until_reviewed
                          ? 'rgba(234, 179, 8, 0.15)'
                          : 'rgba(255, 255, 255, 0.05)',
                        color: entry.keep_local_until_reviewed ? '#facc15' : 'var(--text-muted)',
                        border: entry.keep_local_until_reviewed
                          ? '1px solid rgba(234, 179, 8, 0.4)'
                          : '1px solid var(--border-color)',
                        padding: '0.3rem 0.75rem',
                        borderRadius: '6px',
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                      }}
                    >
                      <Lock size={12} />
                      <span>
                        Policy: {entry.keep_local_until_reviewed ? 'Keep Local Only (Active)' : 'Allow Sync to Cloud'}
                      </span>
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
