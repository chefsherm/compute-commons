"""
CATS — Intake Service Router
All 15 contribution types, abuse detection, rate limiting
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid, math
from shared import store
from shared.models import Contribution, ContributionType, ContributionStatus, ContributionMetadata
from shared.config import (
    VELOCITY_LIMIT_PER_DAY, SIMILARITY_FLAG_THRESHOLD,
    BOT_DETECTION_SECONDS, EXCHANGE_RATE_PER_POINT
)

router = APIRouter()

TIER_MULTIPLIERS = {"contributor": 1.0, "validator": 1.2, "expert": 1.5, "partner": 2.0}

# ── Domain Taxonomy (Change 4) ───────────────────────────────────────────────

DOMAIN_TAXONOMY = {
    "biomedical": "Biomedical & Life Sciences",
    "chemistry": "Chemistry & Materials Science",
    "climate_environment": "Climate & Environmental Science",
    "code_software": "Software Engineering & Code",
    "creative_writing": "Creative Writing & Narrative",
    "culinary_food": "Culinary & Food Science",
    "economics_finance": "Economics & Finance",
    "education_pedagogy": "Education & Pedagogy",
    "engineering_hardware": "Engineering & Hardware",
    "healthcare_clinical": "Healthcare & Clinical Medicine",
    "history_social": "History & Social Sciences",
    "law_legal": "Law & Legal Systems",
    "linguistics_language": "Linguistics & Low-Resource Languages",
    "math_formal": "Mathematics & Formal Reasoning",
    "music_audio": "Music & Audio",
    "philosophy_ethics": "Philosophy & Ethics",
    "physics_astronomy": "Physics & Astronomy",
    "policy_governance": "Policy & Governance",
    "psychology_cognition": "Psychology & Cognitive Science",
    "security_safety": "Security, Safety & Red-Teaming",
}

# Allowed submission types
SUBMISSION_TYPES = {"edge_case", "error_report", "blind_spot", "domain_correction"}

# ── Type definitions ──────────────────────────────────────────────────────────

CONTRIBUTION_TYPE_SPECS = {
    "bug_report":             {"base_min": 50,  "base_max": 150,  "helpfulness_range": [1.0, 1.5], "verification": "auto+validator", "gaming_risk": "low"},
    "edge_case":              {"base_min": 80,  "base_max": 200,  "helpfulness_range": [1.0, 1.7], "verification": "validator", "gaming_risk": "medium"},
    "safety_testing":         {"base_min": 100, "base_max": 250,  "helpfulness_range": [1.2, 1.8], "verification": "expert_validator", "gaming_risk": "low"},
    "domain_labeling":        {"base_min": 100, "base_max": 400,  "helpfulness_range": [1.0, 2.0], "verification": "validator", "gaming_risk": "medium"},
    "training_dataset":       {"base_min": 200, "base_max": 600,  "helpfulness_range": [1.2, 2.0], "verification": "expert_validator", "gaming_risk": "medium"},
    "evaluation_framework":   {"base_min": 200, "base_max": 500,  "helpfulness_range": [1.3, 2.0], "verification": "expert_validator", "gaming_risk": "low"},
    "synthetic_pipeline":     {"base_min": 150, "base_max": 450,  "helpfulness_range": [1.3, 2.0], "verification": "expert_validator", "gaming_risk": "medium"},
    # Phase 2
    "donated_compute":        {"base_min": 50,  "base_max": 300,  "helpfulness_range": [1.0, 1.5], "verification": "usage_logs", "gaming_risk": "low", "daily_cap_hours": 80},
    "prompt_library":         {"base_min": 80,  "base_max": 200,  "helpfulness_range": [1.0, 1.6], "verification": "peer_review+sampling", "gaming_risk": "medium", "similarity_check": True},
    "red_team_report":        {"base_min": 200, "base_max": 500,  "helpfulness_range": [2.0, 2.0], "verification": "two_expert_validators", "gaming_risk": "low", "helpfulness_floor": 2.0},
    "agent_workflow":         {"base_min": 120, "base_max": 300,  "helpfulness_range": [1.2, 1.8], "verification": "reproduction_testing", "gaming_risk": "medium", "min_steps": 3},
    "open_source_connector":  {"base_min": 200, "base_max": 400,  "helpfulness_range": [1.5, 2.0], "verification": "expert_code_review", "gaming_risk": "low"},
    "verified_referral":      {"base_min": 80,  "base_max": 150,  "helpfulness_range": [1.0, 1.3], "verification": "new_contributor_first_submission", "gaming_risk": "medium", "non_affiliated_validators": 3},
    "human_feedback_session": {"base_min": 100, "base_max": 300,  "helpfulness_range": [1.0, 1.8], "verification": "statistical_consistency", "gaming_risk": "high", "consistency_min": 0.80},
    "community_moderation":   {"base_min": 30,  "base_max": 100,  "helpfulness_range": [1.0, 1.0], "verification": "auto_participation_log", "gaming_risk": "low"},
}


class SubmitContributionRequest(BaseModel):
    contributor_id: str
    type: str
    title: str
    description: str
    metadata: Optional[dict] = None
    # Change 4 — Domain taxonomy + structured submission (required for non-compute types)
    domain: Optional[str] = None               # Must be in DOMAIN_TAXONOMY
    submission_type: Optional[str] = None      # edge_case | error_report | blind_spot | domain_correction
    what_went_wrong: Optional[str] = None      # min 20 chars
    correct_answer: Optional[str] = None       # min 10 chars
    domain_qualification: Optional[str] = None # why contributor is qualified
    credential_reference: Optional[str] = None # link/citation to verifiable credential


class FlagRequest(BaseModel):
    flagged_by: str
    reason: str


@router.post("/contributions/submit")
def submit_contribution(req: SubmitContributionRequest):
    contributor = store.get("contributors", req.contributor_id)
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    if req.type not in CONTRIBUTION_TYPE_SPECS:
        raise HTTPException(400, f"Unknown contribution type: {req.type}")

    # Change 4 — Enforce domain taxonomy and required structured fields
    COMPUTE_ONLY_TYPES = {"donated_compute", "community_moderation", "verified_referral"}
    if req.type not in COMPUTE_ONLY_TYPES:
        if not req.domain:
            raise HTTPException(400, "'domain' is required. Use GET /intake/taxonomy/domains to see valid values.")
        if req.domain not in DOMAIN_TAXONOMY:
            raise HTTPException(400, f"Unknown domain '{req.domain}'. Use GET /intake/taxonomy/domains.")
        if not req.submission_type:
            raise HTTPException(400, "'submission_type' is required: edge_case | error_report | blind_spot | domain_correction")
        if req.submission_type not in SUBMISSION_TYPES:
            raise HTTPException(400, f"Invalid submission_type '{req.submission_type}'.")
        if not req.what_went_wrong or len(req.what_went_wrong) < 20:
            raise HTTPException(400, "'what_went_wrong' is required (min 20 characters).")
        if not req.correct_answer or len(req.correct_answer) < 10:
            raise HTTPException(400, "'correct_answer' is required (min 10 characters).")
        if not req.domain_qualification:
            raise HTTPException(400, "'domain_qualification' is required — explain why you are qualified.")

    spec = CONTRIBUTION_TYPE_SPECS[req.type]
    abuse_flags = []
    status = ContributionStatus.pending

    # Bot detection — account < 90s old check (simulated via created_at)
    created = datetime.fromisoformat(contributor["created_at"].replace("Z", ""))
    age_seconds = (datetime.utcnow() - created).total_seconds()
    if age_seconds < BOT_DETECTION_SECONDS:
        raise HTTPException(403, "Account too new — bot detection triggered")

    # Velocity check
    all_contribs = store.query("contributions", "contributor_id", req.contributor_id)
    recent = [c for c in all_contribs
              if datetime.fromisoformat(c["submitted_at"].replace("Z","")) > datetime.utcnow() - timedelta(hours=24)]
    if len(recent) >= VELOCITY_LIMIT_PER_DAY:
        abuse_flags.append("velocity_exceeded")
        status = ContributionStatus.on_hold

    # Type-specific validation
    meta = ContributionMetadata(**(req.metadata or {}))

    if req.type == "agent_workflow":
        if meta.step_count and meta.step_count < 3:
            raise HTTPException(400, "agent_workflow requires minimum 3 steps")
        if not meta.outcome_annotation:
            raise HTTPException(400, "agent_workflow requires outcome_annotation (success/failure)")

    if req.type == "human_feedback_session":
        if meta.session_consistency_score is not None and meta.session_consistency_score < 0.80:
            abuse_flags.append("consistency_below_threshold")
            status = ContributionStatus.rejected

    if req.type == "donated_compute":
        # Check daily cap (80 GPU hours/day per contributor)
        today_compute = [c for c in all_contribs
                         if c["type"] == "donated_compute"
                         and datetime.fromisoformat(c["submitted_at"].replace("Z","")) > datetime.utcnow() - timedelta(hours=24)]
        total_hours = sum((c.get("metadata") or {}).get("gpu_hours", 0) or 0 for c in today_compute)
        if total_hours + (meta.gpu_hours or 0) > 80:
            raise HTTPException(429, "Daily compute donation cap exceeded (80 GPU hours/day)")

    contrib_id = f"c_{uuid.uuid4().hex[:8]}"
    contrib = Contribution(
        id=contrib_id,
        contributor_id=req.contributor_id,
        type=ContributionType(req.type),
        title=req.title,
        description=req.description,
        status=status,
        submitted_at=datetime.utcnow().isoformat() + "Z",
        abuse_flags=abuse_flags,
        metadata=meta,
        # Change 4 fields
        domain=req.domain,
        submission_type=req.submission_type,
        what_went_wrong=req.what_went_wrong,
        correct_answer=req.correct_answer,
        domain_qualification=req.domain_qualification,
        credential_reference=req.credential_reference,
        verified_domain_expert=bool(req.credential_reference),
    )
    store.put("contributions", contrib_id, contrib.model_dump())

    # Mirror submission in Firestore
    store.put("submissions", contrib_id, {
        "id": contrib_id,
        "contributor_id": req.contributor_id,
        "status": status,
        "model": "generic-v1",
        "timestamp": contrib.submitted_at
    })

    # Update contributor's last submission time and type history
    contributor["last_submission_at"] = datetime.utcnow().isoformat() + "Z"
    types = set(contributor.get("contribution_types_used", []))
    types.add(req.type)
    contributor["contribution_types_used"] = list(types)
    store.put("contributors", req.contributor_id, contributor)

    return {
        "contribution_id": contrib_id,
        "status": status,
        "abuse_flags": abuse_flags,
        "verified_domain_expert": bool(req.credential_reference),
        "domain": req.domain,
        "submission_type": req.submission_type,
    }


@router.get("/receipt/{contribution_id}")
def get_credit_receipt(contribution_id: str):
    """
    Credit receipt generated after a contribution is complete.
    Shows the contributor the exact score, all multipliers, and the reason for each.
    """
    c = store.get("contributions", contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")
    if c["status"] != "complete":
        return {
            "contribution_id": contribution_id,
            "status": c["status"],
            "message": "Receipt available only after validation is complete.",
        }

    base = c.get("base_score") or 0
    hlp = c.get("helpfulness_multiplier") or 1.0
    tier = c.get("tier_multiplier") or 1.0
    rep = c.get("reputation_modifier") or 1.0
    final = c.get("final_score") or 0
    credits = c.get("credit_equivalent") or 0

    return {
        "contribution_id": contribution_id,
        "title": c["title"],
        "type": c["type"],
        "domain": c.get("domain"),
        "submission_type": c.get("submission_type"),
        "verified_domain_expert": c.get("verified_domain_expert", False),
        "acted_on": c.get("acted_on", False),
        "score_breakdown": {
            "base_score": base,
            "helpfulness_multiplier": hlp,
            "tier_multiplier": tier,
            "reputation_modifier": rep,
            "final_score": final,
            "credit_equivalent": credits,
        },
        "score_reason": (
            f"Base score {base} × helpfulness {hlp} (signal quality — how much this improved the model) "
            f"× tier {tier} (your contributor tier) "
            f"× reputation {rep} (your accuracy history) "
            f"= {final} points = ${credits:.2f} compute credit."
        ),
        "access_equivalent": f"${credits:.2f} redeemable for compute time with any active lab partner.",
    }


@router.get("/contributions/{contribution_id}/status")
def get_contribution_status(contribution_id: str):
    c = store.get("contributions", contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")
    return c


@router.get("/contributions/contributor/{contributor_id}")
def list_contributor_contributions(contributor_id: str):
    return store.query("contributions", "contributor_id", contributor_id)


@router.post("/contributions/{contribution_id}/flag")
def flag_contribution(contribution_id: str, req: FlagRequest):
    c = store.get("contributions", contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")
    c["flags"].append({"flagged_by": req.flagged_by, "reason": req.reason,
                        "at": datetime.utcnow().isoformat() + "Z"})
    c["status"] = ContributionStatus.flagged
    store.put("contributions", contribution_id, c)
    return {"status": "flagged", "contribution_id": contribution_id}


@router.get("/taxonomy")
def get_taxonomy():
    return {"contribution_types": CONTRIBUTION_TYPE_SPECS}


@router.get("/taxonomy/domains")
def get_domain_taxonomy():
    """Returns the structured domain taxonomy for the submission form."""
    return {
        "domains": DOMAIN_TAXONOMY,
        "submission_types": list(SUBMISSION_TYPES),
    }


@router.get("/contributions")
def list_all_contributions(status: Optional[str] = None, type: Optional[str] = None):
    contribs = store.list_all("contributions")
    if status:
        contribs = [c for c in contribs if c["status"] == status]
    if type:
        contribs = [c for c in contribs if c["type"] == type]
    return contribs
