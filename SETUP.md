# Store Monitoring Backend - Local Setup Guide

## Requirements

### System Requirements
- Python 3.9 or higher
- PostgreSQL database
- Redis server (optional - system has fallback)
- Git

### Python Dependencies
Create a `requirements.txt` file with these packages:

```txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
celery==5.3.4
redis==5.0.1
pandas==2.2.2
pytz==2024.1
python-dotenv==1.0.1
gunicorn==23.0.0
email-validator==2.1.1
```

## Step-by-Step Local Setup

### 1. Clone the Project
```bash
git clone <your-repository-url>
cd store-monitoring-backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL Installation
1. Install PostgreSQL on your system
2. Create a new database:
```sql
CREATE DATABASE taskWatch;
CREATE USER store_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE taskWatch TO store_user1;
```

#### Option B: Docker PostgreSQL
```bash
docker run --name postgres-store \
  -e POSTGRES_DB=taskWatch \
  -e POSTGRES_USER=store_user1 \
  -e POSTGRES_PASSWORD=123456789 \
  -p 5432:5432 \
  -d postgres:15
```

### 5. Set Up Redis (Optional)

#### Option A: Local Redis Installation
```bash
# Install Redis and start the service
redis-server
```

#### Option B: Docker Redis
```bash
docker run --name redis-store -p 6379:6379 -d redis:alpine
```

**Note:** Redis is optional. The system automatically falls back to synchronous processing if Redis is unavailable.

### 6. Configure Environment Variables
Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://store_user:your_password@localhost:5432/taskWatch
PGHOST=localhost
PGPORT=5432
PGDATABASE=taskWatch
PGUSER=store_user
PGPASSWORD=your_password

# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SESSION_SECRET=your-secret-key-here

# Application Settings
PYTHONPATH=.
```

### 7. Prepare CSV Data Files
Create a `data/` directory and add your CSV files:

```
data/
├── store_status.csv
├── menu_hours.csv
└── timezone.csv
```

#### CSV File Formats:

**store_status.csv:**
```csv
store_id,status,timestamp_utc
1,active,2023-01-25 12:05:19.846849 UTC
2,inactive,2023-01-25 12:10:19.846849 UTC
```

**menu_hours.csv:**
```csv
store_id,dayOfWeek,start_time_local,end_time_local
1,0,09:00:00,22:00:00
1,1,09:00:00,22:00:00
```

**timezone.csv:**
```csv
store_id,timezone_str
1,America/New_York
2,America/Chicago
```

### 8. Initialize the Database
```bash
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
```

### 9. Start the Application

#### Option A: Development Server
```bash
python main.py
```

#### Option B: Production Server with Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

#### Option C: With Celery Worker (if using Redis)
In separate terminals:

Terminal 1 - Start Redis:
```bash
redis-server
```

Terminal 2 - Start Celery Worker:
```bash
celery -A celery_app.celery worker --loglevel=info
```

Terminal 3 - Start Flask App:
```bash
python main.py
```

### 10. Test the Application
Visit `http://localhost:5000` in your browser to access the web interface.

#### API Endpoints:
- `POST /api/trigger_report` - Generate a new report
- `GET /api/get_report/<report_id>` - Check report status
- `GET /api/download_report/<report_id>` - Download completed report

#### Test Report Generation:
```bash
# Trigger a report
   curl -X POST http://localhost:5000/api/trigger_report

# Check report status (use the report_id from above)
curl http://localhost:5000/api/get_report/<report_id>

# Download completed report
curl http://localhost:5000/api/download_report/<report_id>
```

## Project Structure
```
store-monitoring-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── api/
│   │   ├── __init__.py
│   │   └── reports.py       # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_loader.py   # CSV data loading
│   │   └── reporter.py      # Report generation logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── db_models.py     # Database models
│   └── reports/             # Generated report files
├── data/                    # CSV input files
├── static/                  # CSS, JS, images
├── templates/               # HTML templates
├── celery_app.py           # Celery configuration
├── main.py                 # Application entry point
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
└── SETUP.md               # This setup guide
```

## Troubleshooting

### Common Issues:

1. **Database Connection Error:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env file
   - Ensure database and user exist

2. **Redis Connection Error:**
   - Check if Redis is running: `redis-cli ping`
   - The system will automatically fall back to synchronous processing

3. **CSV Loading Error:**
   - Ensure CSV files exist in `data/` directory
   - Check CSV file formats match the expected schema
   - Verify file permissions

4. **Import Errors:**
   - Ensure virtual environment is activated
   - Check all dependencies are installed: `pip list`
   - Verify PYTHONPATH is set correctly

### Check System Status:
```bash
# Test database connection
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); print('Database connection:', db.engine.execute('SELECT 1').scalar())"

# Test Redis connection
redis-cli ping

# Check if all CSV files are loaded
python test_report_generation.py
```

## Support
For additional help, check the application logs and ensure all environment variables are properly configured.