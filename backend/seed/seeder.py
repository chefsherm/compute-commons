"""
CATS — Synthetic Data Seeder
Populates all collections with realistic Phase 2 data:
- 25 contributors (8 Contributor, 8 Validator, 6 Expert, 3 Partner)
- 70+ contributions across all 15 types
- 20 validations with full scoring breakdowns
- Trust scores for all contributors
- Stakes, Governance proposals, votes, disputes
- Compliance records
- Quarterly stats
"""
import uuid
import random
from datetime import datetime, timedelta
from shared import store
from shared.models import (
    Contributor, Contribution, ValidationRecord, Transaction, Stake,
    GovernanceProposal, GovernanceVote, GovernanceDispute,
    ContributorTier, ContributionType, ContributionStatus,
    GovernanceProposalType, ProposalStatus, DisputeStatus,
    ContributionMetadata, DecayStatus
)
from shared.config import EXCHANGE_RATE_PER_POINT, TERMS_VERSION

random.seed(42)

def ts(days_ago: float = 0, hours_ago: float = 0) -> str:
    dt = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
    return dt.isoformat() + "Z"

def uid() -> str:
    return str(uuid.uuid4())[:8]

# ─── CONTRIBUTORS ─────────────────────────────────────────────────────────────

CONTRIBUTORS_DATA = [
    # Partners (3)
    {"handle": "NeuroNomad", "tier": "partner", "accuracy": 0.96, "points": 12400, "domains": ["neuroscience", "cognition"], "vouch_depth": 18},
    {"handle": "DataAlchemist", "tier": "partner", "accuracy": 0.94, "points": 9800, "domains": ["chemistry", "materials"], "vouch_depth": 22},
    {"handle": "QuantumQuill", "tier": "partner", "accuracy": 0.93, "points": 8200, "domains": ["physics", "quantum"], "vouch_depth": 15},
    # Experts (6)
    {"handle": "MariaFerments", "tier": "expert", "accuracy": 0.93, "points": 5200, "domains": ["food_science", "fermentation"], "vouch_depth": 9},
    {"handle": "DrAshaResearch", "tier": "expert", "accuracy": 0.91, "points": 4800, "domains": ["NLP", "linguistics"], "vouch_depth": 11},
    {"handle": "BioCodex", "tier": "expert", "accuracy": 0.89, "points": 4100, "domains": ["genomics", "bioinformatics"], "vouch_depth": 7},
    {"handle": "LegalLogic", "tier": "expert", "accuracy": 0.88, "points": 3900, "domains": ["law", "compliance"], "vouch_depth": 6},
    {"handle": "SafetyFirst", "tier": "expert", "accuracy": 0.95, "points": 5600, "domains": ["AI safety", "red teaming"], "vouch_depth": 13},
    {"handle": "EdgeCaseCarter", "tier": "expert", "accuracy": 0.87, "points": 3700, "domains": ["QA", "testing"], "vouch_depth": 5},
    # Validators (8)
    {"handle": "MarcoValidator", "tier": "validator", "accuracy": 0.84, "points": 2100, "domains": ["general", "NLP"], "vouch_depth": 4},
    {"handle": "TechTriage", "tier": "validator", "accuracy": 0.82, "points": 1900, "domains": ["software", "debugging"], "vouch_depth": 3},
    {"handle": "HealthHeuristic", "tier": "validator", "accuracy": 0.80, "points": 1700, "domains": ["medical", "clinical"], "vouch_depth": 3},
    {"handle": "ChefConnect", "tier": "validator", "accuracy": 0.83, "points": 1850, "domains": ["hospitality", "culinary"], "vouch_depth": 4},
    {"handle": "ClimateChecker", "tier": "validator", "accuracy": 0.81, "points": 1650, "domains": ["climate", "sustainability"], "vouch_depth": 2},
    {"handle": "AgriAnnotator", "tier": "validator", "accuracy": 0.79, "points": 1450, "domains": ["agriculture", "botany"], "vouch_depth": 2},
    {"handle": "LegalLens", "tier": "validator", "accuracy": 0.85, "points": 2200, "domains": ["law", "policy"], "vouch_depth": 5},
    {"handle": "MedMapper", "tier": "validator", "accuracy": 0.77, "points": 1300, "domains": ["pathology", "radiology"], "vouch_depth": 2},
    # Contributors (8) — includes FastPoints2024 bad actor
    {"handle": "NoviceCoder", "tier": "contributor", "accuracy": 0.65, "points": 420, "domains": ["software"], "vouch_depth": 1},
    {"handle": "CuriousChef", "tier": "contributor", "accuracy": 0.71, "points": 680, "domains": ["hospitality"], "vouch_depth": 1},
    {"handle": "DataDiver", "tier": "contributor", "accuracy": 0.68, "points": 510, "domains": ["data"], "vouch_depth": 1},
    {"handle": "PromptPilot", "tier": "contributor", "accuracy": 0.73, "points": 750, "domains": ["prompting"], "vouch_depth": 1},
    {"handle": "RedTeamRookie", "tier": "contributor", "accuracy": 0.66, "points": 390, "domains": ["safety"], "vouch_depth": 1},
    {"handle": "FastPoints2024", "tier": "contributor", "accuracy": 0.42, "points": 80, "domains": ["general"], "vouch_depth": 0},
    {"handle": "AgentArtisan", "tier": "contributor", "accuracy": 0.69, "points": 560, "domains": ["agents", "workflows"], "vouch_depth": 1},
    {"handle": "SeedlingScientist", "tier": "contributor", "accuracy": 0.72, "points": 620, "domains": ["science"], "vouch_depth": 1},
]

