"""
Compute Commons — Firestore Client
Wraps google-cloud-firestore with the same get/put/list/query interface
as the in-memory store.py so existing routers require zero changes.

Set GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS in environment.
For local dev, set FIRESTORE_EMULATOR_HOST=localhost:8080 to use the emulator.
"""
import os
from typing import Any, Optional
from google.cloud import firestore

# ── Collections ──────────────────────────────────────────────────────────────
#
# contributors/{contributor_id}        — Contributor profile + balance
# contributions/{contribution_id}      — Individual submissions
# transactions/{transaction_id}        — Credit ledger entries
# validations/{validation_id}          — Peer validation records
# stakes/{stake_id}                    — Credit stakes
# governance_proposals/{proposal_id}   — Governance proposals
# governance_votes/{vote_id}           — Individual votes
# governance_disputes/{dispute_id}     — Disputes
# quarterly_stats/{quarter}            — e.g. "2024-Q2"
# leaderboard/top50                    — Denormalized top-50 snapshot

COLLECTION_MAP = {
    "contributors":          "contributors",
    "contributions":         "contributions",
    "transactions":          "transactions",
    "validations":           "validations",
    "stakes":                "stakes",
    "governance_proposals":  "governance_proposals",
    "governance_votes":      "governance_votes",
    "governance_disputes":   "governance_disputes",
    "quarterly_stats":       "quarterly_stats",
    "leaderboard":           "leaderboard_snapshots",
    "compliance":            "compliance_records",
}

_client: Optional[firestore.Client] = None


def get_client() -> firestore.Client:
    global _client
    if _client is None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        _client = firestore.Client(project=project)
    return _client


def _col(collection: str) -> firestore.CollectionReference:
    name = COLLECTION_MAP.get(collection, collection)
    return get_client().collection(name)


# ── Core interface (mirrors store.py) ─────────────────────────────────────────

def get(collection: str, doc_id: str) -> Optional[dict]:
    doc = _col(collection).document(doc_id).get()
    return doc.to_dict() if doc.exists else None


def put(collection: str, doc_id: str, data: dict) -> None:
    _col(collection).document(doc_id).set(data)


def delete(collection: str, doc_id: str) -> None:
    _col(collection).document(doc_id).delete()


def list_all(collection: str) -> list[dict]:
    return [d.to_dict() for d in _col(collection).stream()]


def query(collection: str, field: str, value: Any) -> list[dict]:
    docs = _col(collection).where(field, "==", value).stream()
    return [d.to_dict() for d in docs]


def query_ordered(
    collection: str,
    order_field: str,
    direction: str = "DESCENDING",
    limit: int = 50,
    filters: Optional[list[tuple]] = None,
) -> list[dict]:
    """
    Ordered + filtered query for leaderboard and webhook pulls.
    filters: list of (field, operator, value) tuples
    """
    ref = _col(collection)
    if filters:
        for field, op, value in filters:
            ref = ref.where(field, op, value)
    dir_ = firestore.Query.DESCENDING if direction == "DESCENDING" else firestore.Query.ASCENDING
    return [d.to_dict() for d in ref.order_by(order_field, direction=dir_).limit(limit).stream()]


# ── Leaderboard snapshot ──────────────────────────────────────────────────────

def update_leaderboard_snapshot() -> None:
    """
    Denormalize top-50 contributors by points into leaderboard/top50.
    Call this after every score award.
    """
    contributors = query_ordered(
        "contributors", order_field="points", direction="DESCENDING", limit=50
    )
    ranked = []
    for i, c in enumerate(contributors):
        ranked.append({
            "rank": i + 1,
            "contributor_id": c.get("id"),
            "handle": c.get("handle"),
            "tier": c.get("tier"),
            "progression_tier": c.get("progression_tier", "contributor"),
            "points": c.get("points", 0),
            "credits_balance": c.get("credits_balance", 0),
            "accuracy_score": c.get("accuracy_score", 0),
            "trust_score": c.get("trust_score", 0),
            "domains": c.get("domains", []),
            "acted_on_count": c.get("acted_on_count", 0),
        })
    get_client().collection("leaderboard_snapshots").document("top50").set({
        "updated_at": firestore.SERVER_TIMESTAMP,
        "contributors": ranked,
    })


def get_leaderboard_snapshot(
    tier: Optional[str] = None,
    domain: Optional[str] = None,
) -> list[dict]:
    """Read the denormalized leaderboard snapshot, with optional filters."""
    doc = get_client().collection("leaderboard_snapshots").document("top50").get()
    if not doc.exists:
        return []
    contributors = doc.to_dict().get("contributors", [])
    if tier:
        contributors = [c for c in contributors if c.get("tier") == tier]
    if domain:
        contributors = [c for c in contributors if domain in c.get("domains", [])]
    return contributors
