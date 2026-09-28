'use client';

import React, { useState } from 'react';
import {
  AlertTriangle,
  Shield,
  Sparkles,
  CheckCircle,
  Copy,
  GitMerge,
  Split,
  User,
  Clock,
  HardDrive,
  RefreshCw,
  Check,
  ChevronRight,
  Info,
} from 'lucide-react';
import { ConflictRecord, CompetingVersion, KnowledgeType } from '../lib/types';
import { resolveConflict, rerunConflictReasoning } from '../lib/api';

interface CloudConflictReconciliationProps {
  conflicts: ConflictRecord[];
  onRefresh: () => void;
}

export const CloudConflictReconciliation: React.FC<CloudConflictReconciliationProps> = ({
  conflicts,
  onRefresh,
}) => {
  const [selectedConflictId, setSelectedConflictId] = useState<string | null>(
    conflicts.length > 0 ? conflicts[0].id : null
  );
  const [resolutionMode, setResolutionMode] = useState<'view' | 'merge'>('view');
  const [mergedTitle, setMergedTitle] = useState('');
  const [mergedBody, setMergedBody] = useState('');
  const [resolutionNote, setResolutionNote] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isReasoning, setIsReasoning] = useState(false);
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const selectedConflict = conflicts.find((c) => c.id === selectedConflictId) || conflicts[0];

  const handlePickWinner = async (winnerIdx: number) => {
    if (!selectedConflict) return;
    setIsProcessing(true);
    setActionFeedback(null);
    try {
      const winner = selectedConflict.competing_versions[winnerIdx];
      await resolveConflict(selectedConflict.id, {
        resolution_type: 'winner_picked',
        winner_version_index: winnerIdx,
        resolution_note: resolutionNote || `Selected ${winner.label || `Version ${winner.version}`} by ${winner.created_by}`,
        resolved_by: 'Central Knowledge Manager',
      });
      setActionFeedback(`Resolved: Picked Version by ${winner.created_by} as master.`);
      onRefresh();
    } catch (err: any) {
      alert(`Error resolving conflict: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAnnotateBoth = async () => {
    if (!selectedConflict) return;
    setIsProcessing(true);
    setActionFeedback(null);
    try {
      await resolveConflict(selectedConflict.id, {
        resolution_type: 'both_annotated',
        resolution_note: resolutionNote || 'Both versions valid: created separate machine variant sub-entries.',
        resolved_by: 'Central Knowledge Manager',
      });
      setActionFeedback('Resolved: Both versions preserved as machine variants (RevA and RevB).');
      onRefresh();
    } catch (err: any) {
      alert(`Error resolving conflict: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const startMerge = () => {
    if (!selectedConflict || selectedConflict.competing_versions.length < 2) return;
    const vA = selectedConflict.competing_versions[0];
    const vB = selectedConflict.competing_versions[1];
    setMergedTitle(`${selectedConflict.entity_title} (Reconciled Standard)`);
    setMergedBody(
      `RECONCILED PROCEDURE (Approved by Safety Committee):\n\n[Primary Safety Protocol - From ${vA.created_by}]:\n${vA.body}\n\n[Authorized Emergency Shortcut - From ${vB.created_by}]:\n${vB.body}`
    );
    setResolutionMode('merge');
  };

  const handleExecuteMerge = async () => {
    if (!selectedConflict) return;
    setIsProcessing(true);
    try {
      await resolveConflict(selectedConflict.id, {
        resolution_type: 'merged',
        merged_title: mergedTitle,
        merged_body: mergedBody,
        resolution_note: resolutionNote || 'Manually merged competing procedures into unified revision.',
        resolved_by: 'Central Knowledge Manager',
      });
      setActionFeedback('Resolved: Master procedure updated with merged content.');
      setResolutionMode('view');
      onRefresh();
    } catch (err: any) {
      alert(`Error executing merge: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRerunReasoning = async () => {
    if (!selectedConflict) return;
    setIsReasoning(true);
    try {
      await rerunConflictReasoning(selectedConflict.id);
      onRefresh();
    } catch (err: any) {
      console.error('Reasoning failed:', err);
    } finally {
      setIsReasoning(false);
    }
  };

  if (!selectedConflict) {
    return (
      <div className="industrial-card" style={{ padding: '3rem', textAlign: 'center' }}>
        <CheckCircle size={40} color="#10b981" style={{ margin: '0 auto 1rem' }} />
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>No Active Conflicts in Queue</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
          All edge procedures and tribal updates are harmonized across kiosks and central office.
        </p>
      </div>
    );
  }

  const vA = selectedConflict.competing_versions[0] || {};
  const vB = selectedConflict.competing_versions[1] || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Banner Alert */}
      <div
        style={{
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          borderRadius: '10px',
          padding: '1rem 1.25rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertTriangle size={24} color="#ef4444" />
          <div>
            <div style={{ fontSize: '0.92rem', fontWeight: 800, color: '#fff' }}>
              Safety-Critical Conflict Detected — Human Reconciliation Required
            </div>
            <div style={{ fontSize: '0.78rem', color: '#f87171', marginTop: '0.15rem' }}>
              Two technicians updated {selectedConflict.machine_id} safety procedures while offline.
              Silent last-write-wins is blocked by safety policy.
            </div>
          </div>
        </div>

        {/* Conflict Selector if multiple */}
        {conflicts.length > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Conflict Queue:</span>
            <select
              value={selectedConflict.id}
              onChange={(e) => setSelectedConflictId(e.target.value)}
              style={{
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.35rem 0.65rem',
                borderRadius: '6px',
                fontSize: '0.78rem',
              }}
            >
              {conflicts.map((c, i) => (
                <option key={c.id} value={c.id}>
                  #{i + 1} - {c.entity_title.slice(0, 35)}... ({c.status})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {actionFeedback && (
        <div
          style={{
            padding: '0.75rem 1rem',
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            borderRadius: '8px',
            color: '#34d399',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <CheckCircle size={16} />
          <span>{actionFeedback}</span>
        </div>
      )}

      {/* Groq LLaMA Plain-Language AI Reasoning Card */}
      <div
        className="industrial-card"
        style={{
          border: '1px solid rgba(139, 92, 246, 0.4)',
          background: 'linear-gradient(180deg, rgba(139, 92, 246, 0.08) 0%, rgba(18, 25, 38, 0.95) 100%)',
          padding: '1.25rem',
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '0.85rem',
            flexWrap: 'wrap',
            gap: '0.5rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={18} color="#a855f7" />
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#fff' }}>
              Groq LLaMA — Conflict Reasoning & Safety Impact Analysis
            </h3>
            <span
              style={{
                fontSize: '0.68rem',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                color: '#c084fc',
                padding: '0.15rem 0.45rem',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
              }}
            >
              llama-3.3-70b
            </span>
          </div>

          <button
            onClick={handleRerunReasoning}
            disabled={isReasoning}
            style={{
              backgroundColor: 'rgba(139, 92, 246, 0.15)',
              color: '#c084fc',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              padding: '0.3rem 0.75rem',
              borderRadius: '6px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: isReasoning ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <RefreshCw size={12} className={isReasoning ? 'animate-spin' : ''} />
            <span>{isReasoning ? 'Reasoning...' : 'Re-Run LLaMA Analysis'}</span>
          </button>
        </div>

        {/* AI Summary Content */}
        <div
          style={{
            fontSize: '0.85rem',
            lineHeight: '1.6',
            color: '#e2e8f0',
            whiteSpace: 'pre-wrap',
            backgroundColor: 'rgba(0, 0, 0, 0.3)',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          {selectedConflict.ai_summary || 'Analyzing conflict parameter variances and safety risks...'}
        </div>
      </div>

      {/* Side-by-Side Comparison Columns */}
      {resolutionMode === 'view' ? (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {/* Version A Card */}
          <div
            className="industrial-card"
            style={{
              border: '1px solid #3b82f6',
              borderTop: '4px solid #3b82f6',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span
                  style={{
                    backgroundColor: 'rgba(59, 130, 246, 0.15)',
                    color: '#60a5fa',
                    border: '1px solid rgba(59, 130, 246, 0.4)',
                    padding: '0.2rem 0.55rem',
                    borderRadius: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  Version A ({vA.device_id || 'kiosk-1'})
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Rev #{vA.version || 2}
                </span>
              </div>

              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>
                {vA.title}
              </h4>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                Author: <strong style={{ color: '#fff' }}>{vA.created_by}</strong> • Device:{' '}
                <span style={{ fontFamily: 'var(--font-mono)' }}>{vA.device_id}</span>
              </div>

              <div
                style={{
                  fontSize: '0.84rem',
                  lineHeight: '1.55',
                  color: '#cbd5e1',
                  backgroundColor: 'rgba(0, 0, 0, 0.25)',
                  padding: '0.85rem',
                  borderRadius: '6px',
                  whiteSpace: 'pre-wrap',
                  border: '1px solid rgba(255, 255, 255, 0.04)',
                }}
              >
                {vA.body}
              </div>
            </div>

            {/* Pick Winner A Button */}
            <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <button
                onClick={() => handlePickWinner(0)}
                disabled={isProcessing}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', backgroundColor: '#2563eb' }}
              >
                <Check size={16} />
                <span>Pick Version A (Enforce Master)</span>
              </button>
            </div>
          </div>

          {/* Version B Card */}
          <div
            className="industrial-card"
            style={{
              border: '1px solid #f59e0b',
              borderTop: '4px solid #f59e0b',
              padding: '1.25rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span
                  style={{
                    backgroundColor: 'rgba(245, 158, 11, 0.15)',
                    color: '#fbbf24',
                    border: '1px solid rgba(245, 158, 11, 0.4)',
                    padding: '0.2rem 0.55rem',
                    borderRadius: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)',
                  }}
                >
                  Version B ({vB.device_id || 'kiosk-2'})
                </span>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Rev #{vB.version || 2}
                </span>
              </div>

              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>
                {vB.title}
              </h4>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
                Author: <strong style={{ color: '#fff' }}>{vB.created_by}</strong> • Device:{' '}
                <span style={{ fontFamily: 'var(--font-mono)' }}>{vB.device_id}</span>
              </div>

              <div
                style={{
                  fontSize: '0.84rem',
                  lineHeight: '1.55',
                  color: '#cbd5e1',
                  backgroundColor: 'rgba(0, 0, 0, 0.25)',
                  padding: '0.85rem',
                  borderRadius: '6px',
                  whiteSpace: 'pre-wrap',
                  border: '1px solid rgba(255, 255, 255, 0.04)',
                }}
              >
                {vB.body}
              </div>
            </div>

            {/* Pick Winner B Button */}
            <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
              <button
                onClick={() => handlePickWinner(1)}
                disabled={isProcessing}
                className="btn-primary"
                style={{ width: '100%', justifyContent: 'center', backgroundColor: '#d97706' }}
              >
                <Check size={16} />
                <span>Pick Version B (Enforce Master)</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Manual Merge Editor */
        <div className="industrial-card" style={{ padding: '1.5rem', border: '1px solid #a855f7' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff', marginBottom: '0.5rem' }}>
            Manual Merge Editor — Crafting Master Standard
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Combine safe elements from Version A with authorized workflow requirements from Version B.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Unified Procedure Title
              </label>
              <input
                type="text"
                value={mergedTitle}
                onChange={(e) => setMergedTitle(e.target.value)}
                style={{
                  width: '100%',
                  backgroundColor: 'var(--bg-secondary)',
                  color: '#fff',
                  border: '1px solid var(--border-color)',
                  padding: '0.65rem',
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Merged Procedure Content
              </label>
              <textarea
                rows={8}
                value={mergedBody}
                onChange={(e) => setMergedBody(e.target.value)}
                style={{
                  width: '100%',
                  backgroundColor: 'var(--bg-secondary)',
                  color: '#fff',
                  border: '1px solid var(--border-color)',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  fontSize: '0.85rem',
                  lineHeight: '1.5',
                  fontFamily: 'inherit',
                }}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button
                type="button"
                onClick={() => setResolutionMode('view')}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleExecuteMerge}
                disabled={isProcessing}
                className="btn-primary"
              >
                <GitMerge size={16} />
                <span>Save Merged Standard & Resolve</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alternative Resolution Actions Bar */}
      {resolutionMode === 'view' && (
        <div
          className="industrial-card"
          style={{
            padding: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
          }}
        >
          {/* Resolution Note Input */}
          <div style={{ flex: 1, minWidth: '260px' }}>
            <label style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
              Audit Resolution Note (Mandatory for Safety Compliance):
            </label>
            <input
              type="text"
              value={resolutionNote}
              onChange={(e) => setResolutionNote(e.target.value)}
              placeholder="e.g. Approved Dave Miller rev2; Frank's bypass rejected per OSHA zero-energy mandate."
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.5rem 0.75rem',
                borderRadius: '6px',
                fontSize: '0.8rem',
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {/* Merge Manually Button */}
            <button
              onClick={startMerge}
              disabled={isProcessing}
              className="btn-secondary"
              style={{ fontSize: '0.82rem' }}
            >
              <GitMerge size={16} color="#a855f7" />
              <span>Merge Manually</span>
            </button>

            {/* Annotate Both as Valid Button */}
            <button
              onClick={handleAnnotateBoth}
              disabled={isProcessing}
              className="btn-secondary"
              style={{ fontSize: '0.82rem' }}
              title="Preserve both as separate machine variants"
            >
              <Split size={16} color="#38bdf8" />
              <span>Annotate Both as Valid (Sub-Variants)</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
