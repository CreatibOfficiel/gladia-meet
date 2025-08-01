from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
import json
from datetime import datetime, timedelta
import uuid
from pathlib import Path

app = FastAPI(title="Google Meet Bot API", description="API to control Google Meet recording bot")

# Store for tracking job status
jobs = {}

class MeetRequest(BaseModel):
    meet_link: str
    email: str
    password: str
    duration_minutes: int = 15
    max_wait_time_minutes: int = 5
    gladia_api_key: str
    diarization: bool = False
    custom_name: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: str
    completed_at: Optional[str] = None
    video_path: Optional[str] = None
    transcript_path: Optional[str] = None
    duration_seconds: Optional[int] = None

@app.get("/")
async def root():
    return {"message": "Google Meet Bot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stats")
async def get_stats():
    """
    Get API statistics
    """
    clean_old_jobs()  # Clean before stats
    
    total_jobs = len(jobs)
    running_jobs = len([j for j in jobs.values() if j.status == "running"])
    completed_jobs = len([j for j in jobs.values() if j.status == "completed"])
    failed_jobs = len([j for j in jobs.values() if j.status == "failed"])
    
    # Calculate average duration
    durations = [j.duration_seconds for j in jobs.values() if j.duration_seconds]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return {
        "total_jobs": total_jobs,
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "average_duration_seconds": round(avg_duration, 2),
        "uptime": datetime.now().isoformat()
    }

@app.post("/start-recording", response_model=JobStatus)
async def start_recording(request: MeetRequest, background_tasks: BackgroundTasks):
    """
    Start a Google Meet recording session
    """
    job_id = str(uuid.uuid4())
    
    # Validate required fields
    if not request.meet_link or not request.email or not request.password or not request.gladia_api_key:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Create job status
    job_status = JobStatus(
        job_id=job_id,
        status="starting",
        message="Job created and starting...",
        created_at=datetime.now().isoformat()
    )
    
    jobs[job_id] = job_status
    
    # Add background task
    background_tasks.add_task(run_recording_job, job_id, request)
    
    return job_status

@app.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a specific recording job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/jobs")
async def list_jobs():
    """
    Get a list of all recording jobs
    """
    clean_old_jobs()
    return list(jobs.values())

def clean_old_jobs():
    """
    Clean up old completed jobs (older than 24 hours)
    """
    cutoff_time = datetime.now() - timedelta(hours=24)
    jobs_to_remove = []
    
    for job_id, job in jobs.items():
        if job.status in ["completed", "failed"] and job.created_at:
            try:
                created_time = datetime.fromisoformat(job.created_at.replace('Z', '+00:00'))
                if created_time < cutoff_time:
                    jobs_to_remove.append(job_id)
            except:
                pass
    
    for job_id in jobs_to_remove:
        del jobs[job_id]

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a specific job and its associated files
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Delete associated files if they exist
    if job.video_path and os.path.exists(job.video_path):
        try:
            os.remove(job.video_path)
        except:
            pass
    
    if job.transcript_path and os.path.exists(job.transcript_path):
        try:
            os.remove(job.transcript_path)
        except:
            pass
    
    # Remove job from store
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}

async def run_recording_job(job_id: str, request: MeetRequest):
    """
    Background task to run the recording job
    """
    try:
        # Update job status to running
        jobs[job_id].status = "running"
        jobs[job_id].message = "Joining Google Meet..."
        
        # Simulate some work (replace with actual recording logic)
        await asyncio.sleep(2)
        
        # Update job status to completed
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Recording completed successfully"
        jobs[job_id].completed_at = datetime.now().isoformat()
        jobs[job_id].duration_seconds = request.duration_minutes * 60
        jobs[job_id].video_path = f"/app/recordings/recording_{job_id}.mp4"
        jobs[job_id].transcript_path = f"/app/recordings/transcript_{job_id}.txt"
        
    except Exception as e:
        # Update job status to failed
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Recording failed: {str(e)}"
        jobs[job_id].completed_at = datetime.now().isoformat()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 