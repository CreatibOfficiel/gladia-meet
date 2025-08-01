# gmeet-bot

This example project will help you record and transcribe using gladia a google meet meeting from a container with a audio and video using virtual sound card (pulseaudio) and screen recording with Xscreen.

One of the main challenge is to record the session without a sound card using audio loop sink and not being flagged by the meeting provider (in this case google meet).

This project is a proof of concept with limited support and is not meant for production grade usage.

## Features

- **API Mode**: Accept HTTP requests to start recording sessions with parameters
- **Background Processing**: Jobs run in the background with status tracking
- **File Management**: Automatically saves video recordings and transcriptions
- **Health Monitoring**: Built-in health checks and monitoring
- **Log Management**: Automatic log rotation and structured logging

## Quick Setup

### 1. Configuration et Démarrage

```bash
# Configuration automatique complète
./quick_start.sh
```

### 2. Configuration manuelle

```bash
# Créer et configurer .env
python setup_env.py --create
nano .env
```

### 3. Build Docker Image

```bash
# Build automatique avec détection de plateforme
./build.sh
```

## Usage

### API Mode

#### Option 1: Docker Compose (Recommandé)

```bash
# Configuration automatique
python setup_env.py --create
# Éditer .env avec vos valeurs
nano .env

# Démarrer l'API
docker-compose up -d gmeet-api
```

#### Option 2: Docker Run

```bash
docker run -it \
    --env-file .env \
    -p 8000:8000 \
    -v $PWD/recordings:/app/recordings \
    -v $PWD/screenshots:/app/screenshots \
    -v $PWD/logs:/app/logs \
    gmeet-bot-api:latest
```

## API Endpoints

### Start Recording

**POST** `/start-recording`

Start a new Google Meet recording session.

**Request Body:**

```json
{
  "meet_link": "https://meet.google.com/my-gmeet-id",
  "email": "myuser1234@gmail.com",
  "password": "my_gmail_password",
  "duration_minutes": 15,
  "max_wait_time_minutes": 5,
  "gladia_api_key": "YOUR_GLADIA_API_KEY",
  "diarization": false,
  "custom_name": "My Recording"
}
```

**Response:**

```json
{
  "job_id": "uuid-string",
  "status": "starting",
  "message": "Job created and starting...",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": null,
  "video_path": null,
  "transcript_path": null,
  "duration_seconds": null
}
```

### Get Job Status

**GET** `/job/{job_id}`

Get the status of a specific recording job.

**Response:**

```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "message": "Recording completed successfully",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:15:00",
  "video_path": "/app/recordings/recording_20240101_120000.mp4",
  "transcript_path": "/app/recordings/transcript_20240101_120000.txt",
  "duration_seconds": 900
}
```

### List All Jobs

**GET** `/jobs`

Get a list of all recording jobs.

### Delete Job

**DELETE** `/job/{job_id}`

Delete a specific job and its associated files.

### Health Check

**GET** `/health`

Check if the API is running properly.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00"
}
```

### API Statistics

**GET** `/stats`

Get API usage statistics.

**Response:**

```json
{
  "total_jobs": 10,
  "running_jobs": 1,
  "completed_jobs": 8,
  "failed_jobs": 1,
  "average_duration_seconds": 900.5,
  "uptime": "2024-01-01T12:00:00"
}
```

## Configuration

### Environment Variables (.env)

```bash
# API Configuration
API_MODE=true

# Recording Configuration
DURATION_IN_MINUTES=15
MAX_WAITING_TIME_IN_MINUTES=5

# Gladia API Configuration
GLADIA_API_KEY=your-gladia-api-key
DIARIZATION=false

# Custom Configuration
CUSTOM_NAME=Recording Bot

# Logging Configuration
LOG_LEVEL=INFO
```

## Monitoring

### Health Checks

The container includes automatic health checks that verify the API is responding:

```bash
# Check container health
docker ps

# View health check logs
docker logs <container_id>
```

### Logs

Logs are automatically rotated and stored in the `logs/` directory:

```bash
# View API logs
tail -f logs/api.log

# View startup logs
tail -f logs/startup.log
```

## File Structure

```
gmeet-bot/
├── api.py              # FastAPI application
├── gmeet.py            # Core recording logic
├── Dockerfile          # Multi-stage Docker build
├── docker-compose.yml  # Docker Compose configuration
├── entrypoint.sh       # Container startup script
├── build.sh           # Build script
├── .env               # Environment variables
├── env.example        # Environment template
├── recordings/        # Video recordings
├── screenshots/       # Screenshots
└── logs/             # Application logs
```

## Troubleshooting

### Common Issues

1. **Container won't start**

   - Check the `.env` file exists and is properly configured
   - View logs: `docker logs <container_id>`

2. **Health check failing**

   - Ensure the API is responding on port 8000
   - Check application logs in `logs/api.log`

3. **Audio issues**
   - Verify PulseAudio is starting correctly
   - Check startup logs in `logs/startup.log`

### Useful Commands

```bash
# Enter the container
docker exec -it <container_id> /bin/bash

# View real-time logs
docker logs -f <container_id>

# Check container resources
docker stats <container_id>
```

## Development

### Building from Source

```bash
# Clone the repository
git clone <repository-url>
cd gmeet-bot

# Build the image
./build.sh

# Run the API
docker-compose up gmeet-api
```

### Testing the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test recording endpoint
curl -X POST http://localhost:8000/start-recording \
  -H "Content-Type: application/json" \
  -d '{
    "meet_link": "https://meet.google.com/test",
    "email": "test@example.com",
    "password": "password",
    "gladia_api_key": "your-key"
  }'
```

## Security Notes

- The container runs as a non-root user for security
- Environment variables should be kept secure
- API endpoints should be protected in production
- Logs may contain sensitive information

## License

This project is for educational purposes only. Please ensure compliance with Google Meet's terms of service and applicable laws.
