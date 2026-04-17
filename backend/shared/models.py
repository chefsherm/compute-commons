"""
CATS — Shared Pydantic Models (Phase 1 + Phase 2)
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# ─── Enums ────────────────────────────────────────────────────────────────────

class ContributorTier(str, Enum):
    contributor = "contributor"
    validator = "validator"
    expert = "expert"
    partner = "partner"


class ContributionType(str, Enum):
    # Phase 1
    bug_report = "bug_report"
    edge_case = "edge_case"
    safety_testing = "safety_testing"
    domain_labeling = "domain_labeling"
    training_dataset = "training_dataset"
    evaluation_framework = "evaluation_framework"
    synthetic_pipeline = "synthetic_pipeline"
    # Phase 2
    donated_compute = "donated_compute"
    prompt_library = "prompt_library"
    red_team_report = "red_team_report"
    agent_workflow = "agent_workflow"
    open_source_connector = "open_source_connector"
    verified_referral = "verified_referral"
    human_feedback_session = "human_feedback_session"
    community_moderation = "community_moderation"


class ContributionStatus(str, Enum):
    pending = "pending"
    validating = "validating"
    complete = "complete"
    flagged = "flagged"
    rejected = "rejected"
    on_hold = "on_hold"


class GovernanceProposalType(str, Enum):
    taxonomy_change = "taxonomy_change"
    point_value_adjustment = "point_value_adjustment"
    new_contribution_type = "new_contribution_type"
    validator_accuracy_threshold = "validator_accuracy_threshold"
    leaderboard_display = "leaderboard_display"
    contributor_dispute = "contributor_dispute"
    exchange_rate_concern = "exchange_rate_concern"


class ProposalStatus(str, Enum):
    active = "active"
    community_passed = "community_passed"
    community_failed = "community_failed"
    pending_ratification = "pending_ratification"
    ratified = "ratified"
    rejected_by_council = "rejected_by_council"
    vetoed = "vetoed"


class DisputeStatus(str, Enum):
    submitted = "submitted"
    panel_assigned = "panel_assigned"
    decided = "decided"


class DecayStatus(str, Enum):
    active = "active"          # submitted in last 90 days — exempt
    exempt = "exempt"          # explicitly exempted
    decaying = "decaying"      # past 12mo inactivity, currently decaying
    floor = "floor"            # at or below 500 credit floor


# ─── Core Models ──────────────────────────────────────────────────────────────

class Contributor(BaseModel):
    id: str
    handle: str
    email: str
    tier: ContributorTier
    points: int = 0
    credits_balance: float = 0.0
    accuracy_score: float = 0.0
    vouch_chain_depth: int = 0
    first_validated_at: Optional[str] = None
    last_submission_at: Optional[str] = None
    created_at: str
    reputation_modifier: float = 1.0
    decay_status: DecayStatus = DecayStatus.active
    trust_score: float = 0.0
    terms_accepted: bool = True
    terms_version: str = "2024-Q2-v1"
    terms_accepted_at: Optional[str] = None
    transfer_attempts: int = 0
    compliance_flags: List[str] = []
    domains: List[str] = []
    contribution_types_used: List[str] = []
    # Change 3 — Progression layer
    progression_tier: str = "contributor"  # contributor | Validator | Field Expert | Founding Reviewer
    acted_on_count: int = 0               # how many submissions were acted on by a lab
    governance_votes_cast: int = 0


class ContributionMetadata(BaseModel):
    """Extra metadata depending on contribution type."""
    # donated_compute
    gpu_hours: Optional[float] = None
    compute_type: Optional[str] = None
    # prompt_library
    prompt_count: Optional[int] = None
    domain: Optional[str] = None
    similarity_score: Optional[float] = None
    # red_team_report
    vulnerabilities_found: Optional[int] = None
    severity_rating: Optional[str] = None
    # agent_workflow
    step_count: Optional[int] = None
    outcome_annotation: Optional[str] = None
    # open_source_connector
    connector_type: Optional[str] = None
    repo_url: Optional[str] = None
    # verified_referral
    referred_contributor_id: Optional[str] = None
    # human_feedback_session
    pair_count: Optional[int] = None
    session_consistency_score: Optional[float] = None
    # community_moderation
    moderation_actions: Optional[int] = None
    # general
    example_count: Optional[int] = None
    language: Optional[str] = None


class Contribution(BaseModel):
    id: str
    contributor_id: str
    type: ContributionType
    title: str
    description: str
    status: ContributionStatus = ContributionStatus.pending
    submitted_at: str
    completed_at: Optional[str] = None
    base_score: Optional[float] = None
    helpfulness_multiplier: Optional[float] = None
    tier_multiplier: Optional[float] = None
    reputation_modifier: Optional[float] = None
    final_score: Optional[float] = None
    validator_ids: List[str] = []
    flags: List[str] = []
    abuse_flags: List[str] = []
    metadata: Optional[ContributionMetadata] = None
    credit_equivalent: Optional[float] = None
    # Change 4 — Domain taxonomy + structured submission
    domain: Optional[str] = None
    submission_type: Optional[str] = None       # edge_case | error_report | blind_spot | domain_correction
    what_went_wrong: Optional[str] = None
    correct_answer: Optional[str] = None
    domain_qualification: Optional[str] = None
    credential_reference: Optional[str] = None
    verified_domain_expert: bool = False
    # Change 5 — Acted-on signal
    acted_on: bool = False
    acted_on_at: Optional[str] = None


class ValidationRecord(BaseModel):
    id: str
    contribution_id: str
    validator_id: str
    decision: str  # "attest" | "flag" | "reject"
    confidence: float
    notes: str
    staked_credits: Optional[int] = None
    created_at: str


class Transaction(BaseModel):
    id: str
    contributor_id: str
    type: str  # "earn" | "redeem" | "decay" | "stake" | "stake_return" | "stake_bonus" | "stake_loss"
    amount: float
    points: Optional[int] = None
    contribution_id: Optional[str] = None
    validator_ids: Optional[List[str]] = None
    helpfulness_multiplier: Optional[float] = None
    tier_multiplier: Optional[float] = None
    reputation_modifier: Optional[float] = None
    credit_equivalent: Optional[float] = None
    description: str
    created_at: str


class Stake(BaseModel):
    id: str
    contributor_id: str
    contribution_id: str
    amount: int
    status: str = "pending"  # "pending" | "upheld" | "overturned"
    created_at: str
    resolved_at: Optional[str] = None


# ─── Governance Models ────────────────────────────────────────────────────────

class GovernanceProposal(BaseModel):
    id: str
    proposer_id: str
    type: GovernanceProposalType
    title: str
    description: str
    affected_parameter: str
    proposed_change: str
    status: ProposalStatus = ProposalStatus.active
    community_votes_for: int = 0
    community_votes_against: int = 0
    council_votes_for: int = 0
    council_votes_against: int = 0
    veto_reason: Optional[str] = None
    created_at: str
    resolved_at: Optional[str] = None


class GovernanceVote(BaseModel):
    id: str
    proposal_id: str
    voter_id: str
    chamber: str  # "community" | "council"
    vote: str  # "for" | "against"
    weight: int
    created_at: str


class GovernanceDispute(BaseModel):
    id: str
    appellant_id: str
    contribution_id: str
    reason: str
    status: DisputeStatus = DisputeStatus.submitted
    panel_ids: List[str] = []
    decision: Optional[str] = None
    decision_notes: Optional[str] = None
    created_at: str
    decided_at: Optional[str] = None


# ─── Trust Score ──────────────────────────────────────────────────────────────

class TrustScoreBreakdown(BaseModel):
    total: float
    validation_accuracy: float
    vouch_chain_depth: float
    contribution_diversity: float
    tenure: float
    governance_participation: float
    stake_history: float
    # Raw inputs
    raw_accuracy: float
    raw_vouch_depth: int
    raw_distinct_types: int
    raw_tenure_months: float
    raw_governance_pct: float
    raw_stake_ratio: float


# ─── Compliance ───────────────────────────────────────────────────────────────

class ComplianceStatus(BaseModel):
    contributor_id: str
    terms_accepted: bool
    terms_version: str
    last_accepted_date: Optional[str]
    transfer_attempts: int
    compliance_flags: List[str]
    is_compliant: bool


# ─── Exchange Rate ────────────────────────────────────────────────────────────

class ExchangeRate(BaseModel):
    points_per_dollar: int = 100
    dollar_per_point: float = 0.01
    helpfulness_multiplier_ceiling: float = 2.0
    inflation_guard: bool = False
    quarterly_issuance_current: int = 0
    quarterly_issuance_prior: int = 0
    note: str = ""
