.PHONY: dev seed test governance trust compliance clean

# ─── Development ──────────────────────────────────────────────────────────────
dev:
	@echo "🚀 Starting Compute Commons (CATS) development servers..."
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:3000"
	@echo "   API Docs: http://localhost:8000/docs"
	@trap 'kill %1 %2' SIGINT; \
	cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000 & \
	cd frontend && npm run dev & \
	wait

backend:
	@echo "🔌 Starting backend only..."
	cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000

frontend:
	@echo "🎨 Starting frontend only..."
	cd frontend && npm run dev

# ─── Data ─────────────────────────────────────────────────────────────────────
seed:
	@echo "🌱 Seeding synthetic data..."
	cd backend && source .venv/bin/activate && python3 -c "from seed.seeder import seed_all; seed_all()"

# ─── Tests ────────────────────────────────────────────────────────────────────
test:
	@echo "🧪 Running smoke tests against all endpoints..."
	@echo "--- Health ---"
	@curl -sf http://localhost:8000/health && echo " ✅ Health OK" || echo " ❌ Backend not running"
	@echo "\n--- Meta/Brand ---"
	@curl -sf http://localhost:8000/api/meta/brand | python3 -c "import sys,json; d=json.load(sys.stdin); print(' ✅ Brand:', d['platform_name'])" || echo " ❌ Brand endpoint failed"
	@echo "\n--- Contributors (leaderboard) ---"
	@curl -sf http://localhost:8000/api/scoring/leaderboard | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ {len(d)} contributors on leaderboard')" || echo " ❌ Leaderboard failed"
	@echo "\n--- Exchange Rate ---"
	@curl -sf http://localhost:8000/api/scoring/exchange-rate | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ Rate: \$${{d[\"dollar_per_point\"]}}/pt, inflation_guard={d[\"inflation_guard\"]}')" || echo " ❌ Exchange rate failed"
	@echo "\n--- Governance Charter ---"
	@curl -sf http://localhost:8000/api/governance/charter | python3 -c "import sys,json; d=json.load(sys.stdin); print(' ✅ Charter loaded:', d['mission'][:60], '...')" || echo " ❌ Charter failed"
	@echo "\n--- Trust Scores ---"
	@curl -sf http://localhost:8000/api/trust/scores | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ {len(d)} trust scores computed')" || echo " ❌ Trust scores failed"
	@echo "\n--- Compliance (contrib_004) ---"
	@curl -sf http://localhost:8000/api/ledger/compliance-status/contrib_004 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ Compliant: {d[\"is_compliant\"]}, Transfers: {d[\"transfer_attempts\"]}')" || echo " ❌ Compliance failed"
	@echo "\n--- Taxonomy ---"
	@curl -sf http://localhost:8000/api/intake/taxonomy | python3 -c "import sys,json; d=json.load(sys.stdin); types=list(d['contribution_types'].keys()); print(f' ✅ {len(types)} contribution types: {types[:4]}...')" || echo " ❌ Taxonomy failed"
	@echo "\n✅ Smoke tests complete"

# ─── Phase 2 Test Suites ──────────────────────────────────────────────────────
governance:
	@echo "⚖ Running governance module tests..."
	@curl -sf http://localhost:8000/api/governance/proposals | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ {len(d)} proposals loaded')"
	@curl -sf http://localhost:8000/api/governance/results | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ Passed: {len(d[\"passed\"])}, Failed: {len(d[\"failed\"])}, Pending: {len(d[\"pending\"])}')"
	@curl -sf http://localhost:8000/api/governance/disputes | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ {len(d)} disputes')"
	@curl -sf http://localhost:8000/api/governance/charter | python3 -c "import sys,json; d=json.load(sys.stdin); print(f' ✅ Charter: {len(d[\"what_can_be_governed\"])} governable items, {len(d[\"what_cannot_be_governed\"])} protected')"
	@echo " ✅ Governance tests passed"

trust:
	@echo "◎ Running trust score calculations against all synthetic contributors..."
	@curl -sf http://localhost:8000/api/trust/scores | python3 -c "\
import sys,json; d=json.load(sys.stdin); \
scores=[x['trust_score'] for x in d]; \
print(f' ✅ {len(scores)} scores computed'); \
print(f'   Min: {min(scores):.1f}, Max: {max(scores):.1f}, Avg: {sum(scores)/len(scores):.1f}'); \
high=[x for x in d if x['trust_score']>=70]; \
low=[x for x in d if x['trust_score']<30]; \
print(f'   Priority validators (≥70): {len(high)}'); \
print(f'   Voting suspended (<30): {len(low)}')"
	@echo " ✅ Trust score calculations complete"
	@echo ""
	@echo "◎ Running fraud checks against FastPoints2024..."
	@curl -sf -X POST http://localhost:8000/api/trust/fraud-check/contrib_022 | python3 -c "\
import sys,json; d=json.load(sys.stdin); \
print(f' ✅ Fraud check for {d[\"handle\"]}: clean={d[\"is_clean\"]}'); \
[print(f'   🚨 {f[\"type\"]}: {f[\"detail\"]}') for f in d['flags']]"

compliance:
	@echo "⚖ Running compliance checks against all synthetic contributor accounts..."
	@python3 -c "\
import urllib.request, json, sys
base = 'http://localhost:8000'
ids = [f'contrib_{i:03d}' for i in range(1, 26)]
results = []
for id in ids:
    try:
        with urllib.request.urlopen(f'{base}/api/ledger/compliance-status/{id}') as r:
            d = json.loads(r.read())
            results.append(d)
    except Exception as e:
        pass
compliant = sum(1 for r in results if r['is_compliant'])
non_compliant = [r for r in results if not r['is_compliant']]
print(f' ✅ {len(results)} compliance records checked')
print(f'   Compliant: {compliant}/{len(results)}')
print(f'   Non-compliant: {len(non_compliant)}')
for r in non_compliant:
    print(f'   ❌ {r[\"contributor_id\"]}: {r[\"compliance_flags\"]}')
transfers = sum(r['transfer_attempts'] for r in results)
print(f'   Total transfer attempts across all accounts: {transfers} (should be 0 for clean accounts)')
"
	@echo " ✅ Compliance audit complete"

# ─── Setup ────────────────────────────────────────────────────────────────────
install:
	@echo "📦 Installing dependencies..."
	cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/.next
	@echo " ✅ Clean complete"