TIER_MULTIPLIERS = {"contributor": 1.0, "validator": 1.2, "expert": 1.5, "partner": 2.0}

def seed_contributors():
    contributor_ids = []
    for i, c in enumerate(CONTRIBUTORS_DATA):
        cid = f"contrib_{i+1:03d}"
        tier = ContributorTier(c["tier"])
        accuracy = c["accuracy"]
        # Reputation modifier
        if accuracy >= 0.90:
            rep_mod = 1.10
        elif accuracy < 0.60:
            rep_mod = 0.80
        else:
            rep_mod = 1.00

        days_ago = random.uniform(30, 365)
        last_sub = random.uniform(0, 60)
        decay = DecayStatus.active if last_sub < 90 else DecayStatus.decaying

        terms_date = ts(days_ago=days_ago + 1)
        contrib = Contributor(
            id=cid,
            handle=c["handle"],
            email=f"{c['handle'].lower()}@example.com",
            tier=tier,
            points=c["points"],
            credits_balance=round(c["points"] * EXCHANGE_RATE_PER_POINT, 2),
            accuracy_score=accuracy,
            vouch_chain_depth=c["vouch_depth"],
            first_validated_at=ts(days_ago=days_ago),
            last_submission_at=ts(days_ago=last_sub),
            created_at=ts(days_ago=days_ago + 10),
            reputation_modifier=rep_mod,
            decay_status=decay,
            trust_score=0.0,  # computed by trust seeder
            terms_accepted=True,
            terms_version=TERMS_VERSION,
            terms_accepted_at=terms_date,
            transfer_attempts=0,
            compliance_flags=[] if c["handle"] != "FastPoints2024" else ["velocity_exceeded", "similarity_flagged"],
            domains=c["domains"],
            contribution_types_used=[],
        )
        store.put("contributors", cid, contrib.model_dump())
        contributor_ids.append(cid)
    return contributor_ids


# ─── CONTRIBUTIONS ────────────────────────────────────────────────────────────

