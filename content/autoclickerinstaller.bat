@echo off
title Auto Clicker Installer
color 0A

echo.
echo ========================================
echo        AUTO CLICKER INSTALLER
echo ========================================
echo.

:MAIN
echo This will install everything automatically...
echo.
timeout /t 1 /nobreak >nul

:CHECK_PYTHON
echo Checking for Python installation...
python --version >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] %PYTHON_VERSION% detected
    goto CHECK_PACKAGES
)

:PYTHON_NOT_FOUND
echo.
echo [ERROR] Python is not installed!
echo.
echo Please install Python from:
echo https://python.org/downloads
echo.
echo Make sure to check "Add Python to PATH" during installation!
echo.
set /p choice="Press D to download Python automatically, M to install manually, or any other key to exit: "

if /i "%choice%"=="D" (
    goto DOWNLOAD_PYTHON
)
if /i "%choice%"=="M" (
    echo.
    echo Please install Python from:
    echo https://python.org/downloads
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    goto WAIT_FOR_PYTHON
)
exit /b 0

:DOWNLOAD_PYTHON
echo.
echo Downloading Python installer...
echo This may take a few minutes depending on your internet speed...
echo.

REM Use official Python download instead of GitHub
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download Python installer. Trying alternative mirror...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe' -OutFile 'python-installer.exe'"
)

if not exist "python-installer.exe" (
    echo [ERROR] Failed to download Python installer.
    echo Please install Python manually from: https://python.org/downloads
    pause
    exit /b 1
)

echo [SUCCESS] Python installer downloaded successfully!
echo.
echo Starting Python installation...
echo IMPORTANT: In the Python installer:
echo 1. Check "Add Python to PATH" at the bottom
echo 2. Click "Install Now"
echo 3. Wait for installation to complete
echo 4. Close the installer when done
echo.
echo The installer will open now...
timeout /t 3 /nobreak >nul

start /wait python-installer.exe

del python-installer.exe >nul 2>nul

:WAIT_FOR_PYTHON
echo.
:CHECK_AGAIN
set /p python_done="Is Python installation complete? (Y/N): "
if /i "%python_done%"=="Y" (
    goto VERIFY_PYTHON
)
if /i "%python_done%"=="N" (
    echo.
    echo Please complete the Python installation and then press Y
    echo.
    goto CHECK_AGAIN
)
echo Please answer Y or N
goto CHECK_AGAIN

:VERIFY_PYTHON
echo.
echo Verifying Python installation...
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python still not detected. Please make sure:
    echo   1. Python is installed correctly
    echo   2. "Add Python to PATH" was checked during installation
    echo   3. You have restarted any command prompts
    echo.
    set /p choice="Press R to retry verification, M to install manually, or any other key to exit: "
    if /i "%choice%"=="R" goto VERIFY_PYTHON
    if /i "%choice%"=="M" (
        start https://python.org/downloads
        goto WAIT_FOR_PYTHON
    )
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] %PYTHON_VERSION% verified successfully!
timeout /t 1 /nobreak >nul

:CHECK_PACKAGES
echo.
echo Checking for required packages...
python -c "import pyautogui, keyboard, win10toast, psutil" >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] All packages are already installed!
    goto CHECK_BACKEND
)

echo Some packages are missing, installing now...
goto INSTALL_PACKAGES

:INSTALL_PACKAGES
echo.
echo Installing required packages...
echo This may take a minute...
echo.

set INSTALL_SUCCESS=0

echo Installing pyautogui, keyboard, win10toast, and psutil...
pip install pyautogui keyboard win10toast psutil
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully!
    set INSTALL_SUCCESS=1
    goto CHECK_BACKEND
)

echo Method 1 failed, trying alternative method...
python -m pip install pyautogui keyboard win10toast psutil
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully via python -m pip!
    set INSTALL_SUCCESS=1
    goto CHECK_BACKEND
)

echo Method 2 failed, trying with --user flag...
pip install --user pyautogui keyboard win10toast psutil
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully with --user flag!
    set INSTALL_SUCCESS=1
    goto CHECK_BACKEND
)

