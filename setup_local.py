#!/usr/bin/env python3
"""
Local setup script for Store Monitoring Backend Application
Run this script to initialize the database and verify the setup.
"""

import os
import sys
from dotenv import load_dotenv

def main():
    print("🏪 Store Monitoring Backend - Local Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = ['DATABASE_URL', 'PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the required variables.")
        print("See SETUP.md for details.")
        return False
    
    print("✅ Environment variables loaded")
    
    try:
        # Import and create app
        from app import create_app, db
        
        print("📦 Creating Flask application...")
        app = create_app()
        
        with app.app_context():
            print("🗄️  Initializing database...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test database connection
            result = db.session.execute(db.text('SELECT 1')).scalar()
            if result == 1:
                print("✅ Database connection verified")
            
            # Load CSV data
            print("📊 Loading CSV data...")
            from app.core.data_loader import load_all_data
            load_all_data()
            print("✅ CSV data loaded successfully!")
            
            # Test report generation
            print("📋 Testing report generation...")
            from app.core.reporter import generate_store_metrics, get_current_timestamp
            
            current_time = get_current_timestamp()
            metrics = generate_store_metrics(current_time)
            
            print(f"✅ Report generation test completed - {len(metrics)} stores processed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r local_requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the application: python main.py")
    print("2. Visit http://localhost:5000 in your browser")
    print("3. Test report generation through the web interface")
    
    # Check Redis (optional)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection available - background tasks enabled")
    except:
        print("⚠️  Redis not available - using synchronous fallback")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)