# 🎵 Spotify Statistics

### 📌 Project Overview:

This project automates the collection and analysis of listening history from the Spotify API.
Data about tracks, albums, and artists is ingested into ClickHouse using Airflow, and then visualized in Apache Superset.

### ⚙️ Architecture:

- Airflow – manages ETL processes
- Spotipy – Python SDK for Spotify API integration
- ClickHouse – analytics-optimized data warehouse
- Apache Superset – dashboarding and visualization 
- Docker Compose – manages containerized services

### 🔑 Spotify Authentication:

The project uses OAuth2 for Spotify API access: A refresh token is obtained manually once. This refresh token is stored securely in Airflow Variables along with client_id, client_secret, and redirect_uri. Airflow automatically uses the refresh token to generate short-lived access tokens and pull listening data.

### 📊 Data Collected:
- Played Time 
- Artist
- Album
- Song
- Date

### 📈 Dashboards:

Data stored in ClickHouse is visualized through Superset dashboards, including:
- Recently played timeline
- Top artists / albums ranking
- Daily listening trends

### ✅ Spotify API prerequirements: 

Before you can run this project and access your Spotify listening data, you need to set up Spotify API credentials and authentication.

1. Create a Spotify Developer Account 
   1. Go to Spotify Developer Dashboard 
   2. Log in with your Spotify account 
   3. Click Create an App 
   4. Give it a name (e.g., SpotifyStatsPipeline)

2. Configure Redirect URI 
   1. In your app settings, find Redirect URIs 
   2. Add your redirect URI (example: http://localhost:7777/callback or your server callback URL)
   3. Save changes

3. Get Your Credentials 
   1. Copy the following values from your app settings:
      - Client ID 
      - Client Secret 
   2. These will be used in Airflow Variables.

4. Generate a Refresh Token

The Spotify API requires OAuth2. Since access tokens expire quickly, you need a refresh token to keep renewing them automatically.

Steps:

1. Use a [local script](local_script.ipynb) (with Spotipy
) to authenticate manually once. 
2. The script will open a browser asking for Spotify login & permissions. 
3. Approve access and copy the redirected URL. 
4. Extract the refresh token from the script’s output. 
5. You will only need to do this step once. 
6. Store Credentials in Airflow

In Airflow UI → Admin → Variables, add the following:

| Key                   | Value (example)                |
|------------------------|--------------------------------|
| SPOTIFY_CLIENT_ID      | your_client_id                 |
| SPOTIFY_CLIENT_SECRET  | your_client_secret             |
| SPOTIFY_REDIRECT_URI   | http://localhost:7777/callback |
| SPOTIFY_REFRESH_TOKEN  | your_refresh_token             |


Make sure values are entered without quotes ' '.

⚠️ Note: Without these steps, Airflow cannot authenticate with Spotify and your DAGs will fail.

### ⚙️ Docker part:

Make sure you have installed:

- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/)  
- A **Spotify Developer Account** with an app created ([Guide](https://developer.spotify.com/dashboard/))  

This repository also includes:

- [requirements.txt](requirements.txt) → Python dependencies (Spotipy, Airflow extras, etc.)  
- [Dockerfile](Dockerfile) → custom Airflow image with dependencies  
- [docker-compose.yml](docker-compose.yml) → services for Airflow, ClickHouse, and Superset 

---

#### 🔑 Environment Variables

Before running, create a `.env` file in the project root with your credentials:

| Key                   | Value (example)                  |
|-----------------------|----------------------------------|
| SPOTIFY_CLIENT_ID     | your_client_id                   |
| SPOTIFY_CLIENT_SECRET | your_client_secret               |
| SPOTIFY_REDIRECT_URI  | http://localhost:7777/callback   |
| SPOTIFY_REFRESH_TOKEN | your_refresh_token               |

---

### Airflow:

1️⃣ Build and start all services:
```bash
docker-compose up -d --build
```

2️⃣ Check running containers:

```bash
docker ps
```

3️⃣ Starting all containers:
```bash
docker compose up -d
```

### Clickhouse:

1️⃣ Pull the imagine:

```bash
docker pull clickhouse/clickhouse-server:latest
```

2️⃣ Start your database container:

```bash
docker run -d \
--name your_name \ 
--net=your_network_name \
-v your_volume:/var/lib/clickhouse \
-p 9000:9000 \
-p 8123:8123 \
-e CLICKHOUSE_USER=your_login \
-e CLICKHOUSE_PASSWORD=your_password \
clickhouse/clickhouse-server
```

### Superset:

1️⃣ Pull the imagine:

```bash
docker pull apache/superset:4.0.0
```

2️⃣ Start your bi container:

```bash
docker run -d \
  --name your_name \
  --network your_network_name \
  -p 8088:8088 \
  -e SUPERSET_HOME=/app/superset_home \
  -e SUPERSET_SECRET_KEY="" \
  apache/superset:4.0.0
```

3️⃣ Create an admin user and run updates after:

```bash
docker exec -it superset superset fab create-admin \
    --username your_username \
    --firstname your_first_name \
    --lastname your_last_name \
    --email your_email \
    --password your_password
```

```bash
docker exec -it superset superset db upgrade;
docker exec -it superset superset init
```

4️⃣ Install clickhouse driver for Superset:

```bash
docker exec superset pip install clickhouse-sqlalchemy
```
