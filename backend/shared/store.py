"""
CATS — In-Memory Store (replaces Firestore emulator for simplicity)
All data lives here during process lifetime; seeder populates it at startup.
"""
from typing import Dict, List, Any
from datetime import datetime

# Collections
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
}


def col(name: str) -> Dict[str, Any]:
    return _store[name]


def get(collection: str, doc_id: str) -> Any:
    return _store[collection].get(doc_id)


def put(collection: str, doc_id: str, data: Any) -> None:
    _store[collection][doc_id] = data


def list_all(collection: str) -> List[Any]:
    return list(_store[collection].values())


def delete(collection: str, doc_id: str) -> None:
    _store[collection].pop(doc_id, None)


def query(collection: str, field: str, value: Any) -> List[Any]:
    return [v for v in _store[collection].values() if v.get(field) == value]


def query_multiple(collection: str, filters: Dict[str, Any]) -> List[Any]:
    results = list(_store[collection].values())
    for field, value in filters.items():
        results = [r for r in results if r.get(field) == value]
    return results


def reset_all() -> None:
    for k in _store:
        _store[k] = {}
