#!/usr/bin/env python3
"""
Celery worker startup script.
Run this script to start the Celery worker process.

Usage:
    python celery_app.py worker --loglevel=info
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Import the Celery instance
from app import celery

if __name__ == '__main__':
    # Start Celery worker
    celery.start()
