#!/usr/bin/env python3
"""
Simple system check for Healthcare Data Pipeline
"""
import sys
import os
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_api():
    """Check if API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running (http://localhost:8000)")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return False

def check_dashboard():
    """Check if dashboard is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard is running (http://localhost:3000)")
            return True
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard not accessible: {e}")
        return False

def check_database():
    """Check database connections"""
    try:
        from src.database.postgres_operations import create_postgres_connection
        engine, SessionLocal = create_postgres_connection()
        print("✅ PostgreSQL connection working")
        
        from src.database.influx_operations import create_influx_connection
        client, bucket = create_influx_connection()
        print("✅ InfluxDB connection working")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Run system checks"""
    print("🔍 Healthcare Data Pipeline System Check")
    print("=" * 40)
    
    # Check databases
    db_ok = check_database()
    
    # Check API
    api_ok = check_api()
    
    # Check dashboard
    dashboard_ok = check_dashboard()
    
    print("\n" + "=" * 40)
    print("📊 SUMMARY:")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"API: {'✅' if api_ok else '❌'}")
    print(f"Dashboard: {'✅' if dashboard_ok else '❌'}")
    
    if all([db_ok, api_ok, dashboard_ok]):
        print("\n🎉 All systems are running properly!")
        print("\n📋 Access URLs:")
        print("- API: http://localhost:8000")
        print("- API Docs: http://localhost:8000/docs")
        print("- Dashboard: http://localhost:3000")
    else:
        print("\n⚠️  Some systems are not running properly.")
        print("To start the system:")
        print("1. Start API: python run_api.py")
        print("2. Start Dashboard: python run_dashboard.py")

if __name__ == "__main__":
    main() 