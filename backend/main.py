from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from routes.resume import router as resume_router
from routes.funnel import router as funnel_router
from db.database import init_db

app = FastAPI(
    title="AntiGravity — VisionAstraa Hiring Engine",
    version="1.0.0",
    description="AI-powered resume scorer + 50k applicant funnel for VisionAstraa EV Academy"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
app.include_router(funnel_router, prefix="/api/funnel", tags=["funnel"])


@app.get("/health")
def health():
    return {"status": "ok", "product": "AntiGravity v1.0 — VisionAstraa Edition"}
