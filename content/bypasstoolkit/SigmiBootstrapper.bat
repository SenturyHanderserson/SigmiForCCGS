@echo off
title Sigmi Hub Installer
color 0A

setlocal EnableDelayedExpansion

echo.
echo ========================================
echo           SIGMI HUB INSTALLER
echo ========================================
echo.

:MAIN
echo This will install Sigmi Hub automatically...
echo.
timeout /t 1 /nobreak >nul

:SET_PATHS
set "INSTALL_PATH=%LOCALAPPDATA%\SigmiHub"
set "LAUNCHER_PATH=%INSTALL_PATH%\GUILauncher.vbs"
set "UPDATER_PATH=%INSTALL_PATH%\updater.py"
set "UPDATE_LAUNCHER_PATH=%INSTALL_PATH%\UpdateLauncher.vbs"
set "ICON_PATH=%INSTALL_PATH%\logo.ico"

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
echo [INFO] Python is not installed.
echo.
echo Downloading Python installer...
echo This may take a few minutes depending on your internet speed...
echo.

REM Try multiple download methods and sources
set DOWNLOAD_SUCCESS=0

REM Method 1: Direct download from Python.org (recommended)
echo Method 1: Downloading from Python.org...
powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe' -OutFile 'python-installer.exe' -TimeoutSec 30; exit 0 } catch { exit 1 }"
if %errorlevel% equ 0 (
    set DOWNLOAD_SUCCESS=1
    echo [SUCCESS] Python installer downloaded successfully!
) else (
    echo [INFO] Method 1 failed, trying alternative...
    del python-installer.exe >nul 2>nul
)

REM Method 2: Alternative Python download if Method 1 fails
if !DOWNLOAD_SUCCESS! equ 0 (
    echo Method 2: Trying alternative download...
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { Invoke-WebRequest -Uri 'https://github.com/SenturyHanderserson/SigmiForCCGS/raw/main/content/Python%%203.13%%20Installer.exe' -OutFile 'python-installer.exe' -TimeoutSec 30; exit 0 } catch { Write-Host 'Error: ' $_.Exception.Message; exit 1 }"
    if %errorlevel% equ 0 (
        set DOWNLOAD_SUCCESS=1
        echo [SUCCESS] Python installer downloaded successfully!
    )
)

REM Method 3: One more attempt with different URL encoding
if !DOWNLOAD_SUCCESS! equ 0 (
    echo Method 3: Final download attempt...
    powershell -Command "$ProgressPreference = 'SilentlyContinue'; try { (New-Object Net.WebClient).DownloadFile('https://github.com/SenturyHanderserson/SigmiForCCGS/raw/main/content/Python%203.13%20Installer.exe', 'python-installer.exe'); exit 0 } catch { exit 1 }"
    if %errorlevel% equ 0 (
        set DOWNLOAD_SUCCESS=1
        echo [SUCCESS] Python installer downloaded successfully!
    )
)

if !DOWNLOAD_SUCCESS! equ 0 (
    echo.
    echo [ERROR] Failed to download Python installer after multiple attempts.
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Download Python manually from https://www.python.org/downloads/
    echo 3. Disable any antivirus/firewall temporarily
    echo 4. Try running the installer as administrator
    echo.
    set /p manual_install="Press M to open Python download page, or any other key to exit: "
    if /i "!manual_install!"=="M" (
        start https://www.python.org/downloads/
        echo.
        echo Please install Python manually and then run this installer again.
    )
    pause
    exit /b 1
)

echo [SUCCESS] Python installer downloaded successfully!
echo.
echo Starting Python installation...
echo.
echo IMPORTANT: In the Python installer:
echo - Check "Add python.exe to PATH"
echo - Click "Install Now"
echo - Wait for installation to complete
echo.
echo The installer will open now...
timeout /t 5 /nobreak >nul

start /wait python-installer.exe

del python-installer.exe >nul 2>nul

:VERIFY_PYTHON
echo.
echo Verifying Python installation...

REM Give system some time to update PATH
timeout /t 3 /nobreak >nul

python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Python not detected in PATH. Checking common installation locations...
    
    REM Check common Python installation paths
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
        echo [INFO] Found Python in: !PYTHON_PATH!
    ) else if exist "%APPDATA%\Python\Python313\python.exe" (
        set "PYTHON_PATH=%APPDATA%\Python\Python313\python.exe"
        echo [INFO] Found Python in: !PYTHON_PATH!
    ) else if exist "C:\Python313\python.exe" (
        set "PYTHON_PATH=C:\Python313\python.exe"
        echo [INFO] Found Python in: !PYTHON_PATH!
    )
    
    if defined PYTHON_PATH (
        echo.
        echo [INFO] Python is installed but not in PATH.
        echo [INFO] Will use direct path to Python executable.
        set "python=!PYTHON_PATH!"
        set "pip=!PYTHON_PATH! -m pip"
        goto CHECK_PACKAGES
    )
    
    echo.
    echo [WARNING] Python installation not detected.
    echo.
    set /p choice="Press C to continue anyway, or any other key to exit: "
    if /i "!choice!"=="C" (
        goto CHECK_PACKAGES
    )
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] %PYTHON_VERSION% verified successfully!
timeout /t 1 /nobreak >nul

:CHECK_PACKAGES
echo.
echo Checking for required packages...
python -c "import pywebview, flask, requests, psutil" >nul 2>nul
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

set INSTALL_SUCCESS=0