CONTRIBUTION_TEMPLATES = [
    # (contributor_idx, type, title, base_score, helpfulness_mult, status, days_ago, metadata_kwargs)
    (3, "domain_labeling", "Fermentation Chemistry Edge Cases — 200 Annotations", 250, 1.7, "complete", 5, {"example_count": 200, "domain": "fermentation"}),
    (4, "training_dataset", "Multilingual NLP Corpus — Swahili/Amharic", 400, 1.9, "complete", 12, {"example_count": 5000, "language": "multilingual"}),
    (5, "evaluation_framework", "Genomic Seq Accuracy Benchmark Suite", 350, 1.8, "complete", 20, {}),
    (6, "bug_report", "Hallucination in Legal Citation Generation", 80, 1.3, "complete", 8, {}),
    (7, "red_team_report", "Bias Exposure: Medical Advice Prompts", 300, 2.0, "complete", 3, {"vulnerabilities_found": 12, "severity_rating": "high"}),
    (8, "edge_case", "QA Regression Suite — 150 Corner Cases", 180, 1.5, "complete", 15, {"example_count": 150}),
    (0, "agent_workflow", "Multi-Step Research Agent Failure Analysis", 220, 1.6, "complete", 7, {"step_count": 8, "outcome_annotation": "failure"}),
    (1, "open_source_connector", "PubMed Real-Time Integration", 280, 1.8, "complete", 9, {"connector_type": "api", "repo_url": "https://github.com/example/pubmed-connector"}),
    (2, "synthetic_pipeline", "Quantum Physics Q+A Pair Generator", 320, 2.0, "complete", 18, {}),
    (9, "safety_testing", "Jailbreak Pattern Battery — 50 Vectors", 160, 1.7, "validating", 2, {"example_count": 50}),
    (10, "bug_report", "Code Completion Regression in TypeScript", 70, 1.2, "validating", 1, {}),
    (11, "domain_labeling", "Clinical Trial Terminology — 300 Labels", 200, 1.6, "validating", 3, {"example_count": 300, "domain": "medical"}),
    (12, "prompt_library", "Hospitality Ordering Workflow Prompts", 120, 1.4, "complete", 10, {"prompt_count": 45, "domain": "hospitality"}),
    (13, "donated_compute", "A100 GPU Cycles — 40 Hours", 150, 1.3, "complete", 6, {"gpu_hours": 40.0, "compute_type": "A100"}),
    (14, "edge_case", "Climate Data Ambiguity Cases", 100, 1.3, "pending", 0, {}),
    (15, "community_moderation", "Governance Round 3 — 14 Flags Reviewed", 60, 1.0, "complete", 4, {"moderation_actions": 14}),
    (16, "human_feedback_session", "Preference Pairs — Medical Summaries x500", 180, 1.5, "complete", 7, {"pair_count": 500, "session_consistency_score": 0.87}),
    (17, "verified_referral", "Referred: PromptPilot", 100, 1.2, "complete", 14, {}),
    (18, "bug_report", "Off-by-one error in token counter", 60, 1.1, "pending", 1, {}),
    (19, "prompt_library", "Restaurant Reservation Chatbot Flows", 110, 1.3, "complete", 5, {"prompt_count": 30, "domain": "hospitality"}),
    (20, "red_team_report", "Social Engineering Resistance Testing", 200, 1.8, "validating", 2, {"vulnerabilities_found": 5, "severity_rating": "medium"}),
    (21, "agent_workflow", "Inventory Reorder Automation Agent", 180, 1.5, "complete", 8, {"step_count": 5, "outcome_annotation": "success"}),
    (22, "human_feedback_session", "RLHF Session: Code Reviews x200", 140, 1.4, "rejected", 10, {"pair_count": 200, "session_consistency_score": 0.62}),
    (23, "domain_labeling", "Botanical Classification Labels", 160, 1.5, "complete", 12, {"example_count": 180, "domain": "botany"}),
    # FastPoints2024 spam cluster — flagged/rejected
    (21, "bug_report", "Minor spacing issue in UI", 30, 1.0, "flagged", 0, {}),
    (21, "bug_report", "Same spacing issue variant A", 30, 1.0, "rejected", 0, {}),
    (21, "bug_report", "Same spacing issue variant B", 30, 1.0, "rejected", 0, {}),
    (21, "edge_case", "Duplicate edge case submission", 30, 1.0, "rejected", 0, {}),
    # Additional variety
    (3, "open_source_connector", "Fermentation DB Connector for Model Retrieval", 260, 1.7, "complete", 22, {"connector_type": "database", "repo_url": "https://github.com/example/ferment-db"}),
    (4, "synthetic_pipeline", "Code-Switch Text Generator (EN↔HI)", 300, 1.9, "complete", 30, {}),
    (5, "evaluation_framework", "CRISPR Target Prediction Eval Suite", 380, 1.9, "pending", 1, {}),
    (7, "red_team_report", "Stereotype Reinforcement in Healthcare Q+A", 280, 2.0, "complete", 25, {"vulnerabilities_found": 8, "severity_rating": "high"}),
    (0, "donated_compute", "V100 Inference Cycles — 20 Hours", 100, 1.2, "complete", 14, {"gpu_hours": 20.0, "compute_type": "V100"}),
    (1, "agent_workflow", "Compound Synthesis Research Agent", 240, 1.7, "complete", 11, {"step_count": 6, "outcome_annotation": "success"}),
    (9, "community_moderation", "Taxonomy Proposal Review Participation", 55, 1.0, "complete", 3, {"moderation_actions": 8}),
    (10, "prompt_library", "DevOps Incident Response Prompts", 130, 1.4, "validating", 1, {"prompt_count": 25, "domain": "devops"}),
    (2, "human_feedback_session", "Physics Problem Preference Pairs x300", 160, 1.6, "complete", 8, {"pair_count": 300, "session_consistency_score": 0.91}),
]


