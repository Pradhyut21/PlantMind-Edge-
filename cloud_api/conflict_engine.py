import json
import logging
import os
import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone

from qdrant_edge.models import (
    KnowledgeEntry,
    KnowledgeType,
    ConflictRecord,
    CompetingVersion,
)
from .config import cloud_settings

logger = logging.getLogger("cloud_api.conflict")

class ConflictEngine:
    """
    Intelligent Conflict Detection and Groq LLaMA Reasoning Engine.
    Detects concurrent diverging edits between edge nodes and central office.
    Strictly safeguards safety-critical procedures from silent last-write-wins overwriting.
    """

    def __init__(self):
        self.groq_client = None
        self._init_groq()

    def _init_groq(self):
        api_key = cloud_settings.groq_api_key or os.getenv("GROQ_API_KEY", "")
        if api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=api_key)
                logger.info("Groq LLaMA client initialized for conflict reasoning.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.groq_client = None

    def evaluate_conflict(
        self,
        existing: KnowledgeEntry,
        incoming: KnowledgeEntry,
    ) -> Tuple[bool, Optional[ConflictRecord], str]:
        """
        Check if an incoming update conflicts with existing central record.
        Returns: (is_conflict, conflict_record_or_none, resolution_strategy)
        """
        # Identical content is not a conflict
        if (
            existing.title == incoming.title
            and existing.body == incoming.body
            and existing.machine_id == incoming.machine_id
        ):
            return False, None, "identical_noop"

        # Check for version divergence or concurrent offline edits
        is_divergent = (
            incoming.version <= existing.version
            or incoming.device_id != existing.device_id
        )

        is_safety = incoming.type == KnowledgeType.SAFETY_PROCEDURE or existing.type == KnowledgeType.SAFETY_PROCEDURE

        if is_safety:
            # SAFETY CRITICAL: NEVER SILENTLY OVERWRITE. ALWAYS RAISE CONFLICT FOR HUMAN RECONCILIATION.
            conflict = self._create_conflict_record(existing, incoming)
            return True, conflict, "queued_for_human_review"

        if is_divergent:
            # Non-safety entry: Create an audit record and auto-resolve to newest
            incoming_time = incoming.updated_at or incoming.created_at
            existing_time = existing.updated_at or existing.created_at
            winner_strategy = "incoming_newer" if incoming_time >= existing_time else "existing_newer"
            conflict = self._create_conflict_record(existing, incoming, auto_resolved=True, strategy=winner_strategy)
            return False, conflict, winner_strategy

        return False, None, "clean_fast_forward"

    def _create_conflict_record(
        self,
        existing: KnowledgeEntry,
        incoming: KnowledgeEntry,
        auto_resolved: bool = False,
        strategy: str = "queued",
    ) -> ConflictRecord:
        """Create conflict record with side-by-side versions and AI reasoning summary."""
        v_existing = {
            "version": existing.version,
            "title": existing.title,
            "body": existing.body,
            "created_by": existing.created_by,
            "device_id": existing.device_id,
            "updated_at": existing.updated_at,
            "tags": existing.tags,
            "label": f"Version {existing.version} ({existing.device_id})",
        }
        v_incoming = {
            "version": incoming.version,
            "title": incoming.title,
            "body": incoming.body,
            "created_by": incoming.created_by,
            "device_id": incoming.device_id,
            "updated_at": incoming.updated_at,
            "tags": incoming.tags,
            "label": f"Version {incoming.version} ({incoming.device_id})",
        }

        ai_summary = self.generate_conflict_summary(existing, incoming)

        record = ConflictRecord(
            entry_id=existing.id,
            entity_title=incoming.title or existing.title,
            entity_type=incoming.type or existing.type,
            machine_id=incoming.machine_id or existing.machine_id,
            area_tag=incoming.area_tag or existing.area_tag,
            status="resolved" if auto_resolved else "open",
            competing_versions=[v_existing, v_incoming],
            resolution_type=strategy if auto_resolved else None,
            resolution_note=f"Auto-resolved to {strategy} (non-safety entry)" if auto_resolved else None,
            resolved_at=datetime.now(timezone.utc).isoformat() if auto_resolved else None,
            ai_summary=ai_summary,
        )
        return record

    def generate_conflict_summary(
        self,
        existing: KnowledgeEntry,
        incoming: KnowledgeEntry,
    ) -> str:
        """
        Use Groq LLaMA to generate a plain-language summary of what changed,
        safety implications, and suggested action for the knowledge manager.
        Falls back to rule-based industrial parameter diff if Groq is unavailable.
        """
        if self.groq_client:
            try:
                prompt = f"""You are PlantMind AI, an industrial safety and knowledge continuity reasoning engine for factory operations.
Analyze these two competing versions of a maintenance/safety procedure for {existing.machine_id} ({existing.area_tag}).
Both versions were edited offline by different technicians.

[VERSION A - Authored by {existing.created_by} on {existing.device_id}]:
Title: {existing.title}
Content:
{existing.body}
Tags: {', '.join(existing.tags)}

[VERSION B - Authored by {incoming.created_by} on {incoming.device_id}]:
Title: {incoming.title}
Content:
{incoming.body}
Tags: {', '.join(incoming.tags)}

Entity Type: {existing.type.value}

Provide a concise, crisp 3-part summary formatted in markdown:
1. **Critical Differences**: What exact steps, parameters, pressure/torque/temperature thresholds, or lockout sequences changed?
2. **Safety & Operational Risk**: What are the risks of choosing Version A vs Version B (e.g. overpressure, seal rupture, downtime, arc flash)?
3. **Recommended Action for Manager**: Specific guidance on which version to keep, whether to merge, or if these are distinct machine variants. Keep it highly practical for plant operations."""

                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an expert plant reliability engineer and safety director."},
                        {"role": "user", "content": prompt}
                    ],
                    model=cloud_settings.groq_model,
                    temperature=0.2,
                    max_tokens=500,
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Groq reasoning request failed, falling back to local reasoning: {e}")

        # Intelligent local fallback diff analyzer
        return self._local_diff_summary(existing, incoming)

    def _local_diff_summary(self, existing: KnowledgeEntry, incoming: KnowledgeEntry) -> str:
        """Heuristic industrial parameter and procedure diff analyzer."""
        diffs = []
        # Find numeric parameter changes (e.g., bar, psi, rpm, C, mm)
        num_patterns = r"(\b\d+(?:\.\d+)?\s*(?:bar|psi|rpm|°c|c|kpa|mpa|mm|nm|volts|v|amps|a)\b)"
        nums_a = set(re.findall(num_patterns, existing.body.lower()))
        nums_b = set(re.findall(num_patterns, incoming.body.lower()))

        param_diff = []
        for n in nums_b - nums_a:
            param_diff.append(f"Added threshold: `{n}`")
        for n in nums_a - nums_b:
            param_diff.append(f"Removed threshold: `{n}`")

        # Check safety keywords
        safety_words = ["lockout", "tagout", "loto", "depressurize", "bleed", "isolat", "glove", "ppe", "ground", "purge"]
        a_safety = [w for w in safety_words if w in existing.body.lower()]
        b_safety = [w for w in safety_words if w in incoming.body.lower()]
        missing_in_b = [w for w in a_safety if w not in b_safety]
        added_in_b = [w for w in b_safety if w not in a_safety]

        summary_lines = [
            f"**Critical Differences**:",
            f"- Author mismatch: `{existing.created_by}` ({existing.device_id}) vs `{incoming.created_by}` ({incoming.device_id}).",
        ]
        if param_diff:
            summary_lines.append(f"- Parameter variance: {', '.join(param_diff)}.")
        else:
            summary_lines.append(f"- Procedural text differs between Version {existing.version} and Version {incoming.version}.")

        if missing_in_b:
            summary_lines.append(f"- ⚠️ **Safety Step Omission**: Version B omitted safety protocols present in Version A ({', '.join(missing_in_b)}).")
        if added_in_b:
            summary_lines.append(f"- 🛡️ Version B introduced additional safety precautions ({', '.join(added_in_b)}).")

        summary_lines.append("\n**Safety & Operational Risk**:")
        if incoming.type == KnowledgeType.SAFETY_PROCEDURE:
            summary_lines.append(
                "- High risk: Discrepancy in lockout/depressurization steps on high-pressure equipment can lead to hydraulic injection, valve failure, or operator injury."
            )
        else:
            summary_lines.append(
                "- Moderate risk: Conflicting maintenance steps can result in incorrect torque or recurring downtime on Line 3."
            )

        summary_lines.append("\n**Recommended Action for Manager**:")
        if missing_in_b:
            summary_lines.append(
                f"- **Recommend Version A or Manual Merge**: Do not approve Version B directly as it omits safety lockout protocols. Verify if Version B's modified parameters apply to a newer valve revision."
            )
        else:
            summary_lines.append(
                f"- Inspect equipment sub-assembly tags. If this is a revised machine modification, merge both or annotate as separate machine sub-variants."
            )

        return "\n".join(summary_lines)
