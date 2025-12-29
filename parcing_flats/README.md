# Moscow Apartment Listings Analyzer & Telegram Notifier

## Project Overview

This project addresses a practical real estate challenge: identifying promising apartment listings quickly on platforms like Avito.ru. The system automates data collection, processing, storage, and delivery by posting curated Moscow apartment deals to a Telegram channel via a custom bot.

**Telegram Channel**: [t.me/moscow_flats_bot](https://t.me/moscow_flats_bot)

**Core Benefits**
- Instant notifications of new or high-potential listings
- Convenient access within Telegram
- Interactive feedback (e.g., emoji reactions for bookmarking)

The architecture forms a complete data pipeline: web scraping → cleaning → analytical storage → orchestration → notification, with optional visualization.

## Key Technologies

**Infrastructure & Orchestration**
- Docker & Docker Compose – reproducible environments
- Apache Airflow – workflow scheduling and DAG management
- ClickHouse – column-oriented database for fast analytical queries
- Apache Superset – data exploration and dashboarding

**Python Libraries**
- BeautifulSoup4 – web scraping and HTML parsing
- Pandas – data cleaning and transformation
- ClickHouse-Driver / ClickHouse-SQLAlchemy – database connectivity
- Python-Telegram-Bot – formatted message delivery
- Hyper – HTTP client
- Emoji – message enhancement

Full dependencies are listed in `requirements.txt`.

**Additional Tools**
- Git – version control
- Basic Linux command-line operations

## Architecture & Workflow

1. **Ingestion** – Scheduled scraping of Avito.ru listings using BeautifulSoup
2. **Processing** – Normalization and cleaning with Pandas (price conversion, address parsing, missing values)
3. **Storage** – Loading structured data into ClickHouse
4. **Notification** – Selective high-value listings sent to Telegram
5. **Orchestration** – Apache Airflow DAG managing the full ETL + notification flow
6. **Exploration** – Superset connected to ClickHouse for ad-hoc analysis

## Setup Instructions

Instructions are optimized for Debian-based systems. Familiarity with Docker and command-line basics is recommended.

### Prerequisites
```bash
docker ps          # Verify Docker
git --version      # Verify Git
```
1. Prepare Shared Resources
```bash
docker volume create flats_data_volume
docker network create flats_network
```
2. Launch Apache Superset
```bash
docker run -d --net flats_network -p 8088:8088 --name superset apache/superset

docker exec -it superset superset fab create-admin \
  --username admin --firstname Superset --lastname Admin \
  --email admin@superset.com --password your_password

docker exec -it superset superset db upgrade
docker exec -it superset superset init
```
3. Launch ClickHouse
```bash
docker run -d --name clickhouse --net flats_network \
  -v flats_data_volume:/var/lib/clickhouse \
  -p 9000:9000 -p 8123:8123 yandex/clickhouse-server
```
4. Connect ClickHouse to Superset
```bash
docker exec superset pip install clickhouse-sqlalchemy
```
5. Clone Repository & Build Custom Airflow Image
```bash
git clone https://github.com/0n1xx/DS_pet_projects.git
cd DS_pet_projects/parcing_flats
docker build . --tag custom-airflow:latest
```
6. Deploy Airflow
```bash
docker-compose up -d
```
7. Connect Networks
```bash
docker network connect flats_network airflow_airflow-scheduler_1
docker network connect flats_network airflow_airflow-worker_1
# Repeat for additional Airflow containers if needed
```
8. Configure Airflow Variables
Set via Airflow UI or environment:

- AIRFLOW_OWNER
- CLICKHOUSE_HOST
- TG_TOKEN_AVITO
- CHAT_ID_MOSCOW_FLATS
- MAIL_TO_REPORT

The DAG will then execute automatically and begin posting listings.

## Learning Resources

- Airflow XCom usage: [YouTube Video](https://www.youtube.com/watch?v=8veO7-SN5ZY)  
- Custom Airflow Docker images: [YouTube Video](https://www.youtube.com/watch?v=0UepvC9X4HY)  

**Recommended courses (Russian-language)**  
- Docker fundamentals: [karpov.courses/docker](https://karpov.courses/docker)  
- Web scraping: [stepik.org/course/104774](https://stepik.org/course/104774)  
- SQL for data analysis: [karpov.courses/simulator-sql](https://karpov.courses/simulator-sql)  

This project showcases end-to-end data engineering skills: robust scraping, pipeline orchestration, containerization, analytical storage, and real-time notification delivery.

Contributions and feedback are welcome.

— Vlad Sakharov  
Data Engineer / Data Scientist
