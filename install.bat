@echo off
echo ========================================================
echo  Starting automated installation for Facebook Extractor 
echo ========================================================

echo =^> Checking for Winget...
where winget >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Winget is not installed on this system.
    echo Please install Python 3 and Git manually, then run this script again.
    pause
    exit /b 1
)

echo =^> Checking for Git...
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo =^> Git not found. Installing Git quietly...
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
) else (
    echo =^> Git is already installed.
)

echo =^> Checking for Python...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo =^> Python not found. Installing Python 3 quietly...
    winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements --silent
    :: Add delay to ensure PATH is somewhat updated or available
    timeout /t 5 /nobreak >nul
) else (
    echo =^> Python is already installed.
)

echo =^> Setting up Python virtual environment...
python -m venv venv
if not exist "venv\Scripts\activate.bat" (
    echo Failed to create virtual environment. Make sure Python is in your PATH.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo =^> Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ========================================================
echo  Installation complete! 
echo  You can now run the tool using:
echo  venv\Scripts\python fb_media_extractor.py ^<facebook_url^>
echo ========================================================
pause
