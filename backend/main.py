"""
CATS — Main FastAPI Application (Phase 1 + Phase 2)
Mounts all service routers. Auto-seeds synthetic data on startup.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

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

app = FastAPI(
    title="Compute Commons",
    description="Peer-governed AI compute access — earned through verified contribution.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
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
def health():
    return {"status": "ok"}
