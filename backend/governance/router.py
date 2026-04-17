"""
CATS — Governance Service Router (Phase 2: Bicameral)
Chambers: Community Voice + Expert Council
Includes: proposals, voting, results, disputes, charter, veto logging
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
from shared import store
from shared.config import (
    GOVERNANCE_COMMUNITY_MAJORITY, GOVERNANCE_EXPERT_THRESHOLD,
    GOVERNANCE_VOTE_LOCKOUT_DAYS, GOVERNANCE_ACTIVE_VOTER_DAYS,
    GOVERNANCE_DISPUTE_DAYS
)

router = APIRouter()

COMMUNITY_ELIGIBLE_TIERS = {"validator", "expert", "partner"}
COUNCIL_ELIGIBLE_TIERS = {"expert", "partner"}
VOTE_WEIGHTS = {"validator": 1, "expert": 2, "partner": 3}

# What can/cannot be governed
GOVERNABLE = [
    "contribution_taxonomy_changes",
    "point_value_adjustments_up_to_20pct",
    "new_contribution_type_proposals",
    "validator_accuracy_thresholds",
    "leaderboard_display_rules",
]
NON_GOVERNABLE = [
    "exchange_rate_floor",
    "anti_fraud_and_abuse_controls",
    "lab_partner_agreements",
    "contributor_personal_data",
]

GOVERNANCE_CHARTER = {
    "mission": (
        "The Compute Commons governance framework exists to ensure that the rules of the "
        "Contribution-to-Access System remain fair, transparent, and responsive to the community "
        "that builds it — while protecting contributors, validators, and the network from fraud, "
        "abuse, and legal risk."
    ),
    "chambers": {
        "community_voice": {
            "members": "All contributors with Validator tier or above",
            "voting_rule": "One vote per person. Simple majority of active voters.",
            "active_voter_definition": "Voted at least once in the prior 90 days.",
            "can_propose": [
                "Taxonomy changes",
                "Exchange rate concerns (advisory only)",
                "Contributor disputes",
            ],
            "pass_threshold": "simple_majority_of_active_voters",
        },
        "expert_council": {
            "members": "All Expert and Partner tier contributors",
            "voting_rule": "Weighted votes: Expert = 2, Partner = 3.",
            "ratification_threshold": "60% of total weighted votes",
            "role": "Ratification chamber. Community Voice proposals must be ratified by Expert Council before taking effect.",
        },
    },
    "voting_rules": {
        "sybil_protection": "Voting weight capped at tier ceiling regardless of points held.",
        "lockout": "New accounts cannot vote for 30 days after first validated submission.",
        "weight_cap": "No contributor can exceed Partner-tier voting weight (3).",
    },
    "what_can_be_governed": GOVERNABLE,
    "what_cannot_be_governed": NON_GOVERNABLE,
    "dispute_process": {
        "steps": [
            "Contributor submits appeal with reason",
            "System assigns a panel of 3 Expert-tier validators not affiliated with original decision",
            "Panel has 7 days to render decision",
            "Majority rules — decision is final",
            "All decisions logged publicly",
        ]
    },
    "veto_conditions": {
        "who_can_veto": "Core team only",
        "valid_reasons": ["security", "legal", "safety"],
        "transparency": "All vetoes are logged publicly with stated reason",
    },
    "transparency_commitments": [
        "All votes are recorded with voter ID, chamber, and weight",
        "Inflation guard status is published transparently at /api/scoring/exchange-rate",
        "All governance decisions are immutably logged",
        "Veto log is publicly readable",
        "Dispute outcomes are publicly logged",
    ],
}


class ProposalRequest(BaseModel):
    proposer_id: str
    type: str
    title: str
    description: str
    affected_parameter: str
    proposed_change: str


class VoteRequest(BaseModel):
    voter_id: str
    proposal_id: str
    chamber: str  # "community" | "council"
    vote: str  # "for" | "against"


class DisputeRequest(BaseModel):
    appellant_id: str
    contribution_id: str
    reason: str


class VetoRequest(BaseModel):
    proposal_id: str
    reason: str
    vetoed_by: str = "core_team"


@router.post("/proposals")
def submit_proposal(req: ProposalRequest):
    proposer = store.get("contributors", req.proposer_id)
    if not proposer:
        raise HTTPException(404, "Proposer not found")
    if proposer["tier"] not in COMMUNITY_ELIGIBLE_TIERS:
        raise HTTPException(403, "Must be Validator tier or above to submit proposals")

    # Check 30-day lockout
    first_validated = proposer.get("first_validated_at")
    if first_validated:
        first_dt = datetime.fromisoformat(first_validated.replace("Z", ""))
        if (datetime.utcnow() - first_dt).days < GOVERNANCE_VOTE_LOCKOUT_DAYS:
            raise HTTPException(403, "Must wait 30 days after first validated submission to participate in governance")

    # Validate proposal is for something governable
    valid_types = [
        "taxonomy_change", "point_value_adjustment", "new_contribution_type",
        "validator_accuracy_threshold", "leaderboard_display", "contributor_dispute", "exchange_rate_concern"
    ]
    if req.type not in valid_types:
        raise HTTPException(400, f"Invalid proposal type. Must be one of: {valid_types}")

    prop_id = f"prop_{uuid.uuid4().hex[:6]}"
    proposal = {
        "id": prop_id,
        "proposer_id": req.proposer_id,
        "type": req.type,
        "title": req.title,
        "description": req.description,
        "affected_parameter": req.affected_parameter,
        "proposed_change": req.proposed_change,
        "status": "active",
        "community_votes_for": 0,
        "community_votes_against": 0,
        "council_votes_for": 0,
        "council_votes_against": 0,
        "veto_reason": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "resolved_at": None,
    }
    store.put("governance_proposals", prop_id, proposal)
    return proposal


@router.get("/proposals")
def list_proposals(status: Optional[str] = None):
    proposals = store.list_all("governance_proposals")
    if status:
        proposals = [p for p in proposals if p["status"] == status]
    proposals.sort(key=lambda x: x["created_at"], reverse=True)
    return proposals


@router.post("/vote")
def cast_vote(req: VoteRequest):
    proposal = store.get("governance_proposals", req.proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    if proposal["status"] not in ("active", "pending_ratification"):
        raise HTTPException(400, f"Proposal is not open for voting (status: {proposal['status']})")

    voter = store.get("contributors", req.voter_id)
    if not voter:
        raise HTTPException(404, "Voter not found")

    # Tier check
    if req.chamber == "community" and voter["tier"] not in COMMUNITY_ELIGIBLE_TIERS:
        raise HTTPException(403, "Community chamber requires Validator tier or above")
    if req.chamber == "council" and voter["tier"] not in COUNCIL_ELIGIBLE_TIERS:
        raise HTTPException(403, "Expert Council requires Expert or Partner tier")

    # Trust score gate
    trust = store.get("trust_scores", req.voter_id)
    if (trust or {}).get("total", 50) < 30:
        raise HTTPException(403, "Trust score below 30 — governance participation suspended")

    # 30-day lockout
    first_validated = voter.get("first_validated_at")
    if first_validated:
        first_dt = datetime.fromisoformat(first_validated.replace("Z", ""))
        if (datetime.utcnow() - first_dt).days < GOVERNANCE_VOTE_LOCKOUT_DAYS:
            raise HTTPException(403, "30-day governance lockout for new accounts")

    # Duplicate vote check
    existing = [v for v in store.list_all("governance_votes")
                if v["proposal_id"] == req.proposal_id and v["voter_id"] == req.voter_id]
    if existing:
        raise HTTPException(409, "Already voted on this proposal")

    weight = VOTE_WEIGHTS.get(voter["tier"], 1)

    vote_id = f"vote_{uuid.uuid4().hex[:8]}"
    vote = {
        "id": vote_id,
        "proposal_id": req.proposal_id,
        "voter_id": req.voter_id,
        "chamber": req.chamber,
        "vote": req.vote,
        "weight": weight,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    store.put("governance_votes", vote_id, vote)

    # Update proposal tally
    if req.chamber == "community":
        if req.vote == "for":
            proposal["community_votes_for"] += 1
        else:
            proposal["community_votes_against"] += 1
    else:
        if req.vote == "for":
            proposal["council_votes_for"] += weight
        else:
            proposal["council_votes_against"] += weight

    # Auto-assess community passage (simple majority of active voters)
    if req.chamber == "community":
        total_cv = proposal["community_votes_for"] + proposal["community_votes_against"]
        if total_cv >= 10:  # minimum quorum
            pct_for = proposal["community_votes_for"] / total_cv
            if pct_for > GOVERNANCE_COMMUNITY_MAJORITY:
                proposal["status"] = "pending_ratification"
            elif pct_for <= (1 - GOVERNANCE_COMMUNITY_MAJORITY):
                proposal["status"] = "community_failed"
                proposal["resolved_at"] = datetime.utcnow().isoformat() + "Z"

    # Auto-assess council ratification
    if req.chamber == "council":
        total_cw = proposal["council_votes_for"] + proposal["council_votes_against"]
        if total_cw >= 6:  # minimum quorum (weighted)
            pct_for = proposal["council_votes_for"] / total_cw if total_cw else 0
            if pct_for >= GOVERNANCE_EXPERT_THRESHOLD:
                proposal["status"] = "ratified"
                proposal["resolved_at"] = datetime.utcnow().isoformat() + "Z"
            elif pct_for < (1 - GOVERNANCE_EXPERT_THRESHOLD):
                proposal["status"] = "rejected_by_council"
                proposal["resolved_at"] = datetime.utcnow().isoformat() + "Z"

    store.put("governance_proposals", req.proposal_id, proposal)
    return {"vote_id": vote_id, "proposal_status": proposal["status"], "weight_cast": weight}


@router.get("/results")
def get_results():
    proposals = store.list_all("governance_proposals")
    passed = [p for p in proposals if p["status"] == "ratified"]
    failed = [p for p in proposals if p["status"] in ("community_failed", "rejected_by_council", "vetoed")]
    pending = [p for p in proposals if p["status"] in ("active", "pending_ratification")]
    return {"passed": passed, "failed": failed, "pending": pending}


@router.post("/veto")
def veto_proposal(req: VetoRequest):
    proposal = store.get("governance_proposals", req.proposal_id)
    if not proposal:
        raise HTTPException(404, "Proposal not found")
    proposal["status"] = "vetoed"
    proposal["veto_reason"] = req.reason
    proposal["vetoed_by"] = req.vetoed_by
    proposal["resolved_at"] = datetime.utcnow().isoformat() + "Z"
    store.put("governance_proposals", req.proposal_id, proposal)

    # Audit log
    store.put("audit_log", f"veto_{req.proposal_id}", {
        "type": "veto",
        "proposal_id": req.proposal_id,
        "reason": req.reason,
        "vetoed_by": req.vetoed_by,
        "at": datetime.utcnow().isoformat() + "Z",
    })
    return {"status": "vetoed", "proposal_id": req.proposal_id, "reason": req.reason}


@router.post("/dispute")
def submit_dispute(req: DisputeRequest):
    appellant = store.get("contributors", req.appellant_id)
    if not appellant:
        raise HTTPException(404, "Appellant not found")

    contribution = store.get("contributions", req.contribution_id)
    if not contribution:
        raise HTTPException(404, "Contribution not found")

    # Assign 3 Expert-tier validators not affiliated with the original decision
    original_validators = set(contribution.get("validator_ids", []))
    all_contributors = store.list_all("contributors")
    experts = [
        c for c in all_contributors
        if c["tier"] in COUNCIL_ELIGIBLE_TIERS
        and c["id"] not in original_validators
        and c["id"] != req.appellant_id
    ]
    panel = experts[:3]
    if len(panel) < 3:
        panel = experts  # take what we have

    disp_id = f"disp_{uuid.uuid4().hex[:6]}"
    dispute = {
        "id": disp_id,
        "appellant_id": req.appellant_id,
        "contribution_id": req.contribution_id,
        "reason": req.reason,
        "status": "submitted",
        "panel_ids": [p["id"] for p in panel],
        "decision": None,
        "decision_notes": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "deadline": (datetime.utcnow() + timedelta(days=GOVERNANCE_DISPUTE_DAYS)).isoformat() + "Z",
        "decided_at": None,
    }
    store.put("governance_disputes", disp_id, dispute)
    return dispute


@router.get("/dispute/{dispute_id}")
def get_dispute(dispute_id: str):
    d = store.get("governance_disputes", dispute_id)
    if not d:
        raise HTTPException(404, "Dispute not found")
    return d


@router.get("/disputes")
def list_disputes():
    return store.list_all("governance_disputes")


@router.get("/charter")
def get_charter():
    return GOVERNANCE_CHARTER


@router.get("/audit")
def get_audit_sample(limit: int = 10):
    """Returns a sample of validations for governance audit."""
    validations = store.list_all("validations")
    import random
    sample = random.sample(validations, min(limit, len(validations)))
    return sample


@router.get("/queue")
def get_escalation_queue():
    """Returns flagged contributions awaiting governance escalation."""
    contribs = store.list_all("contributions")
    flagged = [c for c in contribs if c["status"] in ("flagged", "on_hold")]
    return flagged
