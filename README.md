# DS Pet Projects

This repository contains my personal data science and data engineering projects. Each one started as a way to explore a specific tool or technique, then turned into a practical end-to-end workflow using real data sources.

Currently focusing on data ingestion, cleaning, pipeline orchestration, and analytical storage — all built with Python and modern data tools.

### Moscow Apartment Listings Scraper (parcing_flats/)
A scraper for apartment listings on Avito.ru across Moscow districts. It extracts structured data from dynamic real estate pages and prepares it for analysis.

**Implementation**  
- Parsing with **BeautifulSoup** (handling pagination, varying HTML structures)  
- Extensive data cleaning: price normalization, address parsing, feature extraction (floor, total floors, subway distance, etc.)  
- Full containerization using **Docker** for reproducible runs  

**Key takeaways**  
Gained solid experience dealing with unstructured web data, improving scraper reliability, and ensuring data quality in noisy environments.

**Planned improvements**  
Scheduled execution, asynchronous parsing (or Selenium for JS-heavy pages), Telegram alerts on new runs, and persistent storage in an analytical database for trend analysis.

### Spotify Listening History Pipeline (spotify_history/)
An ETL pipeline that extracts extended Spotify listening history, transforms it, and loads it into an analytical store.

**Implementation**  
- Data extraction via **Spotipy** and Spotify API  
- Orchestration and scheduling with **Apache Airflow** (DAGs for extract → transform → load)  
- Storage in **ClickHouse** for high-performance analytical queries  
- Multi-service environment managed through **Docker Compose**  

**Key takeaways**  
Built hands-on experience with production-style data pipelines, task scheduling, container orchestration, and working with column-oriented databases.

**Planned improvements**  
Enrich data with track/artist metadata, add visualization layer (Superset dashboards), and explore incremental/real-time updates.

These projects demonstrate my current capabilities in data collection (web scraping & APIs), cleaning, pipeline design, and deployment — areas I continue to expand as I learn.

Feel free to review the code or reach out with questions !