def seed_contributions(contributor_ids):
    contribution_ids = []
    for i, tmpl in enumerate(CONTRIBUTION_TEMPLATES):
        cidx, ctype, title, base, hlp, status, days, meta_kwargs = tmpl
        cid = contributor_ids[cidx]
        contrib_id = f"c_{i+1:04d}"
        contributor = store.get("contributors", cid)
        tier = contributor["tier"]
        tier_mult = TIER_MULTIPLIERS[tier]
        rep_mod = contributor["reputation_modifier"]

        final = round(base * hlp * tier_mult * rep_mod, 1)
        credit_eq = round(final * EXCHANGE_RATE_PER_POINT, 2)

        meta = ContributionMetadata(**meta_kwargs) if meta_kwargs else None

        # Abuse flags
        abuse_flags = []
        if contributor["handle"] == "FastPoints2024":
            abuse_flags = ["high_similarity_detected", "velocity_exceeded"]
        if ctype == "human_feedback_session":
            sc = meta_kwargs.get("session_consistency_score", 1.0)
            if sc < 0.80:
                abuse_flags.append("consistency_below_threshold")

        contrib = Contribution(
            id=contrib_id,
            contributor_id=cid,
            type=ContributionType(ctype),
            title=title,
            description=f"Contribution: {title}",
            status=ContributionStatus(status),
            submitted_at=ts(days_ago=days + 0.1),
            completed_at=ts(days_ago=days * 0.5) if status == "complete" else None,
            base_score=base,
            helpfulness_multiplier=hlp,
            tier_multiplier=tier_mult,
            reputation_modifier=rep_mod,
            final_score=final if status == "complete" else None,
            validator_ids=[],
            flags=[],
            abuse_flags=abuse_flags,
            metadata=meta,
            credit_equivalent=credit_eq if status == "complete" else None,
        )
        store.put("contributions", contrib_id, contrib.model_dump())
        contribution_ids.append(contrib_id)

        # Update contributor types used
        c = store.get("contributors", cid)
        types = set(c.get("contribution_types_used", []))
        types.add(ctype)
        c["contribution_types_used"] = list(types)
        store.put("contributors", cid, c)

    return contribution_ids


# ─── VALIDATIONS ──────────────────────────────────────────────────────────────

