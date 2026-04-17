"""
CATS — Validation Service Router
Handles: queue, attest/flag/reject, accuracy scoring, vouching, staking
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
from shared import store
from shared.config import STAKE_MAX_CREDITS, STAKE_UPHOLD_BONUS

router = APIRouter()

EXPERT_TIERS = {"expert", "partner"}
VALIDATOR_TIERS = {"validator", "expert", "partner"}


class ValidateRequest(BaseModel):
    validator_id: str
    decision: str  # "attest" | "flag" | "reject"
    confidence: float
    notes: str
    stake_credits: Optional[int] = None


class VouchRequest(BaseModel):
    voucher_id: str
    vouchee_id: str
    notes: str


class ResolveStakeRequest(BaseModel):
    stake_id: str
    upheld: bool
    resolved_by: str


@router.get("/queue/{validator_id}")
def get_validation_queue(validator_id: str):
    validator = store.get("contributors", validator_id)
    if not validator:
        raise HTTPException(404, "Validator not found")
    if validator["tier"] not in VALIDATOR_TIERS:
        raise HTTPException(403, "Must be Validator tier or above")

    # Return pending/validating contributions not already validated by this validator
    contribs = store.list_all("contributions")
    queue = [
        c for c in contribs
        if c["status"] in ("pending", "validating")
        and validator_id not in c.get("validator_ids", [])
        and c["contributor_id"] != validator_id
    ]
    # Expert tier gets high-value contributions prioritized
    if validator["tier"] in EXPERT_TIERS:
        trust = store.get("trust_scores", validator_id)
        if trust and trust.get("total", 0) > 70:
            queue.sort(key=lambda x: (x.get("base_score") or 0), reverse=True)
    return queue[:20]


@router.post("/validate/{contribution_id}")
def validate_contribution(contribution_id: str, req: ValidateRequest):
    c = store.get("contributions", contribution_id)
    if not c:
        raise HTTPException(404, "Contribution not found")

    validator = store.get("contributors", req.validator_id)
    if not validator:
        raise HTTPException(404, "Validator not found")
    if validator["tier"] not in VALIDATOR_TIERS:
        raise HTTPException(403, "Must be Validator tier or above")

    # red_team_report requires Expert tier
    if c["type"] == "red_team_report" and validator["tier"] not in EXPERT_TIERS:
        raise HTTPException(403, "red_team_report requires Expert-tier validator")

    # open_source_connector requires Expert tier
    if c["type"] == "open_source_connector" and validator["tier"] not in EXPERT_TIERS:
        raise HTTPException(403, "open_source_connector requires Expert-tier validator")

    # Collusion detection — check mutual validation history
    mutual = [v for v in store.list_all("validations")
              if v["validator_id"] == req.validator_id
              and store.get("contributions", v["contribution_id"], ) is not None
              and (store.get("contributions", v["contribution_id"]) or {}).get("contributor_id") ==
                   (store.get("contributions", contribution_id) or {}).get("contributor_id")]
    if len(mutual) >= 3:
        c["abuse_flags"] = list(set(c.get("abuse_flags", []) + ["collusion_risk"]))

    # Staking
    if req.stake_credits is not None:
        if validator["tier"] not in EXPERT_TIERS:
            raise HTTPException(403, "Only Expert/Partner tier can stake credits")
        if req.stake_credits > STAKE_MAX_CREDITS:
            raise HTTPException(400, f"Maximum stake is {STAKE_MAX_CREDITS} credits")
        if validator.get("credits_balance", 0) < req.stake_credits:
            raise HTTPException(400, "Insufficient credits to stake")

        stake_id = f"stake_{uuid.uuid4().hex[:8]}"
        stake = {
            "id": stake_id,
            "contributor_id": req.validator_id,
            "contribution_id": contribution_id,
            "amount": req.stake_credits,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        store.put("stakes", stake_id, stake)

        # Deduct staked credits temporarily
        validator["credits_balance"] = round(validator.get("credits_balance", 0) - req.stake_credits * 0.01, 2)  # points→credits
        store.put("contributors", req.validator_id, validator)

    val_id = f"val_{uuid.uuid4().hex[:8]}"
    val = {
        "id": val_id,
        "contribution_id": contribution_id,
        "validator_id": req.validator_id,
        "decision": req.decision,
        "confidence": req.confidence,
        "notes": req.notes,
        "staked_credits": req.stake_credits,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    store.put("validations", val_id, val)

    # Update contribution
    c["status"] = "validating"
    vids = c.get("validator_ids", [])
    if req.validator_id not in vids:
        vids.append(req.validator_id)
    c["validator_ids"] = vids

    # If attested by 2+ validators and all attest → complete
    all_vals = [v for v in store.list_all("validations") if v["contribution_id"] == contribution_id]
    attest_count = sum(1 for v in all_vals if v["decision"] == "attest")
    reject_count = sum(1 for v in all_vals if v["decision"] == "reject")
    if reject_count >= 1 and req.decision == "reject":
        c["status"] = "rejected"
    elif attest_count >= 2:
        c["status"] = "complete"

    store.put("contributions", contribution_id, c)

    return {"validation_id": val_id, "contribution_status": c["status"]}


@router.get("/validator/{validator_id}/accuracy")
def get_validator_accuracy(validator_id: str):
    contributor = store.get("contributors", validator_id)
    if not contributor:
        raise HTTPException(404, "Validator not found")

    vals = store.query("validations", "validator_id", validator_id)
    attest = sum(1 for v in vals if v["decision"] == "attest")
    total = len(vals)
    return {
        "validator_id": validator_id,
        "handle": contributor["handle"],
        "accuracy_score": contributor["accuracy_score"],
        "total_validations": total,
        "attestations": attest,
        "flags": total - attest,
        "tier": contributor["tier"],
    }


@router.post("/vouch")
def vouch_contributor(req: VouchRequest):
    voucher = store.get("contributors", req.voucher_id)
    vouchee = store.get("contributors", req.vouchee_id)
    if not voucher or not vouchee:
        raise HTTPException(404, "Contributor not found")
    if voucher["tier"] not in VALIDATOR_TIERS:
        raise HTTPException(403, "Must be Validator tier or above to vouch")

    vouchee["vouch_chain_depth"] = vouchee.get("vouch_chain_depth", 0) + 1
    store.put("contributors", req.vouchee_id, vouchee)
    return {"status": "vouched", "vouchee_id": req.vouchee_id, "new_depth": vouchee["vouch_chain_depth"]}


@router.post("/stake/resolve")
def resolve_stake(req: ResolveStakeRequest):
    stake = store.get("stakes", req.stake_id)
    if not stake:
        raise HTTPException(404, "Stake not found")

    contributor = store.get("contributors", stake["contributor_id"])
    if not contributor:
        raise HTTPException(404, "Contributor not found")

    if req.upheld:
        # Return stake + bonus
        bonus_credits = STAKE_UPHOLD_BONUS * 0.01  # 50 credits = $0.50
        contributor["credits_balance"] = round(
            contributor.get("credits_balance", 0) + stake["amount"] * 0.01 + bonus_credits, 2
        )
        contributor["points"] = contributor.get("points", 0) + STAKE_UPHOLD_BONUS
        stake["status"] = "upheld"
    else:
        # Stake lost (already deducted on creation)
        stake["status"] = "overturned"

    stake["resolved_at"] = datetime.utcnow().isoformat() + "Z"
    store.put("stakes", req.stake_id, stake)
    store.put("contributors", stake["contributor_id"], contributor)
    return {"stake_id": req.stake_id, "status": stake["status"],
            "credits_balance": contributor["credits_balance"]}


@router.get("/stakes")
def list_stakes(contributor_id: Optional[str] = None, status: Optional[str] = None):
    stakes = store.list_all("stakes")
    if contributor_id:
        stakes = [s for s in stakes if s["contributor_id"] == contributor_id]
    if status:
        stakes = [s for s in stakes if s["status"] == status]
    return stakes
