"""
Data Steward Queue & Governance Audit Logger
=============================================
Manages flagged medium-confidence HCP record pairs for manual review by data stewards,
enforces decision governance (Approve Merge, Reject Separate, Defer), and maintains
an immutable audit log.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from hcp_identity_resolution import MatchResult, ActionTier


class StewardDecision(Enum):
    PENDING = "PENDING"
    APPROVED_MERGE = "APPROVED_MERGE"
    REJECTED_SEPARATE = "REJECTED_SEPARATE"
    DEFERRED = "DEFERRED"


@dataclass
class QueueItem:
    """Represents an item in the Data Steward verification queue."""
    queue_id: str
    match_result: MatchResult
    status: StewardDecision = StewardDecision.PENDING
    assigned_steward: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved_at: Optional[str] = None


class DataStewardQueueManager:
    """Manages the verification queue and records stewardship audit trails."""

    def __init__(self):
        self.queue: Dict[str, QueueItem] = {}
        self.audit_log: List[Dict] = []
        self._item_counter = 1

    def enqueue_if_needed(self, match_result: MatchResult) -> Optional[QueueItem]:
        """Enqueues candidate pair if recommended action is MANUAL_REVIEW."""
        if match_result.recommended_action == ActionTier.MANUAL_REVIEW:
            queue_id = f"STWD-{self._item_counter:04d}"
            self._item_counter += 1

            item = QueueItem(
                queue_id=queue_id,
                match_result=match_result,
                status=StewardDecision.PENDING
            )
            self.queue[queue_id] = item
            self._log_audit_event("ENQUEUED", queue_id, match_result.candidate_a_id, match_result.candidate_b_id, match_result.explanation)
            return item
        return None

    def process_decision(self, queue_id: str, steward_id: str, decision: StewardDecision, reason: str) -> QueueItem:
        """Processes a data steward's decision on a queued pair."""
        if queue_id not in self.queue:
            raise KeyError(f"Queue item {queue_id} not found.")

        item = self.queue[queue_id]
        item.status = decision
        item.assigned_steward = steward_id
        item.decision_reason = reason
        item.resolved_at = datetime.utcnow().isoformat()

        self._log_audit_event(
            event_type=decision.value,
            queue_id=queue_id,
            candidate_a=item.match_result.candidate_a_id,
            candidate_b=item.match_result.candidate_b_id,
            details=f"Steward {steward_id} decided {decision.value}: {reason}"
        )
        return item

    def get_pending_items(self) -> List[QueueItem]:
        """Returns all items pending data steward review."""
        return [item for item in self.queue.values() if item.status == StewardDecision.PENDING]

    def _log_audit_event(self, event_type: str, queue_id: str, candidate_a: str, candidate_b: str, details: str):
        """Appends an event to the immutable governance audit log."""
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "queue_id": queue_id,
            "candidate_a": candidate_a,
            "candidate_b": candidate_b,
            "details": details
        })
