# Enterprise Retail Sales & Revenue Analytics Pipeline

An end-to-end data pipeline and BI solution designed to ingest, validate, and analyze enterprise sales transactions to extract actionable financial metrics.

## Architecture Overview
[ Raw CSV Data ] -> [ Python ETL Pipeline ] -> [ PostgreSQL Database ] -> [ Power BI Dashboard ]

## Tech Stack
* Language: Python 3.10
* Database: PostgreSQL
* Data Processing: Pandas, NumPy, SQLAlchemy
* CI/CD Automation: GitHub Actions
* Visualization: Power BI
* Containerization: Docker & Docker Compose

## Power BI Dashboard Preview
* Executive Revenue Overview: Tracking MoM revenue growth and regional performance.
* Customer & Product KPIs: Breakdown of top-performing categories and customer retention metrics.

## Getting Started

### Prerequisites
* Docker Desktop installed and running.
* Git installed.

### Quick Start with Docker Compose
1. Clone the repository:
   git clone https://github.com/Vijayanand957/enterprise-sales-analytics.git
   cd enterprise-sales-analytics

2. Start the PostgreSQL database container:
   docker-compose up -d

3. Install Python dependencies locally:
   pip install -r requirements.txt

4. Run the ETL Pipeline:
   python etl_pipeline.py

5. Stop Containers:
   docker-compose down
