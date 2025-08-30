import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from clickhouse_driver import Client
from datetime import datetime, timedelta
from urllib.parse import urlparse

default_args = {
    'owner': 'vladsahar',
    'depends_on_past': False,
    'email': 'vladsahar27@gmail.com',
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
    'start_date': datetime(2025, 8, 28, 16, 0),  # 16:00 is before current time 16:38
}

# Schedule: every hour
schedule_interval = "0 * * * *"

# Get the full connection string from Airflow Variable
conn_string = Variable.get("CLICKHOUSE_CONN")

# Parse it
url = urlparse(conn_string)

# Create ClickHouse client
client = Client(
    host=url.hostname,
    port=url.port or 9000,            # default port if not in URI
    user=url.username,
    password=url.password,
    database=url.path.lstrip("/") or "default"
)

# DAG definition
dag = DAG(
    'spotify_history',
    default_args=default_args,
    schedule_interval=schedule_interval,
    catchup=False
)

def fetch_spotify_history(ti):

    # Gets different credentials that can be found in Spotify Dashboard
    sp_oauth = SpotifyOAuth(
    	client_id=Variable.get("VLAD_SPOTIFY_CLIENT_ID"),
    	client_secret=Variable.get("VLAD_SPOTIFY_SECRET_KEY"),
    	redirect_uri=Variable.get("SERVER_LOOPBACK"),
        scope="user-top-read user-read-recently-played"
    )

    # Using this refreshing token we can get a regular one that allows to pull data
    refresh_token = Variable.get("SPOTIFY_REFRESH_TOKEN")

    token_info = sp_oauth.refresh_access_token(refresh_token)
    token = token_info['access_token']
    
    sp = spotipy.Spotify(auth=token)

    # Cycle with the columns that later be parts of the dataframe
    results = sp.current_user_recently_played(limit=50)
    data = []
    for item in results.get("items", []):
        track = item["track"]
        played_at = pd.to_datetime(item["played_at"]).tz_convert("America/Toronto")
        data.append({
            "played_at": played_at.isoformat(),       # convert to string for JSON
            "song": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "date": played_at.date().isoformat()
        })
    df = pd.DataFrame(data)

    # Push dataframe records to XCom
    ti.xcom_push(key="spotify_history", value=df.to_dict(orient="records"))

def load_to_clickhouse(ti):
    records = ti.xcom_pull(key="spotify_history", task_ids="fetch_spotify_history")
    if not records:
        print("No new data to load.")
        return

    df = pd.DataFrame(records)

    # Converting strings to dates
    df['played_at'] = pd.to_datetime(df['played_at'])
    df['date'] = pd.to_datetime(df['date']).dt.date

    # Insert into ClickHouse
    client.execute("INSERT INTO default.music_history VALUES", df.to_dict(orient="records"))

    # Deduplicate by song, album, artist, played_at
    client.execute("""
        OPTIMIZE TABLE default.music_history 
        DEDUPLICATE BY song, album, artist, played_at
    """)

# Airflow tasks
fetch_spotify_history_task = PythonOperator(
    task_id="fetch_spotify_history",
    python_callable=fetch_spotify_history,
    dag=dag,
    do_xcom_push=True
)

load_to_clickhouse_task = PythonOperator(
    task_id="load_to_clickhouse",
    python_callable=load_to_clickhouse,
    dag=dag,
    do_xcom_push=False
)

fetch_spotify_history_task >> load_to_clickhouse_task