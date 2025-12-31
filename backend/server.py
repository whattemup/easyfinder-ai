from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import os
import csv
import io
import uuid
import logging

from easyfinder.ingestion import load_leads, parse_lead_data
from easyfinder.scoring import score_lead, get_lead_priority
from easyfinder.outreach import send_nda_email
from easyfinder.logging import log_event, get_logs, clear_logs

# -------------------------------------------------------------------
# App setup
# -------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

app = FastAPI(title="EasyFinder API")

# -------------------------------------------------------------------
# MongoDB
# -------------------------------------------------------------------

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "easyfinder_db")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable not set")

@app.on_event("startup")
async def startup_db():
    app.state.mongo_client = AsyncIOMotorClient(MONGO_URL)
    app.state.db = app.state.mongo_client[DB_NAME]

@app.on_event("shutdown")
async def shutdown_db():
    app.state.mongo_client.close()

# -------------------------------------------------------------------
# Router
# -------------------------------------------------------------------

api_router = APIRouter(prefix="/api")

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ProcessResponse(BaseModel):
    total_leads: int
    high_priority_count: int
    emails_sent: int
    message: str

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(
    input: StatusCheckCreate,
    request: Request
):
    status = StatusCheck(client_name=input.client_name)

    doc = status.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    await request.app.state.db.status_checks.insert_one(doc)
    return status

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks(request: Request):
    records = await request.app.state.db.status_checks.find(
        {}, {"_id": 0}
    ).to_list(1000)

    for r in records:
        r["timestamp"] = datetime.fromisoformat(r["timestamp"])

    return records

# -------------------------------------------------------------------
# Leads
# -------------------------------------------------------------------

@api_router.get("/leads")
async def get_leads():
    csv_path = DATA_DIR / "leads.csv"

    raw_leads = load_leads(str(csv_path))
    leads = parse_lead_data(raw_leads)

    for lead in leads:
        score = score_lead(lead)
        lead["score"] = score
        lead["priority"] = get_lead_priority(score)

    leads.sort(key=lambda x: x["score"], reverse=True)

    return {
        "success": True,
        "count": len(leads),
        "leads": leads,
    }

@api_router.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    content = await file.read()
    csv_content = content.decode("utf-8")

    csv_reader = csv.DictReader(io.StringIO(csv_content))
    required_fields = ["name", "email", "company", "company_size", "industry", "budget"]

    if not all(field in csv_reader.fieldnames for field in required_fields):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain: {', '.join(required_fields)}"
        )

    csv_path = DATA_DIR / "leads.csv"
    csv_path.write_text(csv_content, encoding="utf-8")

    log_event("CSV_UPLOADED", {"filename": file.filename})

    return {"success": True, "filename": file.filename}

@api_router.post("/leads/process", response_model=ProcessResponse)
async def process_leads():
    csv_path = DATA_DIR / "leads.csv"
    raw_leads = load_leads(str(csv_path))
    leads = parse_lead_data(raw_leads)

    EMAIL_THRESHOLD = 70
    high_priority_count = 0
    emails_sent = 0

    for lead in leads:
        score = score_lead(lead)
        priority = get_lead_priority(score)

        log_event("LEAD_SCORED", {
            "email": lead.get("email"),
            "score": score,
            "priority": priority
        })

        if score >= EMAIL_THRESHOLD and lead.get("email"):
            high_priority_count += 1
            if send_nda_email(
                lead["email"],
                lead.get("name", "there"),
                lead.get("company", "")
            ):
                emails_sent += 1

    return ProcessResponse(
        total_leads=len(leads),
        high_priority_count=high_priority_count,
        emails_sent=emails_sent,
        message="Leads processed successfully"
    )

# -------------------------------------------------------------------
# Logs
# -------------------------------------------------------------------

@api_router.get("/logs")
async def get_activity_logs(limit: int = 100):
    return {"success": True, "logs": get_logs(limit)}

@api_router.delete("/logs")
async def clear_activity_logs():
    clear_logs()
    return {"success": True}

# -------------------------------------------------------------------
# Register router
# -------------------------------------------------------------------

app.include_router(api_router)