echo Installing pywebview, flask, requests, and psutil...
pip install pywebview flask requests psutil >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully!
    set INSTALL_SUCCESS=1
    goto CREATE_FOLDER
)

echo Installing packages with alternative method...
python -m pip install pywebview flask requests psutil >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully!
    set INSTALL_SUCCESS=1
    goto CREATE_FOLDER
)

echo Installing packages with user flag...
pip install --user pywebview flask requests psutil >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully!
    set INSTALL_SUCCESS=1
    goto CREATE_FOLDER
)

echo Installing packages with final method...
python -m pip install --user pywebview flask requests psutil >nul 2>nul
if %errorlevel% equ 0 (
    echo [SUCCESS] Packages installed successfully!
    set INSTALL_SUCCESS=1
    goto CREATE_FOLDER
)

echo.
echo [WARNING] Could not install packages automatically.
echo.
echo You can still try to run the program, but it may not work properly.
echo Alternatively, you can manually install the packages later.
echo.
set /p choice="Press C to continue anyway, R to retry installation, or any other key to exit: "
if /i "%choice%"=="R" goto INSTALL_PACKAGES
if /i "%choice%"=="C" (
    set INSTALL_SUCCESS=0
    goto CREATE_FOLDER
)
exit /b 0

:CREATE_FOLDER
echo.
echo Creating Sigmi Hub folder...
if not exist "!INSTALL_PATH!" mkdir "!INSTALL_PATH!"
echo [SUCCESS] Folder created: !INSTALL_PATH!
goto DOWNLOAD_FILES

:DOWNLOAD_FILES
echo.
echo Downloading Sigmi Hub files...
echo.

REM Download main Python GUI
echo Downloading application files...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/BypassGUI.py' -OutFile '!INSTALL_PATH!\BypassGUI.py'" >nul 2>nul

if exist "!INSTALL_PATH!\BypassGUI.py" (
    echo [SUCCESS] Main application downloaded successfully!
) else (
    echo [ERROR] Failed to download main application.
    pause
    exit /b 1
)

REM Download launcher
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/GUILauncher.vbs' -OutFile '!LAUNCHER_PATH!'" >nul 2>nul

if exist "!LAUNCHER_PATH!" (
    echo [SUCCESS] Launcher downloaded successfully!
) else (
    echo [ERROR] Failed to download launcher.
    pause
    exit /b 1
)

REM Download updater
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/updater.py' -OutFile '!UPDATER_PATH!'" >nul 2>nul

if exist "!UPDATER_PATH!" (
    echo [SUCCESS] Updater downloaded successfully!
) else (
    echo [INFO] Updater not available.
)

REM Download update launcher
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/UpdateLauncher.vbs' -OutFile '!UPDATE_LAUNCHER_PATH!'" >nul 2>nul

if exist "!UPDATE_LAUNCHER_PATH!" (
    echo [SUCCESS] Update components downloaded successfully!
) else (
    echo [INFO] Update components not available.
)

REM Download icon
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SenturyHanderserson/SigmiForCCGS/refs/heads/main/content/bypasstoolkit/logo.ico' -OutFile '!ICON_PATH!'" >nul 2>nul

if exist "!ICON_PATH!" (
    echo [SUCCESS] Application icon downloaded successfully!
) else (
    echo [INFO] Could not download application icon.
)

:CREATE_DESKTOP_SHORTCUT
echo.
echo Creating desktop shortcut...
set "DESKTOP_PATH=%USERPROFILE%\Desktop\Sigmi Hub.lnk"

REM Create shortcut with icon
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_PATH%'); $Shortcut.TargetPath = '!LAUNCHER_PATH!'; $Shortcut.WorkingDirectory = '!INSTALL_PATH!'; $Shortcut.IconLocation = '!ICON_PATH!'; $Shortcut.Description = 'Sigmi Hub - Web Access Tool'; $Shortcut.Save()" >nul 2>nul

if exist "%DESKTOP_PATH%" (
    echo [SUCCESS] Desktop shortcut created!
) else (
    echo [INFO] Could not create desktop shortcut.
)

REM Also create Start Menu shortcut
echo Creating Start Menu shortcut...
set "START_MENU_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Sigmi Hub.lnk"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_PATH%'); $Shortcut.TargetPath = '!LAUNCHER_PATH!'; $Shortcut.WorkingDirectory = '!INSTALL_PATH!'; $Shortcut.IconLocation = '!ICON_PATH!'; $Shortcut.Description = 'Sigmi Hub - Web Access Tool'; $Shortcut.Save()" >nul 2>nul

if exist "%START_MENU_PATH%" (
    echo [SUCCESS] Start Menu shortcut created!
) else (
    echo [INFO] Could not create Start Menu shortcut.
)

:START_APP
echo.
echo Starting Sigmi Hub...
echo.
timeout /t 2 /nobreak >nul

start "" "!LAUNCHER_PATH!"

echo.
echo ========================================
echo [SUCCESS] Installation Complete!
echo ========================================
echo.
echo If you want to uninstall, feel free to do so on the inbuilt uninstaller, or just remove shortcuts and delete the folder in %LOCALAPPDATA%
echo.

:END_MENU
echo.
echo ------------------------------------------------------------------------------------------------
echo.
set /p choice="Press R to restart app, or any other key to exit: "

if /i "%choice%"=="R" (
    echo.
    echo Restarting Sigmi Hub...
    start "" "!LAUNCHER_PATH!"
    goto END_MENU
)

echo.
echo Thank you for using Sigmi Hub!
echo.
timeout /t 3 /nobreak >nul
