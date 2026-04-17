"""
CATS — Trust Score Service Router (Phase 2)
GET /trust/score/{contributor_id} — full breakdown
GET /trust/scores — all contributors' trust scores
POST /trust/fraud-check/{contributor_id} — run fraud detection checks
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from shared import store
from shared.config import (
    SIMILARITY_FLAG_THRESHOLD, VELOCITY_LIMIT_PER_DAY,
    COLLUSION_MUTUAL_VALIDATION_LIMIT, BOT_DETECTION_SECONDS
)

router = APIRouter()


@router.get("/score/{contributor_id}")
def get_trust_score(contributor_id: str):
    contributor = store.get("contributors", contributor_id)
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    breakdown = store.get("trust_scores", contributor_id)
    if not breakdown:
        raise HTTPException(404, "Trust score not yet computed for this contributor")

    trust_score = breakdown["total"]

    # Access restrictions based on trust score
    restrictions = []
    if trust_score < 40:
        restrictions.append("redemption_cap: max $200/month")
    if trust_score < 30:
        restrictions.append("governance_voting: suspended")
    if trust_score >= 70:
        restrictions.append("validator_priority: assigned high-value contributions first")

    return {
        "contributor_id": contributor_id,
        "handle": contributor["handle"],
        "tier": contributor["tier"],
        "trust_score": trust_score,
        "breakdown": breakdown,
        "active_restrictions": restrictions,
        "computed_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/scores")
def list_trust_scores(min_score: Optional[float] = None, max_score: Optional[float] = None):
    scores = store.list_all("trust_scores")
    if min_score is not None:
        scores = [s for s in scores if s.get("total", 0) >= min_score]
    if max_score is not None:
        scores = [s for s in scores if s.get("total", 0) <= max_score]
    scores.sort(key=lambda x: x.get("total", 0), reverse=True)

    result = []
    for s in scores:
        c = store.get("contributors", s["contributor_id"])
        result.append({
            "contributor_id": s["contributor_id"],
            "handle": c["handle"] if c else "unknown",
            "tier": c["tier"] if c else "unknown",
            "trust_score": s.get("total", 0),
            "breakdown": s,
        })
    return result


@router.post("/fraud-check/{contributor_id}")
def run_fraud_checks(contributor_id: str):
    """
    Runs all fraud detection checks against a contributor.
    Returns flags and recommended actions.
    """
    contributor = store.get("contributors", contributor_id)
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    flags = []
    actions = []
    all_contribs = store.query("contributions", "contributor_id", contributor_id)

    # 1. Velocity check
    recent_24h = [
        c for c in all_contribs
        if datetime.fromisoformat(c["submitted_at"].replace("Z", "")) > datetime.utcnow() - timedelta(hours=24)
    ]
    if len(recent_24h) > VELOCITY_LIMIT_PER_DAY:
        flags.append({
            "type": "velocity_exceeded",
            "detail": f"{len(recent_24h)} submissions in last 24h (limit: {VELOCITY_LIMIT_PER_DAY})",
            "severity": "high"
        })
        actions.append("auto_hold_new_submissions")

    # 2. Bot detection (account age < 90s)
    created = datetime.fromisoformat(contributor["created_at"].replace("Z", ""))
    age_seconds = (datetime.utcnow() - created).total_seconds()
    earliest_sub = min((c["submitted_at"] for c in all_contribs), default=None)
    if earliest_sub:
        earliest_dt = datetime.fromisoformat(earliest_sub.replace("Z", ""))
        sub_age_seconds = (earliest_dt - created).total_seconds()
        if sub_age_seconds < BOT_DETECTION_SECONDS:
            flags.append({
                "type": "bot_detection",
                "detail": f"First submission {sub_age_seconds:.0f}s after account creation",
                "severity": "critical"
            })
            actions.append("auto_reject_submission")

    # 3. Text similarity check (simplified — check if contributor has similarity flags)
    similarity_flagged = [c for c in all_contribs if "high_similarity_detected" in c.get("abuse_flags", [])]
    if similarity_flagged:
        flags.append({
            "type": "high_text_similarity",
            "detail": f"{len(similarity_flagged)} submissions flagged for cosine similarity > {SIMILARITY_FLAG_THRESHOLD}",
            "severity": "medium"
        })
        actions.append("flag_for_manual_review")

    # 4. Collusion detection
    # Check if this contributor has been validated by the same validators > 3 times in 30 days
    validations_on_contrib = [
        v for v in store.list_all("validations")
        if v["contribution_id"] in [c["id"] for c in all_contribs]
        and datetime.fromisoformat(v["created_at"].replace("Z", "")) > datetime.utcnow() - timedelta(days=30)
    ]
    validator_counts: dict = {}
    for v in validations_on_contrib:
        vid = v["validator_id"]
        validator_counts[vid] = validator_counts.get(vid, 0) + 1

    collusion_suspects = {k: v for k, v in validator_counts.items() if v > COLLUSION_MUTUAL_VALIDATION_LIMIT}
    if collusion_suspects:
        flags.append({
            "type": "collusion_risk",
            "detail": f"Validator(s) {list(collusion_suspects.keys())} validated this contributor's work > 3 times in 30 days",
            "severity": "high"
        })
        actions.append("escalate_to_governance")

    # 5. Check existing compliance flags
    existing_flags = contributor.get("compliance_flags", [])
    if existing_flags:
        flags.append({
            "type": "existing_compliance_flags",
            "detail": existing_flags,
            "severity": "medium"
        })

    is_clean = len(flags) == 0
    return {
        "contributor_id": contributor_id,
        "handle": contributor["handle"],
        "is_clean": is_clean,
        "flags": flags,
        "recommended_actions": list(set(actions)),
        "check_timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/leaderboard")
def trust_leaderboard(limit: int = 25):
    scores = store.list_all("trust_scores")
    scores.sort(key=lambda x: x.get("total", 0), reverse=True)
    result = []
    for s in scores[:limit]:
        c = store.get("contributors", s["contributor_id"])
        result.append({
            "rank": len(result) + 1,
            "contributor_id": s["contributor_id"],
            "handle": c["handle"] if c else "unknown",
            "tier": c["tier"] if c else "unknown",
            "trust_score": s.get("total", 0),
        })
    return result
