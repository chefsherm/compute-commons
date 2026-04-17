"""
Compute Commons — Contributor Progression Layer (Change 3)
Quality-based tiers: contributor → Validator → Field Expert → Founding Reviewer
Public profile endpoint (no auth required)
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from shared import store

router = APIRouter()

# ── Progression tier definitions ──────────────────────────────────────────────

PROGRESSION_TIERS = [
    {
        "tier": "Founding Reviewer",
        "label": "Founding Reviewer",
        "badge_color": "#a78bfa",
        "min_validated": 30,
        "min_accuracy": 0.90,
        "min_domains": 1,
        "requires_governance": True,
        "description": "≥30 validated submissions · ≥90% accuracy · governance participation",
    },
    {
        "tier": "Field Expert",
        "label": "Field Expert",
        "badge_color": "#fbbf24",
        "min_validated": 15,
        "min_accuracy": 0.85,
        "min_domains": 2,
        "requires_governance": False,
        "description": "≥15 validated submissions · ≥85% accuracy · ≥2 distinct domains",
    },
    {
        "tier": "Validator",
        "label": "Validator",
        "badge_color": "#818cf8",
        "min_validated": 5,
        "min_accuracy": 0.75,
        "min_domains": 1,
        "requires_governance": False,
        "description": "≥5 validated submissions · ≥75% accuracy",
    },
    {
        "tier": "contributor",
        "label": "Contributor",
        "badge_color": "#94a3b8",
        "min_validated": 0,
        "min_accuracy": 0.0,
        "min_domains": 0,
        "requires_governance": False,
        "description": "Starting tier",
    },
]


def _compute_progression_tier(contributor_id: str) -> dict:
    """Calculate what progression tier a contributor qualifies for."""
    contributor = store.get("contributors", contributor_id)
    if not contributor:
        return PROGRESSION_TIERS[-1]  # default: Contributor

    all_contribs = store.query("contributions", "contributor_id", contributor_id)
    validated = [c for c in all_contribs if c["status"] == "complete"]
    validated_count = len(validated)
    accuracy = contributor.get("accuracy_score", 0.0)
    distinct_domains = len(set(
        c.get("domain") or (c.get("metadata") or {}).get("domain") or ""
        for c in validated
        if c.get("domain") or (c.get("metadata") or {}).get("domain")
    ))
    has_governance = contributor.get("governance_votes_cast", 0) > 0

    for tier_def in PROGRESSION_TIERS:
        meets_count = validated_count >= tier_def["min_validated"]
        meets_accuracy = accuracy >= tier_def["min_accuracy"]
        meets_domains = distinct_domains >= tier_def["min_domains"]
        meets_governance = (not tier_def["requires_governance"]) or has_governance
        if meets_count and meets_accuracy and meets_domains and meets_governance:
            return tier_def

    return PROGRESSION_TIERS[-1]


@router.post("/check/{contributor_id}")
def check_progression(contributor_id: str):
    """
    Check and apply progression tier for a contributor.
    Returns advancement notification if tier changed.
    """
    contributor = store.get("contributors", contributor_id)
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    current_tier = contributor.get("progression_tier", "contributor")
    new_tier_def = _compute_progression_tier(contributor_id)
    new_tier = new_tier_def["tier"]

    advanced = new_tier != current_tier
    if advanced:
        contributor["progression_tier"] = new_tier
        store.put("contributors", contributor_id, contributor)

    return {
        "contributor_id": contributor_id,
        "handle": contributor["handle"],
        "from_tier": current_tier,
        "to_tier": new_tier,
        "advanced": advanced,
        "tier_def": new_tier_def,
        "notification": (
            {
                "type": "tier_advancement",
                "title": f"🎉 You've been promoted to {new_tier}!",
                "body": f"Your contribution quality has earned you {new_tier} status. {new_tier_def['description']}.",
                "triggered_at": datetime.utcnow().isoformat() + "Z",
            }
            if advanced else None
        ),
    }


@router.get("/profile/{handle}")
def get_public_profile(handle: str):
    """
    Public-facing contributor profile. No authentication required.
    Visible outside the platform without login.
    """
    all_contributors = store.list_all("contributors")
    contributor = next((c for c in all_contributors if c["handle"] == handle), None)
    if not contributor:
        raise HTTPException(404, f"No contributor with handle '{handle}'")

    contributor_id = contributor["id"]
    all_contribs = store.query("contributions", "contributor_id", contributor_id)
    validated = [c for c in all_contribs if c["status"] == "complete"]

    # Domains flagged (contributed to)
    domains = sorted(set(
        d
        for c in all_contribs
        for d in ([c.get("domain")] if c.get("domain") else contributor.get("domains", []))
        if d
    ))

    # Submissions acted on by lab partners
    acted_on = [c for c in validated if c.get("acted_on")]

    # Contribution type breakdown
    type_counts: dict = {}
    for c in validated:
        t = c.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    tier_def = _compute_progression_tier(contributor_id)

    return {
        "handle": handle,
        "progression_tier": tier_def["tier"],
        "progression_tier_label": tier_def["label"],
        "badge_color": tier_def["badge_color"],
        "tier_description": tier_def["description"],
        "platform_tier": contributor["tier"],
        "domains": domains,
        "accuracy_rate": contributor.get("accuracy_score", 0.0),
        "validated_submissions": len(validated),
        "acted_on_count": len(acted_on),
        "contribution_type_breakdown": type_counts,
        "member_since": contributor.get("created_at", "")[:10],
        "trust_score": contributor.get("trust_score", 0.0),
        "public_url": f"/profile/{handle}",
    }


@router.get("/tiers")
def get_tier_definitions():
    """Return all progression tier definitions."""
    return {"tiers": PROGRESSION_TIERS}
