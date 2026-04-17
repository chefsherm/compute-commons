"""
Compute Commons — Async Firestore Database Layer
Replaces the in-memory store.py with a fully persistent, async-first
Google Cloud Firestore implementation.

Authentication (local dev):
    Set GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json in .env
    OR run `gcloud auth application-default login` for ADC.

Authentication (Cloud Run):
    Attach a service account with roles/datastore.user to the Cloud Run
    service. The client auto-discovers credentials via the metadata server.

Usage in a FastAPI route:
    from shared.database import get_db, FirestoreDB

    @router.get("/contributors/{id}")
    async def get_contributor(id: str, db: FirestoreDB = Depends(get_db)):
        doc = await db.get("contributors", id)
        if not doc:
            raise HTTPException(404, "Not found")
        return doc
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from google.cloud import firestore
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1 import async_transaction

log = logging.getLogger(__name__)

# ── Collection name registry ──────────────────────────────────────────────────
# Single source of truth — change a name here and it propagates everywhere.

COLLECTIONS = {
    "contributors":         "contributors",
    "contributions":        "contributions",
    "transactions":         "transactions",
    "validations":          "validations",
    "stakes":               "stakes",
    "governance_proposals": "governance_proposals",
    "governance_votes":     "governance_votes",
    "governance_disputes":  "governance_disputes",
    "leaderboard":          "leaderboard_snapshots",
    "quarterly_stats":      "quarterly_stats",
    "compliance_records":   "compliance_records",
}

LEADERBOARD_DOC = "top50"


# ── Timestamp helpers ─────────────────────────────────────────────────────────

def _to_firestore_value(v: Any) -> Any:
    """
    Convert Python/Pydantic values to Firestore-safe types.
    - ISO 8601 strings that look like datetimes → datetime objects (Firestore Timestamps)
    - Everything else passes through.
    """
    if isinstance(v, str) and len(v) >= 19:
        # Try parsing common ISO patterns: "2024-01-15T12:30:00Z" or "2024-01-15T12:30:00"
        for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                dt = datetime.strptime(v, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    if isinstance(v, dict):
        return {k: _to_firestore_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_to_firestore_value(i) for i in v]
    return v


def _from_firestore_value(v: Any) -> Any:
    """
    Convert Firestore types back to JSON-serialisable Python types.
    - Firestore Timestamps (datetime with tzinfo) → ISO 8601 string with "Z"
    - Nested dicts/lists handled recursively.
    """
    if isinstance(v, datetime):
        return v.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(v, dict):
        return {k: _from_firestore_value(val) for k, val in v.items()}
    if isinstance(v, list):
        return [_from_firestore_value(i) for i in v]
    return v


def _serialize(data: dict) -> dict:
    """Pydantic dict → Firestore-safe dict (convert ISO strings to Timestamps)."""
    return {k: _to_firestore_value(v) for k, v in data.items()}


def _deserialize(doc_id: str, data: dict) -> dict:
    """
    Firestore dict → application dict.
    - Injects Firestore document ID as the `id` field.
    - Converts all Timestamps back to ISO strings.
    """
    result = {k: _from_firestore_value(v) for k, v in data.items()}
    result["id"] = doc_id          # always surface the document ID as `id`
    return result


# ── Core database class ───────────────────────────────────────────────────────

class FirestoreDB:
    """
    Async Firestore client wrapper.

    A single instance is created at startup and injected into routes via
    FastAPI's Depends(get_db). All public methods are async and safe to
    await inside async route handlers — they never block the event loop.
    """

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _col(self, collection: str) -> firestore.AsyncCollectionReference:
        name = COLLECTIONS.get(collection, collection)
        return self._client.collection(name)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    async def get(self, collection: str, doc_id: str) -> Optional[dict]:
        """Fetch a single document by ID. Returns None if not found."""
        snap = await self._col(collection).document(doc_id).get()
        if not snap.exists:
            return None
        return _deserialize(snap.id, snap.to_dict())

    async def put(self, collection: str, doc_id: str, data: dict) -> None:
        """
        Create or fully overwrite a document.
        `data` may be a raw dict or a Pydantic model's .model_dump() output.
        The `id` field in `data` is intentionally NOT written to Firestore
        (it lives as the document ID, not a field), but IS re-injected on read.
        """
        payload = {k: v for k, v in data.items() if k != "id"}
        await self._col(collection).document(doc_id).set(_serialize(payload))

    async def patch(self, collection: str, doc_id: str, updates: dict) -> None:
        """Partial update (merge) — only the provided fields are written."""
        payload = {k: v for k, v in updates.items() if k != "id"}
        await self._col(collection).document(doc_id).update(_serialize(payload))

    async def delete(self, collection: str, doc_id: str) -> None:
        await self._col(collection).document(doc_id).delete()

    # ── Querying ──────────────────────────────────────────────────────────────

    async def list_all(self, collection: str) -> list[dict]:
        """Return every document in a collection. Use with care on large sets."""
        docs = self._col(collection).stream()
        return [_deserialize(d.id, d.to_dict()) async for d in docs]

    async def query(
        self,
        collection: str,
        field: str,
        value: Any,
        order_by: Optional[str] = None,
        direction: str = "DESCENDING",
        limit: Optional[int] = None,
    ) -> list[dict]:
        """
        Filter by a single field equality. Optionally order and paginate.

        Example:
            txns = await db.query(
                "transactions", "contributor_id", uid,
                order_by="created_at", direction="DESCENDING", limit=20
            )
        """
        ref = self._col(collection).where(
            filter=FieldFilter(field, "==", value)
        )
        if order_by:
            dir_ = (
                firestore.Query.DESCENDING
                if direction == "DESCENDING"
                else firestore.Query.ASCENDING
            )
            ref = ref.order_by(order_by, direction=dir_)
        if limit:
            ref = ref.limit(limit)

        return [_deserialize(d.id, d.to_dict()) async for d in ref.stream()]

    async def query_multiple(
        self,
        collection: str,
        filters: list[tuple[str, str, Any]],
        order_by: Optional[str] = None,
        direction: str = "DESCENDING",
        limit: Optional[int] = None,
    ) -> list[dict]:
        """
        Multi-field query using Firestore composite filters.

        filters: list of (field, operator, value) tuples
            Operators: "==", "<", "<=", ">", ">=", "!="

        Note: Firestore requires a composite index for multi-field queries.
        Create them at: console.cloud.google.com/firestore/indexes

        Example:
            results = await db.query_multiple(
                "contributions",
                [("contributor_id", "==", uid), ("status", "==", "complete")],
                order_by="submitted_at",
                limit=50,
            )
        """
        ref = self._col(collection)
        for field, op, value in filters:
            ref = ref.where(filter=FieldFilter(field, op, value))
        if order_by:
            dir_ = (
                firestore.Query.DESCENDING
                if direction == "DESCENDING"
                else firestore.Query.ASCENDING
            )
            ref = ref.order_by(order_by, direction=dir_)
        if limit:
            ref = ref.limit(limit)

        return [_deserialize(d.id, d.to_dict()) async for d in ref.stream()]

    async def paginate(
        self,
        collection: str,
        order_by: str,
        direction: str = "DESCENDING",
        page_size: int = 20,
        start_after_value: Optional[Any] = None,
    ) -> dict:
        """
        Cursor-based pagination.

        Returns: {"items": [...], "next_cursor": <value or None>}

        Pass the returned `next_cursor` as `start_after_value` on the next call.

        Example — lab partner webhook pull:
            page1 = await db.paginate("contributions", "submitted_at", page_size=20)
            page2 = await db.paginate(
                "contributions", "submitted_at",
                start_after_value=page1["next_cursor"]
            )
        """
        dir_ = (
            firestore.Query.DESCENDING
            if direction == "DESCENDING"
            else firestore.Query.ASCENDING
        )
        ref = self._col(collection).order_by(order_by, direction=dir_)
        if start_after_value is not None:
            fs_value = _to_firestore_value(str(start_after_value))
            ref = ref.start_after({order_by: fs_value})
        # Fetch one extra to know if there's a next page
        ref = ref.limit(page_size + 1)
        docs = [_deserialize(d.id, d.to_dict()) async for d in ref.stream()]

        has_next = len(docs) > page_size
        items = docs[:page_size]
        next_cursor = items[-1].get(order_by) if has_next and items else None

        return {"items": items, "next_cursor": next_cursor}

    # ── Leaderboard (atomic) ──────────────────────────────────────────────────

    async def update_leaderboard_snapshot(self) -> None:
        """
        Atomically rewrite the leaderboard/top50 document.

        Uses a Firestore transaction so that:
        1. The top-50 read and write happen in a single atomic operation.
        2. Concurrent score updates don't cause stale snapshots.

        Called from the scoring router after every score award.
        """
        lb_ref = (
            self._client
            .collection(COLLECTIONS["leaderboard"])
            .document(LEADERBOARD_DOC)
        )

        @async_transaction.async_transactional
        async def _run(transaction: firestore.AsyncTransaction) -> None:
            # Read top 50 contributors ordered by points
            contributors_ref = (
                self._client
                .collection(COLLECTIONS["contributors"])
                .order_by("points", direction=firestore.Query.DESCENDING)
                .limit(50)
            )
            ranked = []
            async for i, snap in _aenumerate(contributors_ref.stream()):
                c = snap.to_dict()
                ranked.append({
                    "rank": i + 1,
                    "contributor_id": snap.id,
                    "handle": c.get("handle", ""),
                    "tier": c.get("tier", "contributor"),
                    "progression_tier": c.get("progression_tier", "contributor"),
                    "points": c.get("points", 0),
                    "credits_balance": c.get("credits_balance", 0.0),
                    "accuracy_score": c.get("accuracy_score", 0.0),
                    "trust_score": c.get("trust_score", 0.0),
                    "domains": c.get("domains", []),
                    "acted_on_count": c.get("acted_on_count", 0),
                })
            transaction.set(lb_ref, {
                "updated_at": firestore.SERVER_TIMESTAMP,
                "contributors": ranked,
            })

        txn = self._client.transaction()
        await _run(txn)

    async def get_leaderboard(
        self,
        tier: Optional[str] = None,
        domain: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Read the denormalized leaderboard snapshot with optional filters.
        Fast — single document read regardless of contributor count.
        """
        snap = await (
            self._client
            .collection(COLLECTIONS["leaderboard"])
            .document(LEADERBOARD_DOC)
            .get()
        )
        if not snap.exists:
            return []

        contributors = _from_firestore_value(
            snap.to_dict().get("contributors", [])
        )
        if tier:
            contributors = [c for c in contributors if c.get("tier") == tier]
        if domain:
            contributors = [c for c in contributors if domain in c.get("domains", [])]
        return contributors[:limit]

    # ── Batch operations ──────────────────────────────────────────────────────

    async def batch_put(self, collection: str, items: list[dict]) -> None:
        """
        Write up to 500 documents in a single Firestore batch commit.
        Used by the migration script and seeder.
        Splits automatically if len(items) > 500.
        """
        BATCH_LIMIT = 500
        for chunk_start in range(0, len(items), BATCH_LIMIT):
            chunk = items[chunk_start:chunk_start + BATCH_LIMIT]
            batch = self._client.batch()
            for item in chunk:
                doc_id = item.get("id") or item.get("contributor_id", "unknown")
                payload = {k: v for k, v in item.items() if k != "id"}
                ref = self._col(collection).document(doc_id)
                batch.set(ref, _serialize(payload))
            await batch.commit()
            log.info("batch_put: wrote %d docs to '%s'", len(chunk), collection)


