# Compute Commons (CATS) — Phase 2

> **Compute Commons** is an open contribution-to-access network where verified model improvements earn redeemable AI compute credits. Peer governance, trust-chain validation, and a fixed-floor credit economy replace the pay-to-play dynamic that locks smaller organizations out of frontier AI.
>
> *Internal system name: CATS (Contribution-to-Access System)*

---

## Quick Start

```bash
# Install backend deps
cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Start backend (auto-seeds synthetic data)
cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000

# Install and start frontend
cd frontend && npm install && npm run dev
```

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Frontend:** http://localhost:3001

---

## Phase 2 Architecture

```
cats/
├── backend/
│   ├── main.py                   # FastAPI app — mounts all 7 routers
│   ├── shared/
│   │   ├── config.py             # All constants (decay, inflation, staking, etc.)
│   │   ├── store.py              # In-memory data store (simulates Firestore)
│   │   └── models.py             # All Pydantic models (Phase 1 + Phase 2)
│   ├── intake/router.py          # 15 contribution types + abuse detection
│   ├── scoring/router.py         # Scoring engine + inflation guard
│   ├── validation/router.py      # Validation queue + staking + vouch chain
│   ├── ledger/router.py          # Credits + compliance + decay job
│   ├── governance/router.py      # Bicameral governance + charter + disputes
│   ├── trust/router.py           # Trust Score engine + fraud detection
│   ├── meta/router.py            # Brand metadata endpoint
│   └── seed/seeder.py            # 25 contributors, 37 contributions, full Phase 2 data
├── frontend/src/app/
│   ├── page.tsx                  # Homepage — pulls from /api/meta/brand
│   ├── dashboard/contributor/    # Points, credits, decay status, Maria fixture
│   ├── dashboard/validator/      # Queue, attest/reject, staking, collusion detection
│   ├── dashboard/governance/     # Bicameral proposals, votes, disputes, charter
│   ├── dashboard/trust/          # Trust score breakdown, fraud detection panel
│   └── leaderboard/             # Top 50, filters, exchange rate status
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Contribution Taxonomy (15 Types)

### Phase 1 (Original 7)
| Type | Base Score | Value Driver |
|---|---|---|
| `bug_report` | 50–150 | Hallucination/error identification |
| `edge_case` | 80–200 | Robustness probing |
| `safety_testing` | 100–250 | Alignment signal |
| `domain_labeling` | 100–400 | Rare domain coverage |
| `training_dataset` | 200–600 | Direct training signal |
| `evaluation_framework` | 200–500 | Benchmark utility |
| `synthetic_pipeline` | 150–450 | Scalable data generation |

### Phase 2 (8 New Types)
| Type | Base Score | Gaming Risk | Key Controls |
|---|---|---|---|
| `donated_compute` | 50–300 | Low | 80 GPU-hr/day cap per contributor |
| `prompt_library` | 80–200 | Medium | Similarity threshold vs existing library |
| `red_team_report` | 200–500 | Low | 2× Expert validators; helpfulness floor 2.0 |
| `agent_workflow` | 120–300 | Medium | Minimum 3 steps + outcome annotation required |
| `open_source_connector` | 200–400 | Low | Expert-tier code review required |
| `verified_referral` | 80–150 | Medium | New contributor's first 3 subs — non-affiliated validators |
| `human_feedback_session` | 100–300 | High | Session consistency score ≥ 0.80 or auto-rejected |
| `community_moderation` | 30–100 | Low | Auto-verified by participation logs |

---

## Credit Economy (Phase 2)

### Issuance Formula
```
Final Points = Base × Helpfulness Multiplier × Tier Multiplier × Reputation Modifier
Credit Value = Final Points × $0.01
```

### Tier Multipliers
| Tier | Multiplier |
|---|---|
| Contributor | 1.0× |
| Validator | 1.2× |
| Expert | 1.5× |
| Partner | 2.0× |

### Reputation Modifiers
- Accuracy ≥ 90%: **+10% bonus**
- Accuracy < 60%: **-20% penalty**

### Maria Test Fixture
> *Maria is an Expert-tier food scientist with 93% accuracy.*
```
domain_labeling: 250 base × 1.7 helpfulness × 1.5 tier × 1.10 rep_mod
= 701 points = $7.01 compute credit