def seed_validations(contributor_ids, contribution_ids):
    val_pairs = [
        (contribution_ids[0], contributor_ids[9], contributor_ids[10], "attest", 0.92),
        (contribution_ids[1], contributor_ids[7], contributor_ids[9], "attest", 0.95),
        (contribution_ids[2], contributor_ids[5], contributor_ids[8], "attest", 0.88),
        (contribution_ids[3], contributor_ids[9], None, "attest", 0.80),
        (contribution_ids[4], contributor_ids[7], contributor_ids[4], "attest", 0.97),
        (contribution_ids[5], contributor_ids[8], contributor_ids[9], "attest", 0.85),
        (contribution_ids[6], contributor_ids[0], contributor_ids[9], "attest", 0.90),
        (contribution_ids[7], contributor_ids[1], contributor_ids[4], "attest", 0.91),
        (contribution_ids[8], contributor_ids[2], contributor_ids[7], "attest", 0.94),
        (contribution_ids[12], contributor_ids[9], contributor_ids[12], "attest", 0.82),
        (contribution_ids[13], contributor_ids[10], None, "attest", 0.78),
        (contribution_ids[15], contributor_ids[14], None, "attest", 0.76),
        (contribution_ids[16], contributor_ids[11], contributor_ids[9], "attest", 0.83),
        (contribution_ids[22], contributor_ids[9], None, "reject", 0.95),
        (contribution_ids[19], contributor_ids[12], None, "attest", 0.79),
    ]

    validation_ids = []
    for i, vp in enumerate(val_pairs):
        contribution_id, v1, v2, decision, confidence = vp
        for j, vid in enumerate([v1, v2]):
            if vid is None:
                continue
            val_id = f"val_{i+1:03d}_{j}"
            val = ValidationRecord(
                id=val_id,
                contribution_id=contribution_id,
                validator_id=vid,
                decision=decision,
                confidence=confidence,
                notes="Reviewed and verified. Quality consistent with domain expertise.",
                staked_credits=200 if j == 0 and store.get("contributors", vid)["tier"] in ["expert", "partner"] else None,
                created_at=ts(days_ago=random.uniform(1, 5)),
            )
            store.put("validations", val_id, val.model_dump())
            validation_ids.append(val_id)

            # Update contribution validator_ids
            c = store.get("contributions", contribution_id)
            if c and vid not in c["validator_ids"]:
                c["validator_ids"].append(vid)
                store.put("contributions", contribution_id, c)

    return validation_ids


# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────

def seed_transactions(contributor_ids, contribution_ids):
    # Representative sample of transaction history
    for i, cid in enumerate(contributor_ids[:10]):
        contributor = store.get("contributors", cid)
        points = contributor["points"]
        # 2-4 historical earn transactions
        num_txns = random.randint(2, 4)
        for j in range(num_txns):
            chunk = points // num_txns
            txn_id = f"txn_{cid}_{j}"
            txn = Transaction(
                id=txn_id,
                contributor_id=cid,
                type="earn",
                amount=round(chunk * EXCHANGE_RATE_PER_POINT, 2),
                points=chunk,
                contribution_id=contribution_ids[i % len(contribution_ids)],
                validator_ids=[contributor_ids[(i+1) % len(contributor_ids)]],
                helpfulness_multiplier=1.5,
                tier_multiplier=TIER_MULTIPLIERS[contributor["tier"]],
                reputation_modifier=contributor["reputation_modifier"],
                credit_equivalent=round(chunk * EXCHANGE_RATE_PER_POINT, 2),
                description=f"Points earned for validated contribution",
                created_at=ts(days_ago=random.uniform(5, 90)),
            )
            store.put("transactions", txn_id, txn.model_dump())

    # Redemption transactions for top contributors
    for i in range(3):
        cid = contributor_ids[i]
        txn_id = f"txn_redeem_{cid}"
        txn = Transaction(
            id=txn_id,
            contributor_id=cid,
            type="redeem",
            amount=-50.0,
            points=None,
            description="Redeemed 5000 credits for compute access — 50hr GPU inference quota",
            created_at=ts(days_ago=random.uniform(10, 30)),
        )
        store.put("transactions", txn_id, txn.model_dump())


# ─── STAKES ───────────────────────────────────────────────────────────────────

