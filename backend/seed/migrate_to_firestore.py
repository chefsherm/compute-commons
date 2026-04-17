import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from seed.seeder import seed_all
from shared import store

def migrate():
    # 1. Seed in-memory store
    print("🌱 Seeding in-memory store...")
    seed_all()

    # 2. Extract and migrate contributors
    print("🚀 Migrating contributors to Firestore...")
    all_contributors = store.list_all("contributors")
    for c in all_contributors:
        # put() will handle Firestore mirroring if db is available
        store.put("contributors", c["id"], c)
    print(f"   → Migrated {len(all_contributors)} contributors")

    # 3. Extract and migrate the 24 eligible submissions
    print("🚀 Migrating eligible submissions to Firestore...")
    all_contribs = store.list_all("contributions")
    eligible = [
        c for c in all_contribs
        if c.get("status") == "complete" and not c.get("acted_on", False)
    ]

    for c in eligible[:24]:
        store.put("submissions", c["id"], {
            "id": c["id"],
            "contributor_id": c["contributor_id"],
            "status": c["status"],
            "model": "claude-3-5-sonnet-20241022",
            "timestamp": c.get("completed_at") or c.get("submitted_at")
        })
    print(f"   → Migrated {len(eligible[:24])} submissions")

    # 4. Generate and migrate initial leaderboard
    print("🚀 Migrating initial leaderboard to Firestore...")
    contributors = store.list_all("contributors")
    contributors.sort(key=lambda x: x["points"], reverse=True)
    top_50 = []
    for i, c in enumerate(contributors[:50]):
        entry = {
            "rank": i + 1,
            "contributor_id": c["id"],
            "handle": c["handle"],
            "tier": c["tier"],
            "points": c["points"],
            "credits_balance": c["credits_balance"],
            "accuracy_score": c["accuracy_score"],
            "trust_score": c.get("trust_score", 0),
            "domains": c.get("domains", []),
            "domain": c.get("domains")[0] if c.get("domains") else None,
        }
        top_50.append(entry)
        store.put("leaderboard", c["id"], entry)
    print(f"   → Migrated top {len(top_50)} leaderboard entries")

    print("✅ Migration complete.")

if __name__ == "__main__":
    migrate()
