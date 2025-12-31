from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone
import sys
import csv
import io
import uvicorn

# Add easyfinder to path
sys.path.insert(0, str(Path(__file__).parent))

from easyfinder.ingestion import load_leads, parse_lead_data
from easyfinder.scoring import score_lead, get_lead_priority
from easyfinder.outreach import send_nda_email
from easyfinder.logging import log_event, get_logs, clear_logs

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# MongoDB connection
mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")

if not mongo_url or not db_name:
    raise RuntimeError("MONGO_URL or DB_NAME environment variable not set")
    
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("backend.server:app", host="0.0.0.0", port=port)
    
# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# -----------------------
# Models
# -----------------------

class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class Lead(BaseModel):
    name: str
    email: str
    company: str
    company_size: str
    industry: str
    budget: str
    phone: str = ""
    website: str = ""
    score: Optional[int] = None
    priority: Optional[str] = None


class ProcessResponse(BaseModel):
    total_leads: int
    high_priority_count: int
    emails_sent: int
    message: str


    
# -----------------------
# Routes
# -----------------------

@api_router.get("/")
async def root():
    return {"message": "Hello World"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    doc = status_obj.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()

    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    for check in status_checks:
        if isinstance(check.get("timestamp"), str):
            check["timestamp"] = datetime.fromisoformat(check["timestamp"])

    return status_checks


# -----------------------
# EasyFinder AI Endpoints
# -----------------------

@api_router.get("/leads")
async def get_leads():
    """Get all leads with their scores."""
    try:
        csv_path = "/app/backend/data/leads.csv"
        raw_leads = load_leads(csv_path)
        leads = parse_lead_data(raw_leads)

        scored_leads = []
        for lead in leads:
            score = score_lead(lead)
            priority = get_lead_priority(score)
            lead["score"] = score
            lead["priority"] = priority
            scored_leads.append(lead)

        scored_leads.sort(key=lambda x: x["score"], reverse=True)

        return {
            "success": True,
            "count": len(scored_leads),
            "leads": scored_leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """Upload a CSV file with leads."""
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")

        csv_reader = csv.DictReader(io.StringIO(csv_content))
        required_fields = ["name", "email", "company", "company_size", "industry", "budget"]

        if not all(field in csv_reader.fieldnames for field in required_fields):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must contain these fields: {', '.join(required_fields)}"
            )

        csv_path = "/app/backend/data/leads.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_content)

        log_event("CSV_UPLOADED", {
            "filename": file.filename,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {
            "success": True,
            "message": "CSV uploaded successfully",
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/leads/process", response_model=ProcessResponse)
async def process_leads():
    """Process all leads: score them and send emails to high-priority leads."""
    try:
        csv_path = "/app/backend/data/leads.csv"
        raw_leads = load_leads(csv_path)
        leads = parse_lead_data(raw_leads)

        high_priority_count = 0
        emails_sent = 0
        EMAIL_THRESHOLD = 70

        for lead in leads:
            score = score_lead(lead)
            priority = get_lead_priority(score)

            log_event("LEAD_SCORED", {
                "name": lead.get("name"),
                "email": lead.get("email"),
                "company": lead.get("company"),
                "score": score,
                "priority": priority
            })

            if score >= EMAIL_THRESHOLD and lead.get("email"):
                high_priority_count += 1
                success = send_nda_email(
                    to_email=lead["email"],
                    lead_name=lead.get("name", "there"),
                    company=lead.get("company", "your company")
                )
                if success:
                    emails_sent += 1

        return ProcessResponse(
            total_leads=len(leads),
            high_priority_count=high_priority_count,
            emails_sent=emails_sent,
            message=f"Processed {len(leads)} leads successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/logs")
async def get_activity_logs(limit: int = 100):
    """Get activity logs."""
    try:
        logs = get_logs(limit)
        return {
            "success": True,
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/logs")
async def clear_activity_logs():
    """Clear all activity logs."""
    try:
        clear_logs()
        return {
            "success": True,
            "message": "Logs cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Register router
app.include_router(api_router)
