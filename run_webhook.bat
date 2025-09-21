@echo off
echo Webhook Redirector
echo ==================

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set default environment variables (modify as needed)
set REDIRECT_URL=http://localhost:8080/webhook
set LISTEN_PORT=5000

echo.
echo Starting webhook listener...
echo Redirecting requests to: %REDIRECT_URL%
echo Listening on port: %LISTEN_PORT%
echo.

python app.py

echo.
echo Webhook listener stopped.
pause