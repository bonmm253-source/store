@echo off
setlocal

echo ====================================================
echo   Drop Down Store - Mobile APK Builder
echo ====================================================
echo.

REM --- CHECK FOR DOCKER ---
echo [1/4] Checking for Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker not found in PATH. Please ensure Docker Desktop is installed and running.
    pause
    exit /b 1
)
echo [OK] Docker is available.

REM --- CREATE MOBILE PROJECT ---
echo [2/4] Creating Flutter mobile project via Docker...
if not exist mobile (
    docker run --rm -v "%cd%":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter create --platforms android mobile"
) else (
    echo [SKIP] Mobile folder already exists.
)

REM --- PATCH MOBILE PROJECT ---
echo [3/4] Applying App logic and Branding...
if exist scripts/patch_mobile_app.py (
    python scripts/patch_mobile_app.py
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to patch mobile project files. Ensure Python is installed.
    )
) else (
    echo [ERROR] patch_mobile_app.py not found in scripts/
)

REM --- BUILD APK ---
echo.
echo [4/4] Building release APK via Docker...
echo This may take a while. It will install packages and generate the app icon.
echo.

docker run --rm -v "%cd%/mobile":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter pub get && flutter pub run flutter_launcher_icons && flutter build apk --release"

if %errorlevel% equ 0 (
    echo.
    echo ====================================================
    echo   BUILD SUCCESSFUL!
    echo   Location: mobile\build\app\outputs\flutter-apk\app-release.apk
    echo ====================================================
) else (
    echo.
    echo [ERROR] Build failed. Check the logs above.
)

pause
endlocal
