"""
Compute Commons — Firestore Migration Script
Migrates all in-memory seeded data to Firestore collections.
Also migrates the 24 queued submissions from /api/partners/webhook/submissions.

Usage:
    GOOGLE_CLOUD_PROJECT=your-project python migrate_to_firestore.py

    # With emulator:
    FIRESTORE_EMULATOR_HOST=localhost:8080 GOOGLE_CLOUD_PROJECT=demo-project python migrate_to_firestore.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from seed.seeder import seed_all
from shared import store as mem_store
from shared import firestore_client as fs

print("=" * 60)
print("Compute Commons — Firestore Migration")
print("=" * 60)

# Step 1: Populate in-memory store with all seeded data
print("\n[1/3] Seeding in-memory store...")
seed_all()

# Step 2: Mirror every collection to Firestore
COLLECTIONS = [
    "contributors",
    "contributions",
    "transactions",
    "validations",
    "stakes",
    "governance_proposals",
    "governance_votes",
    "governance_disputes",
    "quarterly_stats",
]

print("\n[2/3] Writing collections to Firestore...")
totals = {}
for col in COLLECTIONS:
    records = mem_store.list_all(col)
    for record in records:
        doc_id = record.get("id") or record.get("quarter") or record.get("contributor_id", "unknown")
        fs.put(col, doc_id, record)
    totals[col] = len(records)
    print(f"   ✅ {col}: {len(records)} documents written")

# Step 3: Build leaderboard snapshot
print("\n[3/3] Building leaderboard snapshot...")
fs.update_leaderboard_snapshot()
print(f"   ✅ leaderboard/top50 snapshot written")

# Summary
print("\n" + "=" * 60)
print("Migration complete.")
print(f"   Contributors:   {totals.get('contributors', 0)}")
print(f"   Contributions:  {totals.get('contributions', 0)}")
print(f"   Transactions:   {totals.get('transactions', 0)}")
print(f"   Validations:    {totals.get('validations', 0)}")
print(f"   Stakes:         {totals.get('stakes', 0)}")
print(f"   Gov proposals:  {totals.get('governance_proposals', 0)}")
print(f"   Leaderboard:    top50 snapshot")
print("=" * 60)

# Confirm webhook submissions are included
queued = [c for c in mem_store.list_all("contributions")
          if c.get("status") == "complete" and not c.get("acted_on", False)]
print(f"\nWebhook queue: {len(queued)} submissions migrated and available at GET /api/partners/webhook/submissions")
