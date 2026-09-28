'use client';

import React, { useState } from 'react';
import {
  PenTool,
  CheckCircle,
  AlertCircle,
  Lock,
  Layers,
  Shield,
  User,
  AlertOctagon,
  Sparkles,
} from 'lucide-react';
import { KnowledgeType } from '../lib/types';
import { createLocalEntry } from '../lib/api';

interface KioskWriteProps {
  deviceId: string;
  isOffline: boolean;
  onEntryCreated?: () => void;
}

export const KioskWrite: React.FC<KioskWriteProps> = ({
  deviceId,
  isOffline,
  onEntryCreated,
}) => {
  const [type, setType] = useState<KnowledgeType>(KnowledgeType.TRIBAL_NOTE);
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [machineId, setMachineId] = useState('PRESS-03');
  const [areaTag, setAreaTag] = useState('Stamping Line 3');
  const [createdBy, setCreatedBy] = useState('Dave Miller (Senior Tech)');
  const [tagsInput, setTagsInput] = useState('hydraulic, pressure-drop, tribal');
  const [keepLocal, setKeepLocal] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ success: boolean; message: string } | null>(null);

  // Pre-fill realistic templates for quick technician logging
  const loadTemplate = (kind: 'hydraulic_relief' | 'sensor_override') => {
    if (kind === 'hydraulic_relief') {
      setType(KnowledgeType.TRIBAL_NOTE);
      setTitle('Tribal Tip: Line 3 Press Pilot Relief Valve Whistling Remedy');
      setBody(
        'Observation during night shift: If you hear high-frequency whistling near pilot valve PV-02 when tonnage peaks, the pilot orifice is cavitating. Instead of shutting down the whole line, slightly loosen the dampening bypass needle a 1/4 turn. Whistling ceases immediately and cycle pressure stabilizes at 208 bar.'
      );
      setMachineId('PRESS-03');
      setAreaTag('Stamping Line 3');
      setCreatedBy('Dave Miller (Senior Tech)');
      setTagsInput('hydraulic, relief-valve, whistling, cavitation, quick-fix');
      setKeepLocal(false);
    } else if (kind === 'sensor_override') {
      setType(KnowledgeType.TRIBAL_NOTE);
      setTitle('Draft Note: Optical Curtain Sensitivity Drift in Cold Starts');
      setBody(
        'During winter morning start-ups, the Sick optical safety light curtain trips falsely on mist from the cooling tower. Wiping the optical emitter lens with an anti-fog cloth prevents nuisance trips.'
      );
      setMachineId('PRESS-03');
      setAreaTag('Stamping Line 3');
      setCreatedBy('Junior Tech Leo');
      setTagsInput('optical-curtain, safety, mist, winter-drift');
      setKeepLocal(true); // Demonstrating deliberate local policy!
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) {
      setFeedback({ success: false, message: 'Please provide both a title and observation details.' });
      return;
    }

    setIsSubmitting(true);
    setFeedback(null);

    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

    try {
      const created = await createLocalEntry(
        {
          type,
          title,
          body,
          machine_id: machineId,
          area_tag: areaTag,
          created_by: createdBy,
          tags,
          keep_local_until_reviewed: keepLocal,
        },
        deviceId
      );

      setFeedback({
        success: true,
        message: `Successfully written to local EdgeShard! Status: ${created.sync_status}. Queued in append-only write log.`,
      });

      // Reset form
      setTitle('');
      setBody('');
      if (onEntryCreated) onEntryCreated();
    } catch (err: any) {
      setFeedback({
        success: false,
        message: err.message || 'Failed to write local entry.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="industrial-card" style={{ padding: '1.5rem', border: '1px solid #2a3952' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.25rem',
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
              backgroundColor: 'rgba(255, 123, 0, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <PenTool size={18} color="#ff7b00" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff' }}>
              Author Knowledge Entry (Local Append-Only Log)
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Works completely offline. Automatically embedded and committed to local EdgeShard on device.
            </p>
          </div>
        </div>

        {/* Quick Demo Template Fillers */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Fill Demo Note:</span>
          <button
            type="button"
            onClick={() => loadTemplate('hydraulic_relief')}
            style={{
              backgroundColor: 'var(--bg-secondary)',
              color: '#38bdf8',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              padding: '0.25rem 0.65rem',
              borderRadius: '6px',
              fontSize: '0.72rem',
              cursor: 'pointer',
            }}
          >
            + Relief Valve Tip
          </button>
          <button
            type="button"
            onClick={() => loadTemplate('sensor_override')}
            style={{
              backgroundColor: 'var(--bg-secondary)',
              color: '#facc15',
              border: '1px solid rgba(234, 179, 8, 0.3)',
              padding: '0.25rem 0.65rem',
              borderRadius: '6px',
              fontSize: '0.72rem',
              cursor: 'pointer',
            }}
          >
            + Local Policy Draft
          </button>
        </div>
      </div>

      {feedback && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1.25rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: feedback.success ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: feedback.success ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(239, 68, 68, 0.4)',
            color: feedback.success ? '#34d399' : '#f87171',
            fontSize: '0.85rem',
          }}
        >
          {feedback.success ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <span>{feedback.message}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Row 1: Type, Machine, Area, Author */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '0.85rem',
          }}
        >
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Knowledge Type
            </label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as KnowledgeType)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            >
              <option value={KnowledgeType.TRIBAL_NOTE}>Tribal Knowledge Note (Field Tip)</option>
              <option value={KnowledgeType.INCIDENT_LOG}>Incident Log (Unplanned Stoppage)</option>
              <option value={KnowledgeType.SAFETY_PROCEDURE}>Safety / LOTO Procedure</option>
              <option value={KnowledgeType.MANUAL_SECTION}>OEM Technical Manual Section</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Target Machine
            </label>
            <select
              value={machineId}
              onChange={(e) => setMachineId(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                fontFamily: 'var(--font-mono)',
                outline: 'none',
              }}
            >
              <option value="PRESS-03">PRESS-03 (Line 3 Stamping)</option>
              <option value="CNC-01">CNC-01 (Mori Seiki 5-Axis)</option>
              <option value="CONV-04">CONV-04 (Packaging Bay)</option>
              <option value="GLOBAL">GLOBAL (Plant-Wide)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Area / Bay
            </label>
            <input
              type="text"
              value={areaTag}
              onChange={(e) => setAreaTag(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Authoring Technician
            </label>
            <input
              type="text"
              value={createdBy}
              onChange={(e) => setCreatedBy(e.target.value)}
              style={{
                width: '100%',
                backgroundColor: 'var(--bg-secondary)',
                color: '#fff',
                border: '1px solid var(--border-color)',
                padding: '0.55rem',
                borderRadius: '8px',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            />
          </div>
        </div>

        {/* Title */}
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            Procedure / Knowledge Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Line 3 Hydraulic Accumulator Pre-Charge Verification Trick"
            style={{
              width: '100%',
              backgroundColor: 'var(--bg-secondary)',
              color: '#fff',
              border: '1px solid var(--border-color)',
              padding: '0.65rem 0.85rem',
              borderRadius: '8px',
              fontSize: '0.9rem',
              outline: 'none',
            }}
          />
        </div>

        {/* Body */}
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            Detailed Observation & Technical Instructions
          </label>
          <textarea
            rows={4}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Provide step-by-step guidance, symptoms, valve identifiers, torque ratings, or workarounds..."
            style={{
              width: '100%',
              backgroundColor: 'var(--bg-secondary)',
              color: '#fff',
              border: '1px solid var(--border-color)',
              padding: '0.75rem',
              borderRadius: '8px',
              fontSize: '0.88rem',
              outline: 'none',
              fontFamily: 'inherit',
              lineHeight: '1.5',
            }}
          />
        </div>

        {/* Tags */}
        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            Telemetry Tags (comma separated)
          </label>
          <input
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            placeholder="e.g. hydraulic, viton-seal, manifold, pressure-drop"
            style={{
              width: '100%',
              backgroundColor: 'var(--bg-secondary)',
              color: '#fff',
              border: '1px solid var(--border-color)',
              padding: '0.55rem',
              borderRadius: '8px',
              fontSize: '0.82rem',
              fontFamily: 'var(--font-mono)',
              outline: 'none',
            }}
          />
        </div>

        {/* Deliberate Local Data Policy Checkbox */}
        <div
          style={{
            backgroundColor: keepLocal ? 'rgba(234, 179, 8, 0.1)' : 'rgba(255, 255, 255, 0.03)',
            border: keepLocal ? '1px solid rgba(234, 179, 8, 0.4)' : '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '0.85rem 1rem',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '0.75rem',
            transition: 'all 0.15s ease',
          }}
        >
          <input
            type="checkbox"
            id="keep-local-policy"
            checked={keepLocal}
            onChange={(e) => setKeepLocal(e.target.checked)}
            style={{ marginTop: '0.2rem', cursor: 'pointer', accentColor: '#facc15', transform: 'scale(1.2)' }}
          />
          <div>
            <label
              htmlFor="keep-local-policy"
              style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                color: keepLocal ? '#facc15' : 'var(--text-primary)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
              }}
            >
              <Lock size={14} />
              <span>Deliberate Local-Only Policy: "Keep local until reviewed"</span>
            </label>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              When enabled, this entry remains exclusively stored on this edge kiosk ({deviceId}) with status{' '}
              <strong style={{ color: '#facc15' }}>local_only</strong>. It will be deliberately omitted during cloud
              sync sessions until explicitly approved.
            </p>
          </div>
        </div>

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn-primary"
            style={{ padding: '0.75rem 1.75rem', fontSize: '0.92rem' }}
          >
            <PenTool size={16} />
            <span>
              {isSubmitting ? 'Embedding & Committing...' : 'Commit to Local EdgeShard'}
            </span>
          </button>
        </div>
      </form>
    </div>
  );
};