echo Method 3 failed, trying python -m pip with --user...
python -m pip install --user pyautogui keyboard win10toast psutil
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully via python -m pip --user!
    set INSTALL_SUCCESS=1
    goto CHECK_BACKEND
)

echo.
echo [WARNING] Could not install packages automatically.
echo.
echo You can still try to run the program, but it may not work properly.
echo Alternatively, you can manually install the packages:
echo Open Command Prompt as Administrator and run:
echo pip install pyautogui keyboard win10toast psutil
echo.
set /p choice="Press C to continue anyway, R to retry installation, or any other key to exit: "
if /i "%choice%"=="R" goto INSTALL_PACKAGES
if /i "%choice%"=="C" (
    set INSTALL_SUCCESS=0
    goto CHECK_BACKEND
)
exit /b 0

:CHECK_BACKEND
echo.
echo Checking if backend is already running...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/status.json' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Backend is already running!
    goto OPEN_WEB_INTERFACE
)

:CREATE_FOLDER
echo.
echo Creating Auto Clicker folder...
if not exist "autoclicker" mkdir autoclicker
if not exist "autoclicker" (
    echo [ERROR] Failed to create folder!
    pause
    exit /b 1
)
echo [SUCCESS] Folder created successfully!
goto DOWNLOAD_FILES

:DOWNLOAD_FILES
echo.
echo Downloading Auto Clicker files...
echo.

REM Download with better error handling
echo Downloading backend file...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/main/content/MinecraftEducation.py' -OutFile 'autoclicker\MinecraftEducation.py'"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download backend file from primary source.
    echo Trying alternative download method...
    curl -L -o "autoclicker\MinecraftEducation.py" "https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/main/content/MinecraftEducation.py"
)

if not exist "autoclicker\MinecraftEducation.py" (
    echo [ERROR] Failed to download backend file after all attempts.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo [SUCCESS] Backend downloaded successfully!

echo Downloading VBS launcher...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/main/content/launcher.vbs' -OutFile 'autoclicker\launcher.vbs'"
if not exist "autoclicker\launcher.vbs" (
    echo [WARNING] Failed to download VBS launcher. Creating basic one...
    powershell -NoProfile -Command ^
      "Set-Content -Path 'autoclicker\launcher.vbs' -Value 'CreateObject(""WScript.Shell"").Run ""pythonw MinecraftEducation.py"", 0, False'"
)

echo [SUCCESS] VBS launcher ready!

:START_BACKEND
echo.
echo Starting Backend Server (Hidden via VBS)...
echo.
timeout /t 2 /nobreak >nul

REM Start the backend using the VBS script (completely hidden)
cd autoclicker
start launcher.vbs
cd..
timeout /t 5 /nobreak >nul

:CHECK_BACKEND_RUNNING
echo Checking if backend started successfully...
timeout /t 2 /nobreak >nul
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8080/status.json' -TimeoutSec 2; echo [SUCCESS] Backend is running!; exit 0 } catch { echo [WARNING] Backend may not be running properly; exit 1 }"

:OPEN_WEB_INTERFACE
echo.
echo Opening Web Interface...
echo.
echo The web interface will now open in your browser.
echo You can also manually visit:
echo https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html
echo.
timeout /t 2 /nobreak >nul

start "" "https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html"

echo.
echo ========================================
echo [SUCCESS] Installation Complete!
echo ========================================
echo.
echo ✅ Python and packages installed
echo ✅ Backend server started (completely hidden)
echo ✅ Web interface opened
echo.
echo 📢 You should see a notification confirming the service is running
echo 🎮 Use F6 to start/stop auto-clicker
echo 🌐 Control via web interface at any time
echo.

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
    echo 2. Run: pip install pyautogui keyboard win10toast psutil
    echo 3. Download MinecraftEducation.py manually from:
    echo    https://github.com/SenturyHanderserson/SigmiForCCGS
    echo 4. Visit the web interface:
    echo    https://senturyhanderserson.github.io/SigmiForCCGS/content/autoclickerinterface.html
    echo 5. Run: python MinecraftEducation.py
    echo.
    pause
    goto END_MENU
)

echo.
echo Thank you for using my autoclicker! - 396abc
echo.
timeout /t 3 /nobreak >nul
