"""
Airline Reservation System — One-command start.

Usage:
    python run.py

Opens the app at http://localhost:8000
API docs at http://localhost:8000/docs
"""
import uvicorn

if __name__ == "__main__":
    print("\n[+] Airline Reservation System")
    print("-" * 40)
    print("  App:   http://localhost:8000")
    print("  Docs:  http://localhost:8000/docs")
    print("-" * 40)
    print()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
