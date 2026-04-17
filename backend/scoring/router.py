"""
CATS — Scoring Engine Router (Phase 1 + Phase 2)
Handles: score calculation, award, leaderboard, exchange rate, inflation guard
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from shared import store
from shared.config import (
    EXCHANGE_RATE_PER_POINT, HELPFULNESS_MULTIPLIER_CEILING_DEFAULT,
    HELPFULNESS_MULTIPLIER_CEILING_INFLATION, QUARTERLY_ISSUANCE_CEILING_MULTIPLIER,
    TRUST_REPUTATION_HIGH_THRESHOLD, TRUST_REPUTATION_LOW_THRESHOLD,
    TRUST_BONUS_HIGH, TRUST_PENALTY_LOW
)

router = APIRouter()

TIER_MULTIPLIERS = {"contributor": 1.0, "validator": 1.2, "expert": 1.5, "partner": 2.0}

LOW_SIGNAL_HELPFULNESS_THRESHOLD = 1.2   # below this = low-signal validated contribution
SIGNAL_QUALITY_DECAY_PER_CONSECUTIVE = 0.15  # each consecutive low-signal reduces modifier
SIGNAL_QUALITY_FLOOR = 0.2              # never below 20% of base rate
SIGNAL_QUALITY_LOOKBACK = 10            # inspect last N validated contributions

# Generic-submission classifier heuristics (no ML model needed for prototype)
GENERIC_PHRASES = [
    "the model was wrong", "it got it wrong", "wrong answer", "incorrect",
    "this is wrong", "bad response", "not good", "could be better",
    "the response was poor", "i disagree", "this is incorrect",
]


def get_signal_quality_modifier(contributor_id: str) -> float:
    """
    Inspects last N validated contributions from this contributor.
    First submission always returns 1.0.
    Each consecutive low-signal submission (helpfulness < threshold) reduces
    the modifier by SIGNAL_QUALITY_DECAY_PER_CONSECUTIVE, floored at SIGNAL_QUALITY_FLOOR.
    """
    all_contribs = store.query("contributions", "contributor_id", contributor_id)
    validated = [
        c for c in all_contribs
        if c["status"] == "complete" and c.get("helpfulness_multiplier") is not None
    ]
    # First submission — always full rate
    if len(validated) == 0:
        return 1.0

    # Count consecutive low-signal from most recent backward
    validated.sort(key=lambda x: x.get("completed_at") or x["submitted_at"], reverse=True)
    recent = validated[:SIGNAL_QUALITY_LOOKBACK]
    consecutive_low = 0
    for c in recent:
        if (c.get("helpfulness_multiplier") or 0) < LOW_SIGNAL_HELPFULNESS_THRESHOLD:
            consecutive_low += 1
        else:
            break  # stop at first non-low signal

    if consecutive_low == 0:
        return 1.0
    modifier = 1.0 - (consecutive_low * SIGNAL_QUALITY_DECAY_PER_CONSECUTIVE)
    return max(modifier, SIGNAL_QUALITY_FLOOR)


def get_inflation_guard_status() -> tuple[bool, float]:
    """Returns (inflation_active, current_ceiling)."""
    q2 = store.get("quarterly_stats", "2024-Q2") or {}
    q1 = store.get("quarterly_stats", "2024-Q1") or {}
    current = q2.get("total_credits_issued", 0)
    prior = q1.get("total_credits_issued", 1)
    if current > prior * QUARTERLY_ISSUANCE_CEILING_MULTIPLIER:
        return True, HELPFULNESS_MULTIPLIER_CEILING_INFLATION
    return False, HELPFULNESS_MULTIPLIER_CEILING_DEFAULT


class ScoreRequest(BaseModel):
    contribution_id: str
    proposed_helpfulness_multiplier: Optional[float] = None


class AwardRequest(BaseModel):
    contribution_id: str
    validator_ids: list[str]
    helpfulness_multiplier: float


@router.post("/score/calculate")
def calculate_score(req: ScoreRequest):
    c = store.get("contributions", req.contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")

    contributor = store.get("contributors", c["contributor_id"])
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    inflation_active, ceiling = get_inflation_guard_status()
    hlp = min(req.proposed_helpfulness_multiplier or c.get("helpfulness_multiplier") or 1.5, ceiling)

    # red_team_report has a floor of 2.0 (or ceiling if lower)
    if c["type"] == "red_team_report":
        hlp = min(ceiling, 2.0)

    base = c.get("base_score") or 150
    tier_mult = TIER_MULTIPLIERS[contributor["tier"]]
    rep_mod = contributor["reputation_modifier"]
    signal_mod = get_signal_quality_modifier(c["contributor_id"])
    final = round(base * hlp * tier_mult * rep_mod * signal_mod, 1)

    return {
        "contribution_id": req.contribution_id,
        "base_score": base,
        "helpfulness_multiplier": hlp,
        "tier_multiplier": tier_mult,
        "reputation_modifier": rep_mod,
        "signal_quality_modifier": signal_mod,
        "final_score": final,
        "credit_equivalent": round(final * EXCHANGE_RATE_PER_POINT, 2),
        "inflation_guard_active": inflation_active,
        "helpfulness_ceiling": ceiling,
    }


@router.post("/score/award")
def award_score(req: AwardRequest):
    c = store.get("contributions", req.contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")

    contributor = store.get("contributors", c["contributor_id"])
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    inflation_active, ceiling = get_inflation_guard_status()
    hlp = min(req.helpfulness_multiplier, ceiling)

    if c["type"] == "red_team_report":
        hlp = min(ceiling, 2.0)

    base = c.get("base_score") or 150
    tier_mult = TIER_MULTIPLIERS[contributor["tier"]]
    rep_mod = contributor["reputation_modifier"]
    signal_mod = get_signal_quality_modifier(c["contributor_id"])
    final = round(base * hlp * tier_mult * rep_mod * signal_mod, 1)
    credit_eq = round(final * EXCHANGE_RATE_PER_POINT, 2)

    # Update contribution
    c["status"] = "complete"
    c["final_score"] = final
    c["helpfulness_multiplier"] = hlp
    c["tier_multiplier"] = tier_mult
    c["reputation_modifier"] = rep_mod
    c["credit_equivalent"] = credit_eq
    c["validator_ids"] = req.validator_ids
    c["completed_at"] = datetime.utcnow().isoformat() + "Z"
    store.put("contributions", req.contribution_id, c)

    # Update contributor points and balance
    contributor["points"] = contributor.get("points", 0) + int(final)
    contributor["credits_balance"] = round(contributor.get("credits_balance", 0) + credit_eq, 2)
    contributor["last_submission_at"] = datetime.utcnow().isoformat() + "Z"
    contributor["decay_status"] = "active"  # reset decay clock
    store.put("contributors", c["contributor_id"], contributor)

    # Create transaction
    txn_id = f"txn_{uuid.uuid4().hex[:8]}"
    txn = {
        "id": txn_id,
        "contributor_id": c["contributor_id"],
        "type": "earn",
        "amount": credit_eq,
        "points": int(final),
        "contribution_id": req.contribution_id,
        "validator_ids": req.validator_ids,
        "helpfulness_multiplier": hlp,
        "tier_multiplier": tier_mult,
        "reputation_modifier": rep_mod,
        "credit_equivalent": credit_eq,
        "description": f"Points awarded for validated {c['type']}",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    store.put("transactions", txn_id, txn)

    # Update quarterly stats
    q2 = store.get("quarterly_stats", "2024-Q2") or {"quarter": "2024-Q2", "total_credits_issued": 0}
    q2["total_credits_issued"] = q2.get("total_credits_issued", 0) + int(final)
    store.put("quarterly_stats", "2024-Q2", q2)

    return {"transaction_id": txn_id, "points_awarded": int(final), "credit_equivalent": credit_eq}


# ── Pre-submission Classifier (Change 2) ───────────────────────────────────

class PreClassifyRequest(BaseModel):
    contributor_id: str
    title: str
    description: str
    what_went_wrong: Optional[str] = None


@router.post("/pre-classify")
def pre_classify(req: PreClassifyRequest):
    """
    Pre-submission quality classifier.
    Flags generic feedback before it enters the review queue.
    Contributor sees the flag and can revise before submitting.
    Does NOT block submission — can_submit is always True; it's advisory.
    """
    combined = f"{req.title} {req.description} {req.what_went_wrong or ''}".lower()
    flags = []
    suggestions = []

    # Check for generic phrases
    generic_hits = [p for p in GENERIC_PHRASES if p in combined]
    if generic_hits:
        flags.append("generic_language")
        suggestions.append("Replace generic descriptions with specific model outputs and exact errors.")

    # Check length
    total_chars = len(req.description or "") + len(req.what_went_wrong or "")
    if total_chars < 80:
        flags.append("too_brief")
        suggestions.append("Submissions under 80 characters rarely provide enough signal. Add specifics.")

    # Check for domain specificity (simple heuristic: numbers, technical terms)
    has_specifics = any(char.isdigit() for char in combined) or len(combined.split()) > 20
    if not has_specifics and "too_brief" not in flags:
        flags.append("lacks_specifics")
        suggestions.append("Include specific values, outputs, or domain terms to improve signal quality.")

    # Signal quality determination
    if not flags:
        signal = "high"
    elif len(flags) == 1 and "lacks_specifics" in flags:
        signal = "medium"
    elif "generic_language" in flags:
        signal = "generic"
    else:
        signal = "low"

    # Signal quality modifier preview
    signal_mod = get_signal_quality_modifier(req.contributor_id)

    return {
        "quality_signal": signal,
        "flags": flags,
        "can_submit": True,  # advisory only — never blocks
        "suggestion": " ".join(suggestions) if suggestions else "Looks good — submission is ready.",
        "signal_quality_modifier_current": signal_mod,
        "signal_quality_modifier_note": (
            f"Your current signal quality modifier is {signal_mod:.2f}x. "
            "High-quality submissions raise this; consecutive low-signal submissions reduce it (floor 0.20x)."
        ),
    }


@router.get("/leaderboard")
def get_leaderboard(limit: int = 50, tier: Optional[str] = None, domain: Optional[str] = None):
    contributors = store.list_all("contributors")
    if tier:
        contributors = [c for c in contributors if c["tier"] == tier]
    if domain:
        contributors = [c for c in contributors if domain in c.get("domains", [])]
    contributors.sort(key=lambda x: x["points"], reverse=True)
    ranked = []
    for i, c in enumerate(contributors[:limit]):
        ranked.append({
            "rank": i + 1,
            "contributor_id": c["id"],
            "handle": c["handle"],
            "tier": c["tier"],
            "points": c["points"],
            "credits_balance": c["credits_balance"],
            "accuracy_score": c["accuracy_score"],
            "trust_score": c["trust_score"],
            "domains": c["domains"],
        })
    return ranked


@router.get("/exchange-rate")
def get_exchange_rate():
    inflation_active, ceiling = get_inflation_guard_status()
    q2 = store.get("quarterly_stats", "2024-Q2") or {}
    q1 = store.get("quarterly_stats", "2024-Q1") or {}
    return {
        "points_per_dollar": 100,
        "dollar_per_point": EXCHANGE_RATE_PER_POINT,
        "helpfulness_multiplier_ceiling": ceiling,
        "inflation_guard": inflation_active,
        "quarterly_issuance_current": q2.get("total_credits_issued", 0),
        "quarterly_issuance_prior": q1.get("total_credits_issued", 0),
        "note": ("⚠️ Inflation guard active — helpfulness ceiling reduced to 1.5 for remainder of quarter"
                 if inflation_active else
                 "Exchange rate stable — helpfulness ceiling at 2.0"),
    }


@router.get("/stats")
def get_scoring_stats():
    contribs = store.list_all("contributions")
    complete = [c for c in contribs if c["status"] == "complete"]
    total_points = sum(c.get("final_score", 0) or 0 for c in complete)
    by_type = {}
    for c in complete:
        t = c["type"]
        by_type[t] = by_type.get(t, {"count": 0, "total_points": 0})
        by_type[t]["count"] += 1
        by_type[t]["total_points"] += c.get("final_score", 0) or 0
    return {
        "total_contributions": len(contribs),
        "total_validated": len(complete),
        "total_points_issued": total_points,
        "by_type": by_type,
    }
