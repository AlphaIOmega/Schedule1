@echo off
echo Starting Schedule I Product Viewer...

REM Check if Flask is installed
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
  echo Flask not found. Installing Flask...
  pip install flask
  if %errorlevel% neq 0 (
    echo Failed to install Flask. Please install it manually using "pip install flask"
    pause
    exit /b 1
  )
)

REM Start the Flask application
python app.py

REM If there was an error, pause to show the message
if %errorlevel% neq 0 (
  echo An error occurred while starting the application.
  pause
)