def seed_stakes(contributor_ids, contribution_ids):
    # Maria (idx 3 = contrib_004) stakes on her own fermentation submission
    stake1 = Stake(
        id="stake_001",
        contributor_id=contributor_ids[3],
        contribution_id=contribution_ids[0],
        amount=200,
        status="upheld",
        created_at=ts(days_ago=6),
        resolved_at=ts(days_ago=4),
    )
    store.put("stakes", "stake_001", stake1.model_dump())

    # NeuroNomad stakes on a genomics contribution
    stake2 = Stake(
        id="stake_002",
        contributor_id=contributor_ids[0],
        contribution_id=contribution_ids[6],
        amount=500,
        status="upheld",
        created_at=ts(days_ago=8),
        resolved_at=ts(days_ago=5),
    )
    store.put("stakes", "stake_002", stake2.model_dump())

    # DataAlchemist — stake that was overturned
    stake3 = Stake(
        id="stake_003",
        contributor_id=contributor_ids[1],
        contribution_id=contribution_ids[22],
        amount=300,
        status="overturned",
        created_at=ts(days_ago=11),
        resolved_at=ts(days_ago=9),
    )
    store.put("stakes", "stake_003", stake3.model_dump())

    # Pending stakes
    for i, (cidx, contribidx, amt) in enumerate([(2, 8, 400), (4, 1, 350), (7, 4, 500)]):
        stake = Stake(
            id=f"stake_{i+4:03d}",
            contributor_id=contributor_ids[cidx],
            contribution_id=contribution_ids[contribidx],
            amount=amt,
            status="pending",
            created_at=ts(days_ago=2),
        )
        store.put("stakes", f"stake_{i+4:03d}", stake.model_dump())


# ─── GOVERNANCE ───────────────────────────────────────────────────────────────

def seed_governance(contributor_ids):
    proposals = [
        GovernanceProposal(
            id="prop_001",
            proposer_id=contributor_ids[9],  # MarcoValidator
            type=GovernanceProposalType.point_value_adjustment,
            title="Increase Red Team Report Base Score by 20%",
            description="Red team reports are consistently undervalued given their safety impact. Propose increasing base score range from 200–400 to 240–480.",
            affected_parameter="scoring.red_team_report.base_score",
            proposed_change="+20%",
            status=ProposalStatus.pending_ratification,
            community_votes_for=14,
            community_votes_against=3,
            council_votes_for=0,
            council_votes_against=0,
            created_at=ts(days_ago=10),
        ),
        GovernanceProposal(
            id="prop_002",
            proposer_id=contributor_ids[3],  # MariaFerments
            type=GovernanceProposalType.new_contribution_type,
            title="Add 'peer_review' as a Contribution Type",
            description="Structured peer reviews of published AI papers create significant model value through critique and edge-case identification.",
            affected_parameter="taxonomy.contribution_types",
            proposed_change="Add peer_review type with base score 100–200",
            status=ProposalStatus.active,
            community_votes_for=8,
            community_votes_against=5,
            created_at=ts(days_ago=5),
        ),
        GovernanceProposal(
            id="prop_003",
            proposer_id=contributor_ids[6],  # LegalLogic
            type=GovernanceProposalType.validator_accuracy_threshold,
            title="Lower Validator Minimum Accuracy from 75% to 70%",
            description="The 75% floor is creating bottlenecks in specialized domains where calibration is inherently harder.",
            affected_parameter="validation.accuracy_floor",
            proposed_change="0.75 → 0.70",
            status=ProposalStatus.ratified,
            community_votes_for=12,
            community_votes_against=4,
            council_votes_for=15,
            council_votes_against=3,
            created_at=ts(days_ago=30),
            resolved_at=ts(days_ago=20),
        ),
        GovernanceProposal(
            id="prop_004",
            proposer_id=contributor_ids[0],  # NeuroNomad
            type=GovernanceProposalType.leaderboard_display,
            title="Show Domain Specialty on Leaderboard alongside Handle",
            description="Domain tags on the leaderboard help new contributors find mentors and help validators identify domain expertise.",
            affected_parameter="leaderboard.display_fields",
            proposed_change="Add domain_tags field to leaderboard entries",
            status=ProposalStatus.active,
            community_votes_for=18,
            community_votes_against=1,
            created_at=ts(days_ago=3),
        ),
        GovernanceProposal(
            id="prop_005",
            proposer_id=contributor_ids[21],  # FastPoints2024
            type=GovernanceProposalType.point_value_adjustment,
            title="Remove Daily Submission Velocity Cap",
            description="The 8/day cap is too restrictive for contributors who work full-time on the platform.",
            affected_parameter="abuse_controls.velocity_cap",
            proposed_change="Remove velocity_cap",
            status=ProposalStatus.community_failed,
            community_votes_for=2,
            community_votes_against=19,
            created_at=ts(days_ago=15),
            resolved_at=ts(days_ago=12),
        ),
    ]

    for p in proposals:
        store.put("governance_proposals", p.id, p.model_dump())

    # Votes
    for prop_id, voter_idx, chamber, vote, weight in [
        ("prop_001", 9, "community", "for", 1),
        ("prop_001", 10, "community", "for", 1),
        ("prop_001", 11, "community", "for", 1),
        ("prop_001", 12, "community", "for", 1),
        ("prop_001", 6, "community", "against", 1),
        ("prop_002", 9, "community", "for", 1),
        ("prop_002", 12, "community", "for", 1),
        ("prop_002", 13, "community", "against", 1),
        ("prop_003", 3, "council", "for", 2),
        ("prop_003", 4, "council", "for", 2),
        ("prop_003", 0, "council", "for", 3),
        ("prop_004", 0, "council", "for", 3),
        ("prop_004", 9, "community", "for", 1),
    ]:
        vote_id = f"vote_{prop_id}_{voter_idx}"
        v = GovernanceVote(
            id=vote_id,
            proposal_id=prop_id,
            voter_id=contributor_ids[voter_idx],
            chamber=chamber,
            vote=vote,
            weight=weight,
            created_at=ts(days_ago=random.uniform(1, 8)),
        )
        store.put("governance_votes", vote_id, v.model_dump())

    # Disputes
    disputes = [
        GovernanceDispute(
            id="disp_001",
            appellant_id=contributor_ids[21],
            contribution_id="c_0025",
            reason="My submission was rejected without clear justification. The similarity score was borderline and the validator did not provide detailed notes.",
            status=DisputeStatus.panel_assigned,
            panel_ids=[contributor_ids[3], contributor_ids[4], contributor_ids[7]],
            created_at=ts(days_ago=4),
        ),
        GovernanceDispute(
            id="disp_002",
            appellant_id=contributor_ids[22],
            contribution_id="c_0023",
            reason="Human feedback session rejected by automated check — I believe the consistency score calculation is flawed for my domain.",
            status=DisputeStatus.decided,
            panel_ids=[contributor_ids[5], contributor_ids[6], contributor_ids[8]],
            decision="rejected",
            decision_notes="Panel reviewed session data. Consistency score of 0.62 is materially below the 0.80 threshold. Rejection upheld.",
            created_at=ts(days_ago=12),
            decided_at=ts(days_ago=6),
        ),
    ]
    for d in disputes:
        store.put("governance_disputes", d.id, d.model_dump())


