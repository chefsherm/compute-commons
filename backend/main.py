import sys, os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from intake.router import router as intake_router
from scoring.router import router as scoring_router
from validation.router import router as validation_router
from ledger.router import router as ledger_router
from governance.router import router as governance_router
from trust.router import router as trust_router
from meta.router import router as meta_router
from progression.router import router as progression_router
from partners.router import router as partners_router

from seed.seeder import seed_all
from shared.database import init_db

app = FastAPI(
    title="Compute Commons",
    description="Peer-governed AI compute access — earned through verified contribution.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — always include computecommons.io; extend via ALLOWED_ORIGINS env var
_default_origins = [
    "https://computecommons.io",
    "https://www.computecommons.io",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
]
_extra = os.getenv("ALLOWED_ORIGINS", "")
_allowed_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all service routers
app.include_router(intake_router, prefix="/api/intake", tags=["Intake"])
app.include_router(scoring_router, prefix="/api/scoring", tags=["Scoring"])
app.include_router(validation_router, prefix="/api/validation", tags=["Validation"])
app.include_router(ledger_router, prefix="/api/ledger", tags=["Ledger"])
app.include_router(governance_router, prefix="/api/governance", tags=["Governance"])
app.include_router(trust_router, prefix="/api/trust", tags=["Trust"])
app.include_router(meta_router, prefix="/api/meta", tags=["Meta"])
app.include_router(progression_router, prefix="/api/progression", tags=["Progression"])
app.include_router(partners_router, prefix="/api/partners", tags=["Partners"])


@app.on_event("startup")
async def startup():
    print("🚀 Compute Commons starting up...")

    # Initialize Firestore async client (production + staging)
    # Skipped gracefully in local dev if GOOGLE_CLOUD_PROJECT is not set
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        try:
            init_db()
            print("🔥 Firestore connected")
        except Exception as e:
            print(f"⚠️  Firestore init failed (falling back to in-memory): {e}")
    else:
        print("⚠️  GOOGLE_CLOUD_PROJECT not set — using in-memory store")
        seed_all()

    print("🌐 API ready at http://localhost:8000")
    print("📖 Docs at http://localhost:8000/docs")


@app.get("/")
def root():
    return {
        "service": "Compute Commons",
        "version": "2.0.0",
        "tagline": "Earn your seat at the frontier.",
        "docs": "/docs",
        "services": {
            "intake": "/api/intake",
            "scoring": "/api/scoring",
            "validation": "/api/validation",
            "ledger": "/api/ledger",
            "governance": "/api/governance",
            "trust": "/api/trust",
            "meta": "/api/meta",
            "progression": "/api/progression",
            "partners": "/api/partners",
        },
    }


@app.get("/health")
async def health():
    """
    Health check used by Cloud Run liveness + readiness probes.

    Returns 200 {"status": "ok"}   when everything is reachable.
    Returns 503 {"status": "degraded"} if Firestore is unreachable.

    Always responds within ~3 seconds — the Firestore ping has a hard timeout.
    Cloud Run will restart the container if this returns non-2xx.
    """
    import asyncio
    from time import perf_counter
    from typing import Optional as Opt

    env = os.getenv("ENV", "development")
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    firestore_ok: Opt[bool] = None
    firestore_latency_ms: Opt[float] = None

    if project:
        try:
            from shared.database import get_db
            db = await get_db()
            t0 = perf_counter()
            # Lightweight probe: fetch a known-small doc (leaderboard snapshot)
            await asyncio.wait_for(
                db.get("leaderboard", "top50"),
                timeout=3.0,
            )
            firestore_latency_ms = round((perf_counter() - t0) * 1000, 1)
            firestore_ok = True
        except asyncio.TimeoutError:
            firestore_ok = False
            firestore_latency_ms = 3000.0
        except Exception as exc:
            firestore_ok = False
            firestore_latency_ms = None

    degraded = firestore_ok is False
    from fastapi.responses import JSONResponse
    body = {
        "status": "degraded" if degraded else "ok",
        "env": env,
        "project": project or "not-set",
        "firestore": {
            "reachable": firestore_ok,
            "latency_ms": firestore_latency_ms,
        } if project else "not-configured",
        "version": "2.0.0",
    }
    return JSONResponse(content=body, status_code=503 if degraded else 200)

