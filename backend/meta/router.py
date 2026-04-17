"""
CATS — Meta/Brand Service Router (Phase 2)
GET /meta/brand — returns Compute Commons brand metadata for frontend use
GET /meta/health — health check
"""
from fastapi import APIRouter

router = APIRouter()

BRAND_METADATA = {
    "platform_name": "Compute Commons",
    "internal_system_name": "CATS",
    "internal_system_full": "Contribution-to-Access System",
    "tagline": "Earn your seat at the frontier.",
    "one_liner": (
        "A peer-governed network where verified contribution to AI earns redeemable "
        "compute access — not cash, access."
    ),
    "investor_description": (
        "Compute Commons is a contribution-to-access platform that converts verified model improvements "
        "into AI compute credits. Peer governance, trust-chain validation, and a fixed-floor credit economy "
        "replace the pay-to-play dynamic locking smaller organizations out of frontier AI. "
        "The network grows smarter as access grows wider."
    ),
    "homepage_hero": (
        "The next AI divide isn't intelligence. It's access. We built the mechanism to fix that."
    ),
    "hospitality_vertical_pitch": (
        "Restaurants, chefs, and hospitality operators who teach AI how the industry actually works "
        "earn the compute credits to use it. Domain expertise becomes currency."
    ),
    "legal_disclaimer": (
        "Credits have no cash value and cannot be transferred between accounts. "
        "Redemption is for compute access only. The exchange rate is set by the platform "
        "and may be adjusted with 30 days notice. Credits are not investments and carry "
        "no implied interest, appreciation, or speculative value."
    ),
    "legal_rails": {
        "transferable": False,
        "redeemable_for_cash": False,
        "guaranteed_value": False,
        "speculative_value": False,
        "exchange_rate_notice_days": 30,
    },
    "social": {
        "twitter": "@ComputeCommons",
        "github": "github.com/compute-commons",
    },
    "colors": {
        "primary": "#6366f1",
        "accent": "#f59e0b",
        "dark": "#0f172a",
        "surface": "#1e293b",
    },
}


@router.get("/brand")
def get_brand():
    return BRAND_METADATA


# ── Supply & Partner Status (Change 1 + Change 6) ─────────────────────────────

# Simulated partner pool — in production this would come from a database
ACTIVE_PARTNERS = [
    {
        "model": "Claude Sonnet 3.5",
        "provider": "[Partner A]",
        "rate_tier": "Tier 2",
        "restrictions": ["No fine-tuning", "No system prompt access", "Standard context window"],
        "available_hours": 8200,
        "capacity_pct": 0.82,
    },
    {
        "model": "Gemini 1.5 Pro",
        "provider": "[Partner B]",
        "rate_tier": "Tier 1",
        "restrictions": ["No fine-tuning", "Rate limited: 60 req/min"],
        "available_hours": 3100,
        "capacity_pct": 0.61,
    },
    {
        "model": "GPT-4o",
        "provider": "[Partner C]",
        "rate_tier": "Tier 2",
        "restrictions": ["No fine-tuning", "No DALL-E access", "Standard rate limits"],
        "available_hours": 1100,
        "capacity_pct": 0.22,
        "low_supply": True,
    },
]

SUPPLY_LOW_THRESHOLD = 0.25  # below 25% capacity triggers low-supply banner


@router.get("/supply-status")
def get_supply_status():
    """Returns current compute supply status per partner model. No auth required."""
    total_hours = sum(p["available_hours"] for p in ACTIVE_PARTNERS)
    avg_capacity = sum(p["capacity_pct"] for p in ACTIVE_PARTNERS) / len(ACTIVE_PARTNERS)
    any_low = any(p["capacity_pct"] < SUPPLY_LOW_THRESHOLD for p in ACTIVE_PARTNERS)
    return {
        "available": total_hours > 0,
        "total_hours_available": total_hours,
        "avg_capacity_pct": round(avg_capacity, 2),
        "low_supply": any_low,
        "low_supply_threshold": SUPPLY_LOW_THRESHOLD,
        "model_access": [
            {
                "model": p["model"],
                "rate_tier": p["rate_tier"],
                "restrictions": p["restrictions"],
                "available_hours": p["available_hours"],
                "capacity_pct": p["capacity_pct"],
                "status": "low" if p["capacity_pct"] < SUPPLY_LOW_THRESHOLD else "available",
            }
            for p in ACTIVE_PARTNERS
        ],
    }


@router.get("/partners")
def get_partner_status():
    """Public-facing partner count. Names withheld if confidential. No auth required."""
    total_hours = sum(p["available_hours"] for p in ACTIVE_PARTNERS)
    avg_capacity = sum(p["capacity_pct"] for p in ACTIVE_PARTNERS) / len(ACTIVE_PARTNERS)
    if avg_capacity >= 0.5:
        status = "active"
    elif avg_capacity >= 0.2:
        status = "limited"
    else:
        status = "offline"
    return {
        "active_partner_count": len(ACTIVE_PARTNERS),
        "total_compute_hours_available": total_hours,
        "status": status,
        "capacity_pct": round(avg_capacity, 2),
    }


@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Compute Commons", "version": "2.0.0"}
