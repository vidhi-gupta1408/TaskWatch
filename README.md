# Store Monitoring Backend Application

A comprehensive Python backend application for monitoring restaurant store uptime and downtime with trigger-and-poll architecture, featuring CSV data ingestion, complex timezone handling, and background task processing.

## Features

- **Real-time Store Monitoring**: Track store uptime/downtime across multiple locations
- **CSV Data Processing**: Automated ingestion of store status, business hours, and timezone data
- **Complex Business Logic**: Accurate uptime calculations considering business hours and timezones
- **Background Processing**: Asynchronous report generation with Celery and Redis
- **Fallback System**: Automatic synchronous processing when Redis is unavailable
- **RESTful API**: Complete API endpoints for report management
- **Web Interface**: User-friendly interface for testing and monitoring

## Quick Start

### 1. Install Dependencies
```bash
pip install -r local_requirements.txt
```

### 2. Set Up Database
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
# Create PostgreSQL database named 'taskWatch'
```

### 3. Initialize Application
```bash
python setup_local.py
```

### 4. Start Application
```bash
python main.py
```

Visit `http://localhost:5000` to access the web interface.

## Detailed Setup

For complete setup instructions including database configuration, Redis setup, and troubleshooting, see [SETUP.md](SETUP.md).

## CSV Data Format

Place your CSV files in the `data/` directory:

- `store_status.csv` - Store activity observations
- `menu_hours.csv` - Business hours by store and day
- `timezone.csv` - Store timezone information

## API Endpoints

- `POST /api/trigger_report` - Generate new report
- `GET /api/get_report/<report_id>` - Check report status  
- `GET /api/download_report/<report_id>` - Download CSV report

## Architecture

- **Backend**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL for data persistence
- **Task Queue**: Celery with Redis message broker
- **Data Processing**: Pandas for CSV manipulation
- **Timezone Handling**: pytz for accurate conversions

## Project Structure

```
├── app/                 # Main application package
│   ├── api/            # REST API endpoints
│   ├── core/           # Business logic and data processing
│   ├── models/         # Database models
│   └── reports/        # Generated report files
├── data/               # CSV input files
├── static/             # Web assets
├── templates/          # HTML templates
├── main.py            # Application entry point
└── setup_local.py     # Local setup script
```
