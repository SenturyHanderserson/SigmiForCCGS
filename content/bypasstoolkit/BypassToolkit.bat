@echo off
title Bypass Toolkit Installer
color 0A

setlocal EnableDelayedExpansion

echo.
echo ========================================
echo       BYPASS TOOLKIT INSTALLER
echo ========================================
echo.

:MAIN
echo This will install Bypass Toolkit automatically...
echo.
timeout /t 1 /nobreak >nul

:SET_PATHS
set "INSTALL_PATH=%LOCALAPPDATA%\BypassToolkit"
set "LAUNCHER_PATH=%INSTALL_PATH%\GUILauncher.vbs"
set "UPDATER_PATH=%INSTALL_PATH%\updater.py"
set "REQUIREMENTS_PATH=%INSTALL_PATH%\requirements.txt"
set "MAIN_SCRIPT=BypassGUI.py"

echo Installation Path: !INSTALL_PATH!
echo.

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

powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python-installer.exe'" >nul 2>nul

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
python -c "import pywebview, flask" >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] All packages are already installed!
    goto CREATE_FOLDER
)

echo Required packages missing, installing now...
goto INSTALL_PACKAGES

:INSTALL_PACKAGES
echo.
echo Installing required packages...
echo This may take a minute...
echo.

echo Installing pywebview (this is the correct package)...
pip install pywebview
if %errorlevel% neq 0 (
    echo [WARNING] pip install pywebview failed, trying python -m pip...
    python -m pip install pywebview
    if %errorlevel% neq 0 (
        echo [WARNING] python -m pip install pywebview failed, trying with --user...
        pip install --user pywebview
        if %errorlevel% neq 0 (
            python -m pip install --user pywebview
        )
    )
)

echo.
echo Installing flask...
pip install flask
if %errorlevel% neq 0 (
    python -m pip install flask
)

echo.
echo Verifying installation...
python -c "import pywebview, flask; print('SUCCESS: All packages installed correctly!')" >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed and verified!
    set INSTALL_SUCCESS=1
    goto CREATE_FOLDER
) else (
    echo [ERROR] Package installation failed!
    echo.
    echo Please install the packages manually:
    echo 1. Open Command Prompt as Administrator
    echo 2. Run these commands:
    echo    pip install pywebview flask
    echo.
    echo 3. If that doesn't work, try:
    echo    python -m pip install pywebview flask
    echo.
    set /p choice="Press C to continue anyway, or any other key to exit: "
    if /i "%choice%"=="C" (
        set INSTALL_SUCCESS=0
        goto CREATE_FOLDER
    )
    exit /b 1
)

:CREATE_FOLDER
echo.
echo Creating Bypass Toolkit folder in LocalAppData...
if not exist "!INSTALL_PATH!" mkdir "!INSTALL_PATH!"
echo [SUCCESS] Folder created: !INSTALL_PATH!
goto DOWNLOAD_FILES

:DOWNLOAD_FILES
echo.
echo Downloading Bypass Toolkit files...
echo.

REM Download main Python GUI with WebView2
echo Downloading BypassGUI.py...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py' -OutFile '!INSTALL_PATH!\!MAIN_SCRIPT!'" >nul 2>nul

