from fastapi import APIRouter, HTTPException
from app.services.web_scraper import scrape_worldlink_jobs
from app.services.job_handle import save_jobs_to_db
from pydantic import BaseModel
from typing import Optional


router = APIRouter()

class UpdateJobsRequest(BaseModel):
    description: Optional[str] = None  # Manual description (stored in metadata)

@router.post("/update-jobs")
def update_jobs(payload: UpdateJobsRequest):
    """
    Scrape WorldLink career site and save jobs into DB.
    Manual description is stored in metadata (not merged into scraped description).
    """
    try:
        # Scrape jobs
        jobs = scrape_worldlink_jobs()
        if not jobs:
            raise HTTPException(status_code=404, detail="No jobs found")

        # Pass manual description to save function (stored in metadata)
        save_jobs_to_db(jobs, manual_description=payload.description)

        return {"message": f"{len(jobs)} jobs scraped and saved successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

