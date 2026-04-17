"""
Compute Commons — Dual-Mode Store
In local dev (ENV != production): in-memory dict, resets on restart.
In production (ENV=production): delegates to Firestore via firestore_client.py.

All routers use this module directly — no code changes needed to switch modes.
"""
import os
from typing import Dict, List, Any

_ENV = os.getenv("ENV", "development")
_USE_FIRESTORE = _ENV == "production"

if _USE_FIRESTORE:
    from shared import firestore_client as _fs

# ── In-memory store (local dev / testing) ────────────────────────────────────

_store: Dict[str, Dict[str, Any]] = {
    "contributors": {},
    "contributions": {},
    "validations": {},
    "transactions": {},
    "governance_proposals": {},
    "governance_votes": {},
    "governance_disputes": {},
    "stakes": {},
    "taxonomy": {},
    "audit_log": {},
    "compliance_records": {},
    "trust_scores": {},
    "quarterly_stats": {},
    "leaderboard": {},
    "leaderboard_snapshots": {},
}


def col(name: str) -> Dict[str, Any]:
    return _store[name]


# ── Unified interface ─────────────────────────────────────────────────────────

def get(collection: str, doc_id: str) -> Any:
    if _USE_FIRESTORE:
        return _fs.get(collection, doc_id)
    return _store[collection].get(doc_id)


def put(collection: str, doc_id: str, data: Any) -> None:
    if _USE_FIRESTORE:
        _fs.put(collection, doc_id, data)
    else:
        _store[collection][doc_id] = data


def list_all(collection: str) -> List[Any]:
    if _USE_FIRESTORE:
        return _fs.list_all(collection)
    return list(_store[collection].values())


def delete(collection: str, doc_id: str) -> None:
    if _USE_FIRESTORE:
        _fs.delete(collection, doc_id)
    else:
        _store[collection].pop(doc_id, None)


def query(collection: str, field: str, value: Any) -> List[Any]:
    if _USE_FIRESTORE:
        return _fs.query(collection, field, value)
    return [v for v in _store[collection].values() if v.get(field) == value]


def query_multiple(collection: str, filters: Dict[str, Any]) -> List[Any]:
    results = list_all(collection)
    for field, value in filters.items():
        results = [r for r in results if r.get(field) == value]
    return results


def reset_all() -> None:
    """Only valid in local dev mode."""
    if not _USE_FIRESTORE:
        for k in _store:
            _store[k] = {}