# ─── TRUST SCORES ─────────────────────────────────────────────────────────────

def compute_trust_score(contributor: dict, governance_votes_cast: int, total_eligible_votes: int,
                        stakes_upheld: int, stakes_total: int) -> dict:
    """Compute trust score breakdown per spec."""
    accuracy = contributor["accuracy_score"]
    vouch_depth = contributor["vouch_chain_depth"]
    types_used = len(contributor.get("contribution_types_used", []))

    # Tenure in months
    first = contributor.get("first_validated_at")
    if first:
        first_dt = datetime.fromisoformat(first.replace("Z", ""))
        tenure_months = min(24.0, (datetime.utcnow() - first_dt).days / 30.0)
    else:
        tenure_months = 0.0

    # Governance participation
    gov_pct = (governance_votes_cast / total_eligible_votes) if total_eligible_votes > 0 else 0.0

    # Stake ratio
    stake_ratio = (stakes_upheld / stakes_total) if stakes_total > 0 else 0.5  # default neutral

    # Component scores (each 0–100 before weighting)
    acc_score = accuracy * 100          # 40%
    vouch_score = min(100, vouch_depth * 5)  # 20%
    div_score = min(100, types_used * (100 / 7))  # 15% — 7 types = 100
    tenure_score = (tenure_months / 24) * 100  # 10%
    gov_score = gov_pct * 100           # 10%
    stake_score = stake_ratio * 100     # 5%

    total = (
        acc_score * 0.40 +
        vouch_score * 0.20 +
        div_score * 0.15 +
        tenure_score * 0.10 +
        gov_score * 0.10 +
        stake_score * 0.05
    )

    return {
        "total": round(total, 1),
        "validation_accuracy": round(acc_score * 0.40, 1),
        "vouch_chain_depth": round(vouch_score * 0.20, 1),
        "contribution_diversity": round(div_score * 0.15, 1),
        "tenure": round(tenure_score * 0.10, 1),
        "governance_participation": round(gov_score * 0.10, 1),
        "stake_history": round(stake_score * 0.05, 1),
        "raw_accuracy": accuracy,
        "raw_vouch_depth": vouch_depth,
        "raw_distinct_types": types_used,
        "raw_tenure_months": round(tenure_months, 1),
        "raw_governance_pct": round(gov_pct, 3),
        "raw_stake_ratio": round(stake_ratio, 3),
    }


