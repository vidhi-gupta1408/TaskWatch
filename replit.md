# Store Monitoring Backend Application

## Overview

A comprehensive Python backend application for monitoring restaurant store uptime and downtime. The system processes store status data to generate detailed reports showing business hours compliance and operational metrics. Built with a trigger-and-poll architecture for scalable background report generation, the application handles complex timezone conversions and business logic for accurate uptime/downtime calculations across multiple restaurant locations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask** as the main web framework with Blueprint-based modular architecture
- Application factory pattern for clean initialization and configuration management
- Template-based web interface for testing and monitoring functionality

### Database Design
- **SQLite** with SQLAlchemy ORM for local development and data persistence
- Four main entities:
  - `StoreStatus`: Timestamped active/inactive status observations
  - `BusinessHours`: Store operating hours by day of week
  - `Timezone`: Store-specific timezone information
  - `Report`: Generated report metadata and status tracking

### Background Task Processing
- **Celery** with Redis message broker for asynchronous report generation
- Trigger-and-poll architecture: POST `/trigger_report` starts background task, GET `/get_report` polls for completion
- Custom task class with Flask app context integration for database operations
- Task result persistence and status tracking

### Data Processing Pipeline
- **Pandas** for CSV data ingestion and manipulation
- Robust CSV parsing with multiple timestamp format support
- Data interpolation logic for filling gaps in status observations
- Timezone-aware calculations using pytz library

### Business Logic Engine
- Complex uptime/downtime calculations considering business hours
- Timezone conversion between UTC storage and local business time
- Interpolation algorithms for estimating status during data gaps
- Multiple reporting periods: last hour, last day, last week

### API Architecture
- RESTful endpoints for report management
- JSON responses with comprehensive error handling
- File serving capability for generated CSV reports
- Web interface with real-time status polling

### Data Storage Strategy
- UUID-based store identifiers for production-scale data handling
- Indexed database columns for efficient querying by store_id and timestamp
- Optimized queries for time-range filtering and aggregation
- CSV export functionality for report delivery
- Database session management with proper cleanup
- Support for large datasets (143K+ status records, 35K+ business hours, 4K+ timezones)

## External Dependencies

### Infrastructure Services
- **Redis**: Message broker for Celery task queue and result backend
- **SQLite**: Local database for development and demonstration

### Python Libraries
- **Flask**: Web framework and API development
- **SQLAlchemy**: Database ORM and query builder
- **Celery**: Distributed task queue for background processing
- **Pandas**: Data manipulation and CSV processing
- **pytz**: Timezone handling and conversions
- **python-dotenv**: Environment variable management

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for interface elements
- **Vanilla JavaScript**: Client-side interactivity and AJAX polling

### Development Tools
- **Logging**: Comprehensive application logging for debugging and monitoring
- **UUID**: Unique report identifier generation
- **CSV**: Built-in Python library for report file generation

### File System Integration
- CSV data ingestion from `/data` directory
- Report generation to `/app/reports` directory
- Template rendering from `/templates` directory
- Static asset serving from `/static` directory