Staked 200 credits → upheld → +50 bonus
Final: 751 pts credited, decay clock reset
```

### Decay Policy
- Credits earned don't expire for **12 months from issuance**
- After 12 months of inactivity: **10% decay per quarter**
- Floor: **500 credits** (credits never drop below this)
- Exempt: any validated submission in the **last 90 days**

### Inflation Guard
- If quarterly issuance > 2× prior quarter → helpfulness ceiling drops **2.0 → 1.5**
- Published transparently at `GET /api/scoring/exchange-rate`

### Staking (No Crypto)
- Expert/Partner can stake up to **500 credits** behind a contribution they validate
- Upheld by governance audit → **+50 bonus credits**
- Overturned → **lose staked amount**
- Creates skin-in-the-game without financial instruments

---

## Governance Charter (Summary)

### Bicameral Structure
**Chamber One — Community Voice**
- Members: Validator tier and above
- Voting: 1 vote per person
- Pass threshold: Simple majority of active voters (voted in prior 90 days)
- Can propose: Taxonomy changes, point value adjustments, contributor disputes

**Chamber Two — Expert Council**
- Members: Expert and Partner tier
- Voting: Expert = 2 votes, Partner = 3 votes (weighted)
- Ratification threshold: 60% of weighted votes
- Role: Must ratify Community Voice proposals before they take effect

### What Can Be Governed
- Contribution taxonomy changes
- Point value adjustments (±20%)
- New contribution type proposals
- Validator accuracy thresholds
- Leaderboard display rules

### What Cannot Be Governed
- Exchange rate floor (legal protection)
- Anti-fraud and abuse controls
- Lab partner agreements
- Contributor personal data

### Sybil Protection
- Voting weight capped at tier ceiling regardless of points held
- New accounts cannot vote for **30 days** after first validated submission

### Dispute Resolution
1. Contributor submits appeal with reason
2. Panel of 3 Expert-tier validators (not affiliated with original decision)
3. 7-day window to render majority decision
4. Decision is final and logged publicly

### Core Team Veto
- Security, legal, and safety issues only
- All vetoes logged publicly with stated reason

---

## Trust Score

A composite 0–100 score computed for every contributor:

| Component | Weight | Description |
|---|---|---|
| Validation accuracy | 40% | Confirmed-correct rate across contributions and validations |
| Vouch chain depth | 20% | Validated contributors in downstream vouch chain |
| Contribution diversity | 15% | Distinct contribution types with passing validations |
| Tenure | 10% | Months since first validated submission (cap: 24) |
| Governance participation | 10% | Votes cast as % of eligible votes (prior 2 quarters) |
| Stake history | 5% | Ratio of stakes upheld to stakes lost |

### Access Restrictions
- **< 30**: Governance voting suspended
- **< 40**: Redemption capped at $200/month
- **≥ 70**: Priority validator assignment for high-value contributions

### Fraud Detection
| Check | Trigger | Action |
|---|---|---|
| Velocity | > 8 submissions in 24 hours | Auto-hold |
| Bot detection | Submission within 90s of account creation | Auto-reject |
| Text similarity | Cosine similarity > 0.75 between submissions within 30 days | Flag for review |
| Collusion | Same validator pair validates > 3 times in 30 days | Escalate to governance |

---

## Legal Rails

Credits are **not securities, not cash, not investments**.

1. **Non-transferable**: No peer-to-peer credit trading. All transfer attempts are logged and rejected.
2. **Compute access only**: Redemption is for GPU/CPU compute time only.
3. **No guaranteed value**: Exchange rate is set by the platform; adjustable with 30 days notice.
4. **No speculative value**: No interest, appreciation, or implied investment return.

Every redemption call runs `compliance_check()` validating:
- Contributor has accepted current terms version
- Redemption target is `compute_access`
- Trust score passes threshold
- Transfer flag is not set

---

## API Endpoints

### Intake
| Method | Path | Description |
|---|---|---|
| POST | `/api/intake/contributions/submit` | Submit a contribution (all 15 types) |
| GET | `/api/intake/contributions/{id}/status` | Check contribution status |
| GET | `/api/intake/contributions/contributor/{id}` | List all contributions by contributor |
| POST | `/api/intake/contributions/{id}/flag` | Flag a contribution |
| GET | `/api/intake/taxonomy` | Get full contribution type taxonomy |

### Scoring
| Method | Path | Description |
|---|---|---|
| POST | `/api/scoring/score/calculate` | Calculate score for a contribution |
| POST | `/api/scoring/score/award` | Award score and issue credits |
| GET | `/api/scoring/leaderboard` | Top contributors |
| GET | `/api/scoring/exchange-rate` | Current rate + inflation guard status |
| GET | `/api/scoring/stats` | Aggregate scoring statistics |

### Validation
| Method | Path | Description |
|---|---|---|
| GET | `/api/validation/queue/{validator_id}` | Get validation queue |
| POST | `/api/validation/validate/{contribution_id}` | Submit validation decision |
| GET | `/api/validation/validator/{id}/accuracy` | Accuracy scorecard |
| POST | `/api/validation/vouch` | Vouch for a contributor |
| POST | `/api/validation/stake/resolve` | Resolve a stake (upheld/overturned) |
| GET | `/api/validation/stakes` | List stakes |

### Credits Ledger
| Method | Path | Description |
|---|---|---|
| GET | `/api/ledger/balance/{contributor_id}` | Balance + decay + trust info |
| GET | `/api/ledger/transactions/{contributor_id}` | Transaction history |
| POST | `/api/ledger/redeem` | Redeem credits for compute access |
| POST | `/api/ledger/transfer` | Always rejects (non-transferable) |
| GET | `/api/ledger/compliance-status/{contributor_id}` | Compliance audit |
| POST | `/api/ledger/decay/run` | Run quarterly decay job |

### Governance
| Method | Path | Description |
|---|---|---|
| POST | `/api/governance/proposals` | Submit a proposal |
| GET | `/api/governance/proposals` | List all proposals |
| POST | `/api/governance/vote` | Cast a vote |
| GET | `/api/governance/results` | Passed/failed/pending proposals |
| POST | `/api/governance/veto` | Core team veto |
| POST | `/api/governance/dispute` | Submit a dispute |
| GET | `/api/governance/dispute/{id}` | Dispute status |
| GET | `/api/governance/disputes` | All disputes |
| GET | `/api/governance/charter` | Governance charter JSON |
| GET | `/api/governance/queue` | Escalation queue |
| GET | `/api/governance/audit` | Random validation audit sample |

### Trust
| Method | Path | Description |
|---|---|---|
| GET | `/api/trust/score/{contributor_id}` | Full trust score breakdown |
| GET | `/api/trust/scores` | All trust scores |
| POST | `/api/trust/fraud-check/{contributor_id}` | Run fraud detection |
| GET | `/api/trust/leaderboard` | Trust score leaderboard |

### Meta
| Method | Path | Description |
|---|---|---|
| GET | `/api/meta/brand` | Brand metadata (Compute Commons) |
| GET | `/api/meta/health` | Service health |

---

## Makefile Targets

```bash
make dev          # Start both backend + frontend
make backend      # Backend only (port 8000)
make frontend     # Frontend only (port 3000)
make seed         # Re-seed all synthetic data
make test         # Smoke tests — all major endpoints
make governance   # Governance module tests
make trust        # Trust score calculations + fraud checks
make compliance   # Compliance audit across all 25 synthetic accounts
make install      # Install all deps
make docker-up    # Docker Compose up
make clean        # Remove build artifacts
```

---

## Synthetic Data

Seeded on startup via `seed/seeder.py`:

- **25 contributors**: 3 Partner, 6 Expert, 8 Validator, 8 Contributor
- **37 contributions**: All 15 types, all statuses (pending/validating/complete/flagged/rejected)
- **25 validations**: Full scoring breakdowns, staking records
- **6 stakes**: Mix of upheld, overturned, and pending
- **5 governance proposals**: Active, ratified, failed, pending ratification
- **5+ votes**: Cross-chamber
- **2 disputes**: One panel-assigned, one decided
- **25 trust scores**: Range 22.2–79.1, avg 47.7
- **25 compliance records**: 1 non-compliant (FastPoints2024)
- **Quarterly stats**: Q1 + Q2 issuance for inflation guard calculation

### Scenario: FastPoints2024 Bad Actor
- Submitted spam bug reports with high text similarity
- Triggered velocity cap (> 8/day) → auto-hold
- Flagged: `velocity_exceeded`, `similarity_flagged`
- Trust score: 22.2 — governance voting suspended
- Attempted governance proposal to remove velocity cap → community_failed (2 for, 19 against)

---

## Design Principles

- **No external dependencies**: No GCP credentials, no Firestore emulator needed — in-memory store
- **Auto-seeding**: Backend populates all synthetic data on startup
- **Legal first**: Every redemption path runs compliance checks; transfer endpoint always rejects
- **Peer-governed**: Charter is a first-class API object, editable only through governance
- **Anti-speculation UI copy**: No language implying investment, appreciation, or financial return

---

*Compute Commons — Earn your seat at the frontier.*
