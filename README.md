# gmeet-bot

This example project will help you record and transcribe using gladia a google meet meeting from a container with a audio and video using virtual sound card (pulseaudio) and screen recording with Xscreen.

One of the main challenge is to record the session without a sound card using audio loop sink and not being flagged by the meeting provider (in this case google meet).

This project is a proof of concept with limited support and is not meant for production grade usage.

## Features

- **Direct Mode**: Run the bot directly with environment variables (original functionality)
- **API Mode**: Accept HTTP requests to start recording sessions with parameters
- **Background Processing**: Jobs run in the background with status tracking
- **File Management**: Automatically saves video recordings and transcriptions

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

### 2. Build Docker Image

```bash
# Build automatique avec détection de plateforme
./build.sh
```

## Usage

### Direct Mode (Original)

```bash
docker run -it \
    -e GMEET_LINK=https://meet.google.com/my-gmeet-id \
    -e GMAIL_USER_EMAIL=myuser1234@gmail.com \
    -e GMAIL_USER_PASSWORD=my_gmail_password \
    -e DURATION_IN_MINUTES=1 \
    -e GLADIA_API_KEY=YOUR_GLADIA_API_KEY \
    -e GLADIA_DIARIZATION=true \
    -e MAX_WAIT_TIME_IN_MINUTES=2 \
    -v $PWD/recordings:/app/recordings \
    -v $PWD/screenshots:/app/screenshots \
    gmeet
```

### API Mode (New)

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
    -e API_MODE=true \
    -p 8000:8000 \
    -v $PWD/recordings:/app/recordings \
    -v $PWD/screenshots:/app/screenshots \
    gmeet
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
  "custom_name": "Optional Custom Name"
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
  "transcript_path": null
}
```

### Get Job Status

**GET** `/job/{job_id}`

Get the current status of a recording job.

**Response:**

```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "message": "Recording completed successfully",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:15:00",
  "video_path": "recordings/output.mp4",
  "transcript_path": "recordings/transcript.json"
}
```

### List All Jobs

**GET** `/jobs`

Get a list of all jobs.

### Delete Job

**DELETE** `/job/{job_id}`

Delete a job and stop running process if any.

### Health Check

**GET** `/health`

Check if the API is running.

### Statistics

**GET** `/stats`

Get API statistics (jobs count, average duration, etc.).

## Scripts Utilitaires

### Configuration

```bash
# Créer .env depuis env.example
python setup_env.py --create

# Valider la configuration
python setup_env.py --validate
```

### Build et Déploiement

```bash
# Build automatique avec détection de plateforme
./build.sh
```

### Test et Exemples

```bash
# Test interactif de l'API
python test_api.py

# Exemples d'utilisation
python example_usage.py
```

## Example Usage with curl

### Start a recording:

```bash
curl -X POST "http://localhost:8000/start-recording" \
     -H "Content-Type: application/json" \
     -d '{
         "meet_link": "https://meet.google.com/my-gmeet-id",
         "email": "myuser1234@gmail.com",
         "password": "my_gmail_password",
         "duration_minutes": 15,
         "gladia_api_key": "YOUR_GLADIA_API_KEY"
     }'
```

### Check job status:

```bash
curl "http://localhost:8000/job/{job_id}"
```

### List all jobs:

```bash
curl "http://localhost:8000/jobs"
```

## Job Status Values

- `starting`: Job has been created and is initializing
- `running`: Bot is joining the Google Meet
- `completed`: Recording finished successfully
- `failed`: Recording failed with an error
- `cancelled`: Job was cancelled by user

## Output Files

When a recording is completed successfully, the following files are created:

- `recordings/output.mp4`: Video recording of the meeting
- `recordings/transcript.json`: Transcription data from Gladia API

## Environment Variables

### API Mode

- `API_MODE`: Set to "true" to enable API mode

### Recording Parameters

- `GMEET_LINK`: Google Meet URL
- `GMAIL_USER_EMAIL`: Gmail account email
- `GMAIL_USER_PASSWORD`: Gmail account password
- `DURATION_IN_MINUTES`: Recording duration in minutes
- `MAX_WAITING_TIME_IN_MINUTES`: Maximum time to wait in lobby
- `GLADIA_API_KEY`: Your Gladia API key for transcription
- `DIARIZATION`: Enable/disable speaker diarization
- `CUSTOM_NAME`: Custom name to use when joining the meeting

## API Documentation

When running in API mode, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
