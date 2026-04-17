"""
CATS — Credits Ledger Router (Phase 2 Rebuild)
Handles: balance, transactions, redemption with compliance, decay, inflation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
from shared import store
from shared.config import (
    EXCHANGE_RATE_PER_POINT, DECAY_RATE_PER_QUARTER, DECAY_FLOOR_CREDITS,
    DECAY_ACTIVE_WINDOW_DAYS, TERMS_VERSION
)

router = APIRouter()


class RedeemRequest(BaseModel):
    contributor_id: str
    credits_amount: float
    redemption_target: str  # must be "compute_access"
    compute_type: Optional[str] = "gpu_inference"
    terms_version_accepted: str


class TransferRequest(BaseModel):
    from_contributor_id: str
    to_contributor_id: str
    amount: float


def compliance_check(contributor_id: str, redemption_target: str, terms_version: str) -> dict:
    """
    Validates redemption compliance. Returns {passed: bool, violations: list}.
    Rules:
    1. Credits are non-transferable (target cannot be another account)
    2. Redemption is for compute access only
    3. Contributor must have accepted current terms
    """
    violations = []
    contributor = store.get("contributors", contributor_id)

    if not contributor:
        return {"passed": False, "violations": ["contributor_not_found"]}

    # Rule 1: Compute-only check
    if redemption_target != "compute_access":
        violations.append("redemption_target_must_be_compute_access")

    # Rule 2: Terms version check
    if not contributor.get("terms_accepted"):
        violations.append("terms_not_accepted")
    elif contributor.get("terms_version") != terms_version:
        violations.append(f"outdated_terms_version_accepted:{contributor.get('terms_version')}_current:{TERMS_VERSION}")

    # Rule 3: Trust score gate
    trust = store.get("trust_scores", contributor_id)
    trust_score = (trust or {}).get("total", 50)
    if trust_score < 40:
        violations.append("trust_score_below_redemption_threshold_40")

    # Log compliance check
    record = store.get("compliance_records", contributor_id) or {
        "contributor_id": contributor_id,
        "transfer_attempts": 0,
        "compliance_flags": [],
    }
    if violations:
        record["compliance_flags"] = list(set(record.get("compliance_flags", []) + violations))
    record["last_check"] = datetime.utcnow().isoformat() + "Z"
    store.put("compliance_records", contributor_id, record)

    return {"passed": len(violations) == 0, "violations": violations}


@router.get("/balance/{contributor_id}")
def get_balance(contributor_id: str):
    c = store.get("contributors", contributor_id)
    if not c:
        raise HTTPException(404, "Contributor not found")

    # Check decay status
    last_sub = c.get("last_submission_at")
    if last_sub:
        last_dt = datetime.fromisoformat(last_sub.replace("Z", ""))
        days_inactive = (datetime.utcnow() - last_dt).days
    else:
        days_inactive = 999

    first_validated = c.get("first_validated_at")
    if first_validated:
        first_dt = datetime.fromisoformat(first_validated.replace("Z", ""))
        months_since_first = (datetime.utcnow() - first_dt).days / 30
    else:
        months_since_first = 0

    in_decay = days_inactive > DECAY_ACTIVE_WINDOW_DAYS and months_since_first > 12

    trust = store.get("trust_scores", contributor_id)
    monthly_redemption_cap = 200.0 if (trust or {}).get("total", 50) < 40 else None

    return {
        "contributor_id": contributor_id,
        "handle": c["handle"],
        "points": c["points"],
        "credits_balance": c["credits_balance"],
        "tier": c["tier"],
        "accuracy_score": c["accuracy_score"],
        "reputation_modifier": c["reputation_modifier"],
        "decay_status": c.get("decay_status", "active"),
        "days_inactive": days_inactive,
        "in_decay_window": in_decay,
        "monthly_redemption_cap": monthly_redemption_cap,
        "trust_score": c.get("trust_score", 0),
    }


@router.get("/transactions/{contributor_id}")
def get_transactions(contributor_id: str, limit: int = 50):
    c = store.get("contributors", contributor_id)
    if not c:
        raise HTTPException(404, "Contributor not found")
    txns = store.query("transactions", "contributor_id", contributor_id)
    txns.sort(key=lambda x: x["created_at"], reverse=True)
    return txns[:limit]


@router.post("/redeem")
def redeem_credits(req: RedeemRequest):
    c = store.get("contributors", req.contributor_id)
    if not c:
        raise HTTPException(404, "Contributor not found")

    # Compliance check
    check = compliance_check(req.contributor_id, req.redemption_target, req.terms_version_accepted)
    if not check["passed"]:
        raise HTTPException(403, f"Compliance check failed: {check['violations']}")

    # Balance check
    if c["credits_balance"] < req.credits_amount:
        raise HTTPException(400, "Insufficient credits balance")

    # Trust score monthly cap
    trust = store.get("trust_scores", req.contributor_id)
    if (trust or {}).get("total", 50) < 40:
        # Check this month's redemptions
        this_month = datetime.utcnow().replace(day=1)
        monthly_txns = [t for t in store.query("transactions", "contributor_id", req.contributor_id)
                        if t["type"] == "redeem"
                        and datetime.fromisoformat(t["created_at"].replace("Z", "")) >= this_month]
        monthly_redeemed = abs(sum(t["amount"] for t in monthly_txns))
        if monthly_redeemed + req.credits_amount > 200:
            raise HTTPException(403, "Monthly redemption cap of $200 exceeded (trust score < 40)")

    # Process redemption
    c["credits_balance"] = round(c["credits_balance"] - req.credits_amount, 2)
    store.put("contributors", req.contributor_id, c)

    txn_id = f"txn_{uuid.uuid4().hex[:8]}"
    txn = {
        "id": txn_id,
        "contributor_id": req.contributor_id,
        "type": "redeem",
        "amount": -req.credits_amount,
        "description": f"Compute access redemption — {req.compute_type or 'gpu_inference'}",
        "redemption_target": req.redemption_target,
        "compute_type": req.compute_type,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    store.put("transactions", txn_id, txn)

    gpu_hours = req.credits_amount / 1.0  # $1 = 1 GPU-hour approximate
    return {
        "transaction_id": txn_id,
        "credits_redeemed": req.credits_amount,
        "new_balance": c["credits_balance"],
        "compute_quota_granted": f"{gpu_hours:.1f} GPU-hours",
        "legal_notice": "Credits have no cash value. Redemption is for compute access only. No refunds.",
    }


@router.post("/transfer")
def attempt_transfer(req: TransferRequest):
    """
    Always rejects. Credits are non-transferable.
    Logs the attempt for compliance.
    """
    c = store.get("contributors", req.from_contributor_id)
    if c:
        c["transfer_attempts"] = c.get("transfer_attempts", 0) + 1
        flags = c.get("compliance_flags", [])
        if "transfer_attempted" not in flags:
            flags.append("transfer_attempted")
        c["compliance_flags"] = flags
        store.put("contributors", req.from_contributor_id, c)

        # Update compliance record
        record = store.get("compliance_records", req.from_contributor_id) or {}
        record["transfer_attempts"] = record.get("transfer_attempts", 0) + 1
        record["compliance_flags"] = list(set(record.get("compliance_flags", []) + ["transfer_attempted"]))
        store.put("compliance_records", req.from_contributor_id, record)

    raise HTTPException(
        403,
        "Credits are non-transferable. Peer-to-peer credit trading is prohibited. "
        "This attempt has been logged."
    )


@router.get("/compliance-status/{contributor_id}")
def get_compliance_status(contributor_id: str):
    c = store.get("contributors", contributor_id)
    if not c:
        raise HTTPException(404, "Contributor not found")

    record = store.get("compliance_records", contributor_id) or {}
    return {
        "contributor_id": contributor_id,
        "terms_accepted": c.get("terms_accepted", False),
        "terms_version": c.get("terms_version"),
        "last_accepted_date": c.get("terms_accepted_at"),
        "transfer_attempts": c.get("transfer_attempts", 0),
        "compliance_flags": c.get("compliance_flags", []),
        "is_compliant": len(c.get("compliance_flags", [])) == 0 and c.get("terms_accepted", False),
        "current_terms_version": TERMS_VERSION,
    }


@router.post("/decay/run")
def run_decay_job():
    """
    Quarterly decay job. Decays credits by 10% for inactive contributors.
    In production this would be scheduled. Here it's manually triggerable.
    """
    contributors = store.list_all("contributors")
    decayed = []
    exempt = []

    for c in contributors:
        last_sub = c.get("last_submission_at")
        if last_sub:
            last_dt = datetime.fromisoformat(last_sub.replace("Z", ""))
            days_inactive = (datetime.utcnow() - last_dt).days
        else:
            days_inactive = 999

        first_validated = c.get("first_validated_at")
        months_since_first = 0
        if first_validated:
            first_dt = datetime.fromisoformat(first_validated.replace("Z", ""))
            months_since_first = (datetime.utcnow() - first_dt).days / 30

        # Exempt: active in last 90 days
        if days_inactive <= 90:
            c["decay_status"] = "active"
            store.put("contributors", c["id"], c)
            exempt.append(c["id"])
            continue

        # Decay only kicks in after 12 months of inactivity
        if months_since_first < 12:
            exempt.append(c["id"])
            continue

        # Apply decay
        if c["credits_balance"] > DECAY_FLOOR_CREDITS * EXCHANGE_RATE_PER_POINT:
            decay_amount = c["credits_balance"] * DECAY_RATE_PER_QUARTER
            new_balance = max(
                DECAY_FLOOR_CREDITS * EXCHANGE_RATE_PER_POINT,
                c["credits_balance"] - decay_amount
            )
            c["credits_balance"] = round(new_balance, 2)
            c["decay_status"] = "decaying" if new_balance > DECAY_FLOOR_CREDITS * EXCHANGE_RATE_PER_POINT else "floor"
            store.put("contributors", c["id"], c)

            txn_id = f"txn_decay_{c['id']}_{uuid.uuid4().hex[:6]}"
            store.put("transactions", txn_id, {
                "id": txn_id, "contributor_id": c["id"], "type": "decay",
                "amount": -round(decay_amount, 2),
                "description": "Quarterly credit decay (10%) — inactivity > 12 months",
                "created_at": datetime.utcnow().isoformat() + "Z",
            })
            decayed.append({"id": c["id"], "decay_amount": round(decay_amount, 2)})
        else:
            c["decay_status"] = "floor"
            store.put("contributors", c["id"], c)

    return {"decayed_count": len(decayed), "exempt_count": len(exempt), "details": decayed}
