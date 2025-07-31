#!/usr/bin/env python3
"""
Test script for the Google Meet Bot API
"""

import requests
import json
import time
import sys

# API base URL
API_BASE = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False

def start_recording(meet_link, email, password, gladia_api_key, duration_minutes=1):
    """Start a recording session"""
    print("Starting recording session...")
    
    payload = {
        "meet_link": meet_link,
        "email": email,
        "password": password,
        "duration_minutes": duration_minutes,
        "max_wait_time_minutes": 2,
        "gladia_api_key": gladia_api_key,
        "diarization": False,
        "custom_name": "Test Bot"
    }
    
    try:
        response = requests.post(f"{API_BASE}/start-recording", json=payload)
        if response.status_code == 200:
            job_data = response.json()
            print(f"✅ Recording started with job ID: {job_data['job_id']}")
            return job_data['job_id']
        else:
            print(f"❌ Failed to start recording: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error starting recording: {e}")
        return None

def check_job_status(job_id):
    """Check the status of a job"""
    try:
        response = requests.get(f"{API_BASE}/job/{job_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get job status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error checking job status: {e}")
        return None

def wait_for_completion(job_id, timeout_minutes=10):
    """Wait for a job to complete"""
    print(f"Waiting for job {job_id} to complete...")
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        job_data = check_job_status(job_id)
        if job_data:
            status = job_data['status']
            message = job_data['message']
            print(f"Status: {status} - {message}")
            
            if status == "completed":
                print("✅ Recording completed successfully!")
                print(f"Video: {job_data.get('video_path', 'N/A')}")
                print(f"Transcript: {job_data.get('transcript_path', 'N/A')}")
                return True
            elif status == "failed":
                print("❌ Recording failed!")
                return False
        
        time.sleep(5)  # Check every 5 seconds
    
    print("⏰ Timeout waiting for completion")
    return False

def list_jobs():
    """List all jobs"""
    try:
        response = requests.get(f"{API_BASE}/jobs")
        if response.status_code == 200:
            jobs = response.json()['jobs']
            print(f"Found {len(jobs)} jobs:")
            for job in jobs:
                print(f"  - {job['job_id']}: {job['status']} ({job['message']})")
        else:
            print(f"❌ Failed to list jobs: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error listing jobs: {e}")

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

def quick_test():
    """Quick test - just check if API is running"""
    print("🧪 Quick API Test")
    print("=" * 20)
    
    if test_health():
        print("✅ API is running and healthy!")
        return True
    else:
        print("❌ API is not responding")
        return False

def main():
    """Main test function"""
    # Check for quick test flag
    if "--quick-test" in sys.argv:
        if quick_test():
            return 0
        else:
            sys.exit(1)
    
    print("Google Meet Bot API Test")
    print("=" * 30)
    
    # Check .env file
    if not check_env_file():
        sys.exit(1)
    
    # Test health
    if not test_health():
        sys.exit(1)
    
    # Get test parameters from user
    print("\nEnter test parameters:")
    meet_link = input("Google Meet Link: ").strip()
    email = input("Gmail Email: ").strip()
    password = input("Gmail Password: ").strip()
    gladia_api_key = input("Gladia API Key: ").strip()
    
    if not all([meet_link, email, password, gladia_api_key]):
        print("❌ All parameters are required")
        sys.exit(1)
    
    # Start recording
    job_id = start_recording(meet_link, email, password, gladia_api_key)
    if not job_id:
        sys.exit(1)
    
    # Wait for completion
    success = wait_for_completion(job_id)
    
    # List all jobs
    print("\nAll jobs:")
    list_jobs()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 