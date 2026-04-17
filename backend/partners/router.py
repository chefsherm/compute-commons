"""
Compute Commons — Lab Partner API (Change 5)
Acted-on signal: lab partners mark high-value submissions, triggering contributor bonus + accuracy update.
Webhook pull endpoint: partners get new high-quality submissions without polling the UI.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
from shared import store

router = APIRouter()

ACTED_ON_BONUS_CREDITS = 50       # bonus points when a submission is acted on
ACTED_ON_ACCURACY_BOOST = 0.01    # acted-on submissions boost accuracy by 1%
WEBHOOK_PAGE_SIZE = 20


class ActedOnRequest(BaseModel):
    lab_partner_id: str
    note: Optional[str] = None  # optional note from lab (e.g. "used in Claude 3.6 training run")


@router.post("/acted-on/{contribution_id}")
def mark_acted_on(contribution_id: str, req: ActedOnRequest):
    """
    Lab partner marks a contribution as acted on.
    - Sets acted_on=True on the contribution
    - Issues +50 bonus compute credits to the contributor
    - Updates contributor accuracy score
    - Creates an 'acted_on' transaction entry
    - Updates contributor acted_on_count
    """
    c = store.get("contributions", contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")
    if c.get("status") != "complete":
        raise HTTPException(400, "Only completed contributions can be marked as acted on")
    if c.get("acted_on"):
        raise HTTPException(409, "Contribution already marked as acted on")

    contributor_id = c["contributor_id"]
    contributor = store.get("contributors", contributor_id)
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    # Mark the contribution
    c["acted_on"] = True
    c["acted_on_at"] = datetime.utcnow().isoformat() + "Z"
    c["acted_on_by"] = req.lab_partner_id
    c["acted_on_note"] = req.note
    store.put("contributions", contribution_id, c)

    # Bonus credits
    bonus_points = ACTED_ON_BONUS_CREDITS
    bonus_credit = round(bonus_points * 0.01, 2)  # same EXCHANGE_RATE_PER_POINT
    contributor["points"] = contributor.get("points", 0) + bonus_points
    contributor["credits_balance"] = round(contributor.get("credits_balance", 0) + bonus_credit, 2)

    # Accuracy boost (capped at 1.0)
    contributor["accuracy_score"] = min(
        1.0,
        round(contributor.get("accuracy_score", 0.0) + ACTED_ON_ACCURACY_BOOST, 4)
    )

    # acted_on counter
    contributor["acted_on_count"] = contributor.get("acted_on_count", 0) + 1

    store.put("contributors", contributor_id, contributor)

    # Transaction record
    txn_id = f"txn_{uuid.uuid4().hex[:8]}"
    txn = {
        "id": txn_id,
        "contributor_id": contributor_id,
        "type": "acted_on",
        "amount": bonus_credit,
        "points": bonus_points,
        "contribution_id": contribution_id,
        "description": f"Lab partner acted on submission — {req.note or 'no note provided'}",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    store.put("transactions", txn_id, txn)

    return {
        "contribution_id": contribution_id,
        "acted_on": True,
        "contributor_id": contributor_id,
        "bonus_credits_issued": bonus_credit,
        "bonus_points": bonus_points,
        "new_accuracy_score": contributor["accuracy_score"],
        "transaction_id": txn_id,
        "message": f"Contributor '{contributor['handle']}' notified — +{bonus_points} pts credited.",
    }


@router.get("/webhook/submissions")
def webhook_pull_submissions(
    since: Optional[str] = Query(None, description="ISO timestamp — only return submissions after this time"),
    limit: int = Query(WEBHOOK_PAGE_SIZE, le=100),
    page: int = Query(1, ge=1),
):
    """
    Lab partners pull new high-quality submissions without polling the UI.
    Returns complete, high-signal, not-yet-acted-on contributions.
    Supports since= for incremental pulls and pagination.
    """
    all_contribs = store.list_all("contributions")

    # Filter: complete + not yet acted on
    eligible = [
        c for c in all_contribs
        if c.get("status") == "complete" and not c.get("acted_on", False)
    ]

    # Filter by since timestamp if provided
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", ""))
            eligible = [
                c for c in eligible
                if datetime.fromisoformat(
                    (c.get("completed_at") or c["submitted_at"]).replace("Z", "")
                ) > since_dt
            ]
        except ValueError:
            raise HTTPException(400, "Invalid 'since' timestamp format. Use ISO 8601.")

    # Sort by recency
    eligible.sort(
        key=lambda x: x.get("completed_at") or x["submitted_at"],
        reverse=True
    )

    total = len(eligible)
    offset = (page - 1) * limit
    page_items = eligible[offset:offset + limit]

    # Compute next_since from the oldest item in this page
    next_since = None
    if page_items:
        oldest = page_items[-1]
        next_since = oldest.get("completed_at") or oldest["submitted_at"]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "contributions": page_items,
        "next_since": next_since,
        "usage_note": (
            "Use next_since as the 'since' param on your next pull to get only new submissions. "
            "POST /partners/acted-on/{id} to mark a submission as acted on."
        ),
    }


@router.get("/webhook/acted-on")
def webhook_pull_acted_on(since: Optional[str] = Query(None)):
    """
    Pull all contributions that have been marked as acted on (for lab-side record keeping).
    """
    all_contribs = store.list_all("contributions")
    acted = [c for c in all_contribs if c.get("acted_on")]

    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", ""))
            acted = [
                c for c in acted
                if datetime.fromisoformat(
                    (c.get("acted_on_at") or c["submitted_at"]).replace("Z", "")
                ) > since_dt
            ]
        except ValueError:
            raise HTTPException(400, "Invalid 'since' timestamp format.")

    acted.sort(key=lambda x: x.get("acted_on_at") or x["submitted_at"], reverse=True)
    return {"total": len(acted), "contributions": acted}
