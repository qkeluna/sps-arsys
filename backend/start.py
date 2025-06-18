#!/usr/bin/env python3
"""
Startup script for the SPS Appointment System API
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.config import settings


def main():
    """Main function to start the API server"""
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📊 Environment: {settings.environment}")
    print(f"🔧 Debug mode: {settings.debug}")
    print(f"🔗 Database: {settings.database_url[:50]}...")
    print(f"📧 Email service: Resend")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        access_log=settings.debug
    )


if __name__ == "__main__":
    main() 