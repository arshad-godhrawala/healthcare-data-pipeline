"""
Script to run the Healthcare Pipeline API server.
"""

import sys
import os
import uvicorn

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

if __name__ == "__main__":
    print("🚀 Starting Healthcare Pipeline API Server...")
    print("📖 API Documentation will be available at:")
    print("   - Swagger UI: http://localhost:8002/docs")
    print("   - ReDoc: http://localhost:8002/redoc")
    print("=" * 60)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 