if exist "!INSTALL_PATH!\!MAIN_SCRIPT!" (
    echo [SUCCESS] Bypass Toolkit downloaded successfully!
) else (
    echo [ERROR] Failed to download Bypass Toolkit.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

REM Download VBS launcher
echo Downloading VBS launcher...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/GUILauncher.vbs' -OutFile '!LAUNCHER_PATH!'" >nul 2>nul

if exist "!LAUNCHER_PATH!" (
    echo [SUCCESS] VBS launcher downloaded successfully!
) else (
    echo [WARNING] Could not download VBS launcher. Creating basic one...
    goto CREATE_BASIC_VBS
)

REM Download updater
echo Downloading updater...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/updater.py' -OutFile '!UPDATER_PATH!'" >nul 2>nul

if exist "!UPDATER_PATH!" (
    echo [SUCCESS] Updater downloaded successfully!
) else (
    echo [INFO] Updater not available, continuing without update checks.
)

REM Download requirements file
echo Downloading requirements.txt...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/requirements.txt' -OutFile '!REQUIREMENTS_PATH!'" >nul 2>nul

if exist "!REQUIREMENTS_PATH!" (
    echo [SUCCESS] Requirements file downloaded successfully!
) else (
    echo [INFO] Creating basic requirements file...
    goto CREATE_BASIC_REQUIREMENTS
)

goto CREATE_DESKTOP_SHORTCUT

:CREATE_BASIC_VBS
(
echo Set WshShell = CreateObject^("WScript.Shell"^)
echo currentDir = "!INSTALL_PATH!"
echo WshShell.CurrentDirectory = currentDir
echo WshShell.Run "python BypassGUI.py", 0, False
) > "!LAUNCHER_PATH!"
echo [INFO] Basic VBS launcher created.

:CREATE_BASIC_REQUIREMENTS
(
echo pywebview>=4.2.2
echo flask>=3.0.0
) > "!REQUIREMENTS_PATH!"
echo [INFO] Basic requirements file created.

:CREATE_DESKTOP_SHORTCUT
echo.
echo Creating desktop shortcut...
set "DESKTOP_PATH=%USERPROFILE%\Desktop\Bypass Toolkit.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_PATH%'); $Shortcut.TargetPath = '!LAUNCHER_PATH!'; $Shortcut.WorkingDirectory = '!INSTALL_PATH!'; $Shortcut.IconLocation = '!INSTALL_PATH!\BypassGUI.py,0'; $Shortcut.Save()" >nul 2>nul

if exist "%DESKTOP_PATH%" (
    echo [SUCCESS] Desktop shortcut created!
) else (
    echo [INFO] Could not create desktop shortcut.
)

:CHECK_UPDATES
echo.
echo Checking for updates...
if exist "!UPDATER_PATH!" (
    python "!UPDATER_PATH!" >nul 2>nul
    if !errorlevel! equ 1 (
        echo [INFO] Update available! Downloading latest version...
        goto DOWNLOAD_FILES
    ) else (
        echo [SUCCESS] Application is up to date!
    )
) else (
    echo [INFO] Skipping update check (updater not available)
)

:START_APP
echo.
echo Starting Bypass Toolkit (hidden)...
echo.

REM Test if packages are actually installed before starting
echo Verifying packages before launch...
python -c "import pywebview, flask" >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Packages not found! Cannot start application.
    echo Please run the installer again or install manually.
    goto MANUAL_INSTALL_HELP
)

timeout /t 2 /nobreak >nul

start "" "!LAUNCHER_PATH!"

echo.
echo ========================================
echo [SUCCESS] Installation Complete!
echo ========================================
echo.
echo ✅ Python and packages installed
echo ✅ Bypass Toolkit installed to LocalAppData
echo ✅ VBS launcher created (runs hidden)
echo ✅ Desktop shortcut created
echo.
echo 🚀 Application is now running in background
echo 🚀 Use the desktop shortcut to launch anytime
echo 🎨 Features 4 beautiful glass morphism themes
echo 🖱️ Draggable window with theme persistence
echo 🌐 Enter any URL to bypass filters via Google Translate
echo.

goto END_MENU

:MANUAL_INSTALL_HELP
echo.
echo ========================================
echo MANUAL INSTALLATION REQUIRED
echo ========================================
echo.
echo Please install the required packages manually:
echo.
echo 1. Open Command Prompt as Administrator
echo 2. Run these commands:
echo    pip install pywebview flask
echo.
echo 3. If that doesn't work, try:
echo    python -m pip install pywebview flask
echo.
echo 4. After installing, run this installer again
echo.
pause
exit /b 1

:END_MENU
echo.
echo ------------------------------------------------------------------------------------------------
echo.
set /p choice="Press R to restart app, U to check for updates, or any other key to exit: "

if /i "%choice%"=="R" (
    echo.
    echo Restarting Bypass Toolkit...
    start "" "!LAUNCHER_PATH!"
    goto END_MENU
)

if /i "%choice%"=="U" (
    echo.
    echo Checking for updates...
    if exist "!UPDATER_PATH!" (
        python "!UPDATER_PATH!"
        if !errorlevel! equ 1 (
            echo.
            echo Update available! Run the installer again to get the latest version.
            pause
        )
    ) else (
        echo Updater not available.
    )
    goto END_MENU
)

echo.
echo Thank you for using Bypass Toolkit! -396abc
echo.
timeout /t 3 /nobreak >nul
