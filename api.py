from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
import os
import json
from datetime import datetime, timedelta
import uuid
from pathlib import Path

# Import the existing join_meet function
from gmeet import join_meet

app = FastAPI(title="Google Meet Bot API", description="API to control Google Meet recording bot")

# Store for tracking job status
jobs = {}
# Store for running processes
running_processes = {}

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
    
    # Set environment variables for the bot
    os.environ["GMEET_LINK"] = request.meet_link
    os.environ["GMAIL_USER_EMAIL"] = request.email
    os.environ["GMAIL_USER_PASSWORD"] = request.password
    os.environ["DURATION_IN_MINUTES"] = str(request.duration_minutes)
    os.environ["MAX_WAITING_TIME_IN_MINUTES"] = str(request.max_wait_time_minutes)
    os.environ["GLADIA_API_KEY"] = request.gladia_api_key
    os.environ["DIARIZATION"] = str(request.diarization).lower()
    
    if request.custom_name:
        os.environ["CUSTOM_NAME"] = request.custom_name
    
    # Create recordings directory if it doesn't exist
    Path("recordings").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    
    # Start the recording process in background
    task = background_tasks.add_task(run_recording_job, job_id, request)
    running_processes[job_id] = task
    
    return job_status

@app.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a recording job
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/jobs")
async def list_jobs():
    """
    List all jobs and clean old ones
    """
    # Clean old completed jobs (older than 24 hours)
    clean_old_jobs()
    return {"jobs": list(jobs.values())}

def clean_old_jobs():
    """
    Remove jobs older than 24 hours
    """
    cutoff_time = datetime.now() - timedelta(hours=24)
    jobs_to_remove = []
    
    for job_id, job in jobs.items():
        if job.completed_at:
            try:
                completed_time = datetime.fromisoformat(job.completed_at)
                if completed_time < cutoff_time:
                    jobs_to_remove.append(job_id)
            except:
                pass
    
    for job_id in jobs_to_remove:
        del jobs[job_id]
        if job_id in running_processes:
            del running_processes[job_id]
    
    if jobs_to_remove:
        print(f"Cleaned {len(jobs_to_remove)} old jobs")

@app.delete("/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and stop running process if any
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Stop running process if exists
    if job_id in running_processes:
        try:
            process = running_processes[job_id]
            if process and not process.done():
                process.cancel()
                jobs[job_id].status = "cancelled"
                jobs[job_id].message = "Job cancelled by user"
        except Exception as e:
            print(f"Error cancelling job {job_id}: {e}")
        finally:
            del running_processes[job_id]
    
    del jobs[job_id]
    return {"message": "Job deleted and stopped"}

async def run_recording_job(job_id: str, request: MeetRequest):
    """
    Background task to run the recording job
    """
    try:
        # Update job status
        jobs[job_id].status = "running"
        jobs[job_id].message = "Joining Google Meet..."
        
        # Calculate total timeout (recording + transcription + buffer)
        total_timeout = (request.duration_minutes + 10) * 60  # +10 minutes buffer
        
        # Run the join_meet function with timeout
        try:
            await asyncio.wait_for(join_meet(), timeout=total_timeout)
        except asyncio.TimeoutError:
            jobs[job_id].status = "failed"
            jobs[job_id].message = f"Job timed out after {total_timeout//60} minutes"
            return
        
        # Check if files were created
        video_path = "recordings/output.mp4"
        transcript_path = "recordings/transcript.json"
        
        if os.path.exists(video_path) and os.path.exists(transcript_path):
            jobs[job_id].status = "completed"
            jobs[job_id].message = "Recording completed successfully"
            jobs[job_id].video_path = video_path
            jobs[job_id].transcript_path = transcript_path
        else:
            jobs[job_id].status = "failed"
            jobs[job_id].message = "Recording failed - files not found"
            
    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Recording failed: {str(e)}"
    
    finally:
        jobs[job_id].completed_at = datetime.now().isoformat()
        
        # Calculate duration
        try:
            created_time = datetime.fromisoformat(jobs[job_id].created_at)
            completed_time = datetime.fromisoformat(jobs[job_id].completed_at)
            duration = int((completed_time - created_time).total_seconds())
            jobs[job_id].duration_seconds = duration
        except:
            pass
        
        # Clean up running process
        if job_id in running_processes:
            del running_processes[job_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 