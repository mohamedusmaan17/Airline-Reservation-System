import os
import sys
import traceback

# Add root directory to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import app
except Exception as e:
    from fastapi import FastAPI
    from fastapi.responses import PlainTextResponse
    
    app = FastAPI()
    error_trace = traceback.format_exc()
    
    @app.get("/{path:path}")
    def error_handler(path: str = ""):
        return PlainTextResponse(f"Startup Error:\n{error_trace}", status_code=500)

# Export app for Vercel Serverless Functions
