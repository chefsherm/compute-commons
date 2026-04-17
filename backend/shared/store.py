"""
CATS — Data Store (In-Memory + Firestore Hybrid)
Specific collections are mirrored/stored in Firestore.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
try:
    from shared.firestore_client import get_firestore_client
except ImportError:
    from firestore_client import get_firestore_client

# Firestore-backed collections
FIRESTORE_COLLECTIONS = ["contributors", "submissions", "leaderboard"]

# In-memory store (remains as fallback and for other collections)
_store: Dict[str, Dict[str, Any]] = {
    "contributors": {},
    "contributions": {},
    "submissions": {}, # New collection
    "leaderboard": {}, # New collection
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

db = get_firestore_client()

def col(name: str) -> Dict[str, Any]:
    return _store[name]

def get(collection: str, doc_id: str) -> Any:
    if db and collection in FIRESTORE_COLLECTIONS:
        doc = db.collection(collection).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
    return _store[collection].get(doc_id)

def put(collection: str, doc_id: str, data: Any) -> None:
    # Save FULL data to avoid loss, but ensure requested fields exist for external use
    fs_data = data.copy()
    if collection == "contributors":
        # Ensure (id, name, tier, points, domain, trust_score) are present
        if fs_data.get("name") is None and fs_data.get("handle"):
            fs_data["name"] = fs_data["handle"]
        if fs_data.get("domain") is None and fs_data.get("domains"):
            fs_data["domain"] = fs_data["domains"][0]
    elif collection == "submissions":
        # Ensure (id, contributor_id, status, model, timestamp) are present
        if fs_data.get("model") is None:
            fs_data["model"] = "generic-v1"
        if fs_data.get("timestamp") is None:
            fs_data["timestamp"] = fs_data.get("submitted_at") or fs_data.get("completed_at")

    # Always update in-memory store with potentially enhanced data
    _store[collection][doc_id] = fs_data

    if db and collection in FIRESTORE_COLLECTIONS:
        db.collection(collection).document(doc_id).set(fs_data)

def list_all(collection: str) -> List[Any]:
    if db and collection in FIRESTORE_COLLECTIONS:
        docs = db.collection(collection).stream()
        return [doc.to_dict() for doc in docs]
    return list(_store[collection].values())

def delete(collection: str, doc_id: str) -> None:
    if db and collection in FIRESTORE_COLLECTIONS:
        db.collection(collection).document(doc_id).delete()
    _store[collection].pop(doc_id, None)

def query(collection: str, field: str, value: Any) -> List[Any]:
    if db and collection in FIRESTORE_COLLECTIONS:
        docs = db.collection(collection).where(field, "==", value).stream()
        return [doc.to_dict() for doc in docs]
    return [v for v in _store[collection].values() if v.get(field) == value]

def query_multiple(collection: str, filters: Dict[str, Any]) -> List[Any]:
    if db and collection in FIRESTORE_COLLECTIONS:
        query_ref = db.collection(collection)
        for field, value in filters.items():
            query_ref = query_ref.where(field, "==", value)
        docs = query_ref.stream()
        return [doc.to_dict() for doc in docs]

    results = list(_store[collection].values())
    for field, value in filters.items():
        results = [r for r in results if r.get(field) == value]
    return results

def reset_all() -> None:
    for k in _store:
        _store[k] = {}
