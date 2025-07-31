# Setup Guide for Google Meet Bot API

This guide will help you set up and use the Google Meet Bot with the new API functionality.

## Prerequisites

1. **Docker** installed on your system
2. **Gladia API Key** - Get one for free at https://app.gladia.io/
3. **Gmail Account** with 2FA disabled or app password configured

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t gmeet -f Dockerfile .
```

### 2. Start the API Server

```bash
docker run -d \
    --name gmeet-api \
    -e API_MODE=true \
    -p 8000:8000 \
    -v $PWD/recordings:/app/recordings \
    -v $PWD/screenshots:/app/screenshots \
    gmeet
```

### 3. Test the API

```bash
# Check if the API is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### 4. Start a Recording Session

```bash
curl -X POST "http://localhost:8000/start-recording" \
     -H "Content-Type: application/json" \
     -d '{
         "meet_link": "https://meet.google.com/your-meet-id",
         "email": "your-email@gmail.com",
         "password": "your-password",
         "duration_minutes": 5,
         "gladia_api_key": "your-gladia-api-key"
     }'
```

## Using the Test Script

1. Install Python dependencies:

```bash
pip install requests
```

2. Run the test script:

```bash
python test_api.py
```

3. Follow the prompts to enter your credentials and test the API.

## Using the Example Script

```bash
python example_usage.py
```

This will show you how to use the API programmatically.

## File Structure

After running recordings, you'll find:

```
recordings/
├── output.mp4          # Video recording
└── transcript.json     # Transcription data

screenshots/            # Debug screenshots
├── email.png
├── password.png
├── signed_in.png
└── ...
```

## Troubleshooting

### API Not Responding

- Check if the container is running: `docker ps`
- Check container logs: `docker logs gmeet-api`
- Ensure port 8000 is not blocked by firewall

### Recording Fails

- Verify your Gmail credentials
- Check if 2FA is disabled or use app password
- Ensure the Google Meet link is valid and accessible
- Check the screenshots folder for debug information

### Transcription Fails

- Verify your Gladia API key is valid
- Check if the video file was created successfully
- Review the error.json file in recordings folder

## Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive data
- Consider using app passwords instead of main Gmail password
- The API runs in a container for isolation

## API Endpoints Summary

- `GET /` - API info
- `GET /health` - Health check
- `POST /start-recording` - Start recording session
- `GET /job/{job_id}` - Get job status
- `GET /jobs` - List all jobs
- `DELETE /job/{job_id}` - Delete job

## Support

For issues and questions:

1. Check the container logs
2. Review the screenshots for visual debugging
3. Verify all prerequisites are met
4. Test with a short duration first
