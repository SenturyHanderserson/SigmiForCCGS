@echo off
title Minecraft Education Edition Installer
color 05
echo.
echo    _____          __         _________ .__  .__        __                  __________                                    
echo   /  _  \  __ ___/  |_  ____ \_   ___ \|  | |__| ____ |  | __ ___________  \______   \___.__.___________    ______ ______
echo  /  /_\  \|  |  \   __\/  _ \/    \  \/|  | |  |/ ___\|  |/ // __ \_  __ \  |    |  _<   |  |\____ \__  \  /  ___//  ___/
echo /    |    \  |  /|  | (  <_> )     \___|  |_|  \  \___|    <\  ___/|  | \/  |    |   \\___  ||  |_> > __ \_\___ \ \___ \ 
echo \____|__  /____/ |__|  \____/ \______  /____/__|\___  >__|_ \\___  >__|     |______  // ____||   __(____  /____  >____  >
echo         \/                           \/             \/     \/    \/                \/ \/     |__|       \/     \/     \/
echo.
echo ------------------------------------------------------------------------------------------------
echo                          MINECRAFT EDUCATION EDITION AUTO INSTALLER
echo ------------------------------------------------------------------------------------------------
echo.
echo This will install everything automatically...
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo █ ERROR: Python is not installed!
    echo.
    echo ➤ Please install Python from:
    echo   https://python.org/downloads
    echo.
    echo ➤ Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)
echo ✓ Python is installed
echo.
echo Installing required packages...
echo This may take a minute...
pip install pyautogui keyboard requests >nul 2>&1
if %errorlevel% neq 0 (
    echo Trying alternative method...
    python -m pip install pyautogui keyboard requests >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✗ Failed to install packages
        echo Please run manually as admin: pip install pyautogui keyboard requests
        pause
        exit /b 1
    )
)
echo ✓ Packages installed successfully!
echo.
echo Downloading AutoClicker...
curl -L -o MinecraftEducation.py "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/MinecraftEducation.py"
if exist MinecraftEducation.py (
    echo ✓ AutoClicker downloaded successfully!
) else (
    echo ✗ Failed to download the script.
    pause
    exit /b 1
)
echo.
echo ⚡ Opening AutoClicker...
echo.
python MinecraftEducation.py
pause