# ── Async enumerate helper (no built-in for async generators) ─────────────────

async def _aenumerate(aiter, start: int = 0):
    i = start
    async for item in aiter:
        yield i, item
        i += 1


# ── Singleton + FastAPI dependency ────────────────────────────────────────────

_db_instance: Optional[FirestoreDB] = None


def init_db() -> FirestoreDB:
    """
    Call once at application startup (in main.py @app.on_event("startup")).
    Reads GOOGLE_CLOUD_PROJECT from the environment.
    Credentials are resolved via Application Default Credentials (ADC):
      - Local dev: GOOGLE_APPLICATION_CREDENTIALS env var pointing to a
        service account JSON, or `gcloud auth application-default login`.
      - Cloud Run: the attached service account is used automatically.
    """
    global _db_instance
    if _db_instance is None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project:
            raise RuntimeError(
                "GOOGLE_CLOUD_PROJECT environment variable is not set. "
                "Add it to your .env file."
            )
        client = AsyncClient(project=project)
        _db_instance = FirestoreDB(client)
        log.info("Firestore AsyncClient initialized for project '%s'", project)
    return _db_instance


async def get_db() -> FirestoreDB:
    """
    FastAPI dependency. Inject into route handlers with Depends(get_db).

    Example:
        @router.get("/contributors/{contributor_id}")
        async def get_contributor(
            contributor_id: str,
            db: FirestoreDB = Depends(get_db)
        ):
            doc = await db.get("contributors", contributor_id)
            if not doc:
                raise HTTPException(status_code=404, detail="Contributor not found")
            return doc
    """
    if _db_instance is None:
        raise RuntimeError("Database not initialized. Call init_db() at startup.")
    return _db_instance
