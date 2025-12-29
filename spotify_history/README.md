# Spotify Listening History Analytics Pipeline

## Project Overview

This project implements an automated ETL pipeline for collecting, storing, and analyzing personal Spotify listening history. Data is extracted from the Spotify Web API, transformed, loaded into an analytical database, and visualized through interactive dashboards.

The solution demonstrates a production-like data workflow suitable for music consumption insights, including top artists, albums, tracks, and temporal listening patterns.

## Architecture

- **Apache Airflow** – Orchestrates the end-to-end ETL process (extraction, transformation, loading)
- **Spotipy** – Python client for Spotify Web API integration
- **ClickHouse** – Columnar database optimized for high-performance analytical queries on large datasets
- **Apache Superset** – BI tool for building dashboards and exploring stored data
- **Docker & Docker Compose** – Containerization and service orchestration for reproducible deployment

## Data Collected

For each played track:
- Playback timestamp
- Track name
- Artist(s)
- Album
- Duration and other metadata

## Key Features & Dashboards

Once loaded into ClickHouse and connected to Superset:
- Timeline of recently played tracks
- Rankings of top artists, albums, and songs (all-time or filtered by period)
- Daily/weekly/monthly listening trends
- Custom explorations via SQL queries in Superset

## Prerequisites

- Docker and Docker Compose
- Spotify Developer Account and registered application [](https://developer.spotify.com/dashboard/)

## Spotify API Setup

The project uses OAuth 2.0 with refresh token flow for secure, long-term access.

1. **Create a Spotify App**
   - Log in to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
   - Create a new app
   - Note **Client ID** and **Client Secret**
   - Add a Redirect URI (e.g., `http://localhost:7777/callback`)

2. **Generate Refresh Token (One-Time)**
   - Run the provided `local_script.ipynb` notebook
   - Follow the authentication flow in your browser
   - Grant required permissions (`user-read-recently-played`, `user-library-read`, etc.)
   - Extract the refresh token from the output

3. **Store Credentials**
   Create a `.env` file in the project root:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:7777/callback
   SPOTIFY_REFRESH_TOKEN=your_refresh_token
   ```
## Deployment Instructions
1. Start Services
```bash
docker-compose up -d --build
```
2. Verify Containers
```bash
docker ps
```
3. Access Tools
- Airflow UI: http://localhost:8080 (default: airflow/airflow)
- Superset UI: http://localhost:8088
- ClickHouse: accessible via port 9000 (TCP) and 8123 (HTTP)
4. Initialize Superset
```bash
docker exec -it superset superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@example.com \
  --password your_password

docker exec -it superset superset db upgrade
docker exec -it superset superset init
```
5. Install ClickHouse Driver in Superset
```bash
docker exec superset pip install clickhouse-sqlalchemy
```
After setup, connect Superset to ClickHouse using the container network and credentials.
The Airflow DAG will automatically:

- Refresh the access token
- Pull extended listening history
- Load data into ClickHouse

## Repository Contents

- `requirements.txt` — Python dependencies (Spotipy, Airflow providers, etc.)
- `Dockerfile` — Custom Airflow image with required packages pre-installed
- `docker-compose.yml` — Orchestrates the full stack (Airflow, ClickHouse, Superset)
- `dags/` — Airflow DAG definitions for extraction, transformation, and loading
- `local_script.ipynb` — Jupyter notebook for one-time generation of Spotify refresh token

This project highlights practical skills in API integration, ETL orchestration, containerized deployment, and analytical database management — foundational competencies for data engineering and analytics roles.

Feedback and contributions are welcome.