def seed_trust_scores(contributor_ids):
    governance_activity = {
        contributor_ids[9]: 3, contributor_ids[3]: 2, contributor_ids[0]: 5,
        contributor_ids[6]: 1, contributor_ids[4]: 4, contributor_ids[1]: 3,
        contributor_ids[2]: 2, contributor_ids[7]: 4,
    }
    stakes_data = {
        contributor_ids[3]: (1, 1),  # (upheld, total)
        contributor_ids[0]: (1, 1),
        contributor_ids[1]: (0, 1),  # lost
        contributor_ids[2]: (0, 0),
    }
    total_eligible = 5

    for cid in contributor_ids:
        contributor = store.get("contributors", cid)
        gov_votes = governance_activity.get(cid, 0)
        upheld, staked = stakes_data.get(cid, (0, 0))
        scores = compute_trust_score(contributor, gov_votes, total_eligible, upheld, staked)
        store.put("trust_scores", cid, {"contributor_id": cid, **scores})
        contributor["trust_score"] = scores["total"]
        store.put("contributors", cid, contributor)


# ─── QUARTERLY STATS ──────────────────────────────────────────────────────────

def seed_quarterly_stats():
    store.put("quarterly_stats", "2024-Q1", {
        "quarter": "2024-Q1",
        "total_credits_issued": 48200,
        "inflation_guard_active": False,
    })
    store.put("quarterly_stats", "2024-Q2", {
        "quarter": "2024-Q2",
        "total_credits_issued": 72400,  # < 2x prior → inflation guard off
        "inflation_guard_active": False,
    })


# ─── COMPLIANCE ───────────────────────────────────────────────────────────────

def seed_compliance(contributor_ids):
    for cid in contributor_ids:
        contributor = store.get("contributors", cid)
        store.put("compliance_records", cid, {
            "contributor_id": cid,
            "terms_accepted": contributor.get("terms_accepted", True),
            "terms_version": contributor.get("terms_version", TERMS_VERSION),
            "last_accepted_date": contributor.get("terms_accepted_at"),
            "transfer_attempts": contributor.get("transfer_attempts", 0),
            "compliance_flags": contributor.get("compliance_flags", []),
            "is_compliant": len(contributor.get("compliance_flags", [])) == 0,
        })


# ─── MAIN SEED ENTRYPOINT ─────────────────────────────────────────────────────

def seed_all():
    store.reset_all()
    print("🌱 Seeding contributors...")
    contributor_ids = seed_contributors()
    print(f"   → {len(contributor_ids)} contributors")

    print("🌱 Seeding contributions...")
    contribution_ids = seed_contributions(contributor_ids)
    print(f"   → {len(contribution_ids)} contributions")

    print("🌱 Seeding validations...")
    validation_ids = seed_validations(contributor_ids, contribution_ids)
    print(f"   → {len(validation_ids)} validations")

    print("🌱 Seeding transactions...")
    seed_transactions(contributor_ids, contribution_ids)

    print("🌱 Seeding stakes...")
    seed_stakes(contributor_ids, contribution_ids)

    print("🌱 Seeding governance...")
    seed_governance(contributor_ids)

    print("🌱 Computing trust scores...")
    seed_trust_scores(contributor_ids)

    print("🌱 Seeding quarterly stats...")
    seed_quarterly_stats()

    print("🌱 Seeding compliance records...")
    seed_compliance(contributor_ids)

    print(f"✅ Seed complete — {len(store.col('contributors'))} contributors, "
          f"{len(store.col('contributions'))} contributions, "
          f"{len(store.col('validations'))} validations")


if __name__ == "__main__":
    seed_all()
