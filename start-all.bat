@echo off
ECHO Starting AgentriX Project...

REM Make sure MongoDB service is running first!

ECHO Starting Streamlit Dashboard...
start "Dashboard" cmd /k "cd backend && .\\.venv\\Scripts\\activate && streamlit run ..\\dashboard.py"

ECHO Starting All Servers (Backend + Frontend)...
start "Servers" cmd /k "cd frontend && npm run dev"

ECHO All processes started in separate windows.