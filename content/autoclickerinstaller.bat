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

:MAIN
echo This will install everything automatically...
echo.
timeout /t 2
:CHECK_PYTHON
echo Checking for Python installation...
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
    echo ➤ After installing Python, run this installer again.
    echo.
    set /p choice="Press R to retry after installing Python, or any other key to exit: "
    if /i "%choice%"=="R" goto CHECK_PYTHON
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ %PYTHON_VERSION% detected

:INSTALL_PACKAGES
echo.
echo Installing required packages...
echo This may take a minute...
echo.

:: Try multiple installation methods
set INSTALL_SUCCESS=0

echo Attempting method 1: pip install...
pip install pyautogui keyboard requests >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Packages installed successfully via pip!
    set INSTALL_SUCCESS=1
    goto DOWNLOAD_SCRIPT
)

echo Method 1 failed, trying method 2: python -m pip install...
python -m pip install pyautogui keyboard requests >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Packages installed successfully via python -m pip!
    set INSTALL_SUCCESS=1
    goto DOWNLOAD_SCRIPT
)

echo Method 2 failed, trying method 3: pip install with --user...
pip install --user pyautogui keyboard requests >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Packages installed successfully via pip --user!
    set INSTALL_SUCCESS=1
    goto DOWNLOAD_SCRIPT
)

echo Method 3 failed, trying method 4: python -m pip install with --user...
python -m pip install --user pyautogui keyboard requests >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Packages installed successfully via python -m pip --user!
    set INSTALL_SUCCESS=1
    goto DOWNLOAD_SCRIPT
)

:: If all methods failed
echo.
echo █ WARNING: Could not install packages automatically.
echo.
echo ➤ You can still try to run the program, but it may not work properly.
echo ➤ Alternatively, you can manually install the packages:
echo   Open Command Prompt as Administrator and run:
echo   pip install pyautogui keyboard requests
echo.
set /p choice="Press C to continue anyway, R to retry installation, or any other key to exit: "
if /i "%choice%"=="R" goto INSTALL_PACKAGES
if /i "%choice%"=="C" (
    set INSTALL_SUCCESS=0
    goto DOWNLOAD_SCRIPT
)
exit /b 1

:DOWNLOAD_SCRIPT
echo.
echo Downloading Minecraft Education Edition...
echo.

:: Try multiple download methods
set DOWNLOAD_SUCCESS=0

:: Method 1: Using curl if available
curl --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Attempting download with curl...
    curl -L -o MinecraftEducation.py "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/MinecraftEducation.py" >nul 2>&1
    if %errorlevel% equ 0 (
        if exist MinecraftEducation.py (
            echo ✓ Script downloaded successfully via curl!
            set DOWNLOAD_SUCCESS=1
            goto RUN_SCRIPT
        )
    )
)

:: Method 2: Using powershell
echo Trying download with PowerShell...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/MinecraftEducation.py' -OutFile 'MinecraftEducation.py'" >nul 2>&1
if %errorlevel% equ 0 (
    if exist MinecraftEducation.py (
        echo ✓ Script downloaded successfully via PowerShell!
        set DOWNLOAD_SUCCESS=1
        goto RUN_SCRIPT
    )
)

:: Method 3: Using bitsadmin
echo Trying download with BITSAdmin...
bitsadmin /transfer myDownloadJob /download /priority normal "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/MinecraftEducation.py" "MinecraftEducation.py" >nul 2>&1
if exist MinecraftEducation.py (
    echo ✓ Script downloaded successfully via BITSAdmin!
    set DOWNLOAD_SUCCESS=1
    goto RUN_SCRIPT
)

:: If download failed
echo.
echo █ WARNING: Could not download the script automatically.
echo.
echo ➤ The installer will use a local version if available.
echo ➤ If the program doesn't work, please download the script manually.
echo.
if exist MinecraftEducation.py (
    echo ✓ Found local script file, using that instead.
    set DOWNLOAD_SUCCESS=1
) else (
    echo ✗ No local script found.
    set DOWNLOAD_SUCCESS=0
)

:RUN_SCRIPT
echo.
echo ⚡ Starting Minecraft Education Edition...
echo.

if exist MinecraftEducation.py (
    echo Running the application...
    echo If a window doesn't appear, please wait a moment...
    echo.
    
    :: Try to run the script
    python MinecraftEducation.py
    
    if %errorlevel% neq 0 (
        echo.
        echo █ The application encountered an error.
        echo.
        echo ➤ This might be because:
        echo   - Required packages weren't installed properly
        echo   - The script file is corrupted
        echo   - Python is not configured correctly
        echo.
        echo ➤ Solutions to try:
        echo   1. Run the installer again as Administrator
        echo   2. Manually install: pip install pyautogui keyboard requests
        echo   3. Download the script file manually
        echo.
    ) else (
        echo.
        echo ✓ Application closed successfully.
    )
) else (
    echo.
    echo █ ERROR: No script file found to run.
    echo.
    echo ➤ Please download MinecraftEducation.py manually and place it
    echo   in the same folder as this installer, then run this again.
    echo.
)

:END_MENU
echo.
echo ------------------------------------------------------------------------------------------------
echo.
set /p choice="Press R to restart the installer, A to try manual installation, or any other key to exit: "

if /i "%choice%"=="R" (
    echo.
    echo Restarting installer...
    timeout /t 2 /nobreak >nul
    goto MAIN
)

if /i "%choice%"=="A" (
    echo.
    echo Opening manual installation instructions...
    echo.
    echo MANUAL INSTALLATION STEPS:
    echo 1. Open Command Prompt as Administrator
    echo 2. Run: pip install pyautogui keyboard requests
    echo 3. Download MinecraftEducation.py manually
    echo 4. Double-click MinecraftEducation.py to run
    echo.
    pause
)

echo.
echo Thank you for using Minecraft Education Edition!
echo.
pause
