#!/usr/bin/env python3
"""
Example usage of the Google Meet Bot API
"""

import requests
import time
import json

# Configuration
API_BASE = "http://localhost:8000"

def example_start_recording():
    """Example of starting a recording session"""
    
    # Prepare the request payload
    payload = {
        "meet_link": "https://meet.google.com/your-meet-id",
        "email": "your-email@gmail.com",
        "password": "your-password",
        "duration_minutes": 5,  # Short duration for testing
        "max_wait_time_minutes": 2,
        "gladia_api_key": "your-gladia-api-key",
        "diarization": True,
        "custom_name": "Recording Bot"
    }
    
    print("Starting recording session...")
    response = requests.post(f"{API_BASE}/start-recording", json=payload)
    
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data['job_id']
        print(f"✅ Recording started! Job ID: {job_id}")
        return job_id
    else:
        print(f"❌ Failed to start recording: {response.status_code}")
        print(response.text)
        return None

def example_monitor_job(job_id):
    """Example of monitoring a job until completion"""
    
    print(f"Monitoring job {job_id}...")
    
    while True:
        response = requests.get(f"{API_BASE}/job/{job_id}")
        
        if response.status_code == 200:
            job_data = response.json()
            status = job_data['status']
            message = job_data['message']
            
            print(f"Status: {status} - {message}")
            
            if status == "completed":
                print("🎉 Recording completed successfully!")
                print(f"Video file: {job_data.get('video_path')}")
                print(f"Transcript file: {job_data.get('transcript_path')}")
                return True
            elif status == "failed":
                print("💥 Recording failed!")
                return False
        else:
            print(f"Error checking job status: {response.status_code}")
            return False
        
        time.sleep(10)  # Check every 10 seconds

def example_list_jobs():
    """Example of listing all jobs"""
    
    print("Listing all jobs...")
    response = requests.get(f"{API_BASE}/jobs")
    
    if response.status_code == 200:
        jobs = response.json()['jobs']
        print(f"Found {len(jobs)} jobs:")
        
        for job in jobs:
            print(f"  - {job['job_id']}: {job['status']}")
            print(f"    Created: {job['created_at']}")
            print(f"    Message: {job['message']}")
            if job.get('completed_at'):
                print(f"    Completed: {job['completed_at']}")
            print()
    else:
        print(f"Error listing jobs: {response.status_code}")

def example_health_check():
    """Example of checking API health"""
    
    print("Checking API health...")
    response = requests.get(f"{API_BASE}/health")
    
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ API is healthy - {health_data['timestamp']}")
        return True
    else:
        print(f"❌ API health check failed: {response.status_code}")
        return False

def check_env_file():
    """Check if .env file exists and create it if needed"""
    import os
    if not os.path.exists(".env"):
        print("🔍 .env file not found")
        # Use the setup script
        import subprocess
        result = subprocess.run([sys.executable, "setup_env.py", "--create"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ .env file created successfully")
            return False  # Still need to edit
        else:
            print("❌ Failed to create .env file")
            return False
    return True

def main():
    """Main example function"""
    
    print("Google Meet Bot API - Example Usage")
    print("=" * 40)
    
    # Check .env file
    if not check_env_file():
        return
    
    # Check if API is running
    if not example_health_check():
        print("Make sure the API server is running with: docker run -e API_MODE=true -p 8000:8000 gmeet")
        return
    
    # List existing jobs
    example_list_jobs()
    
    # Start a new recording (uncomment to test)
    # job_id = example_start_recording()
    # if job_id:
    #     example_monitor_job(job_id)
    
    print("\nExample completed!")

if __name__ == "__main__":
    main() 