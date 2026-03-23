@echo off
setlocal enabledelayedexpansion

:: ====================================================
::   DROP DOWN - DISTRIBUTION BUILDER (V1.2)
:: ====================================================

title Drop Down App Builder
set "APP_NAME=Drop Down"

echo ====================================================
echo   Building !APP_NAME! (Mobile APK + Windows EXE)
echo ====================================================
echo.

:: 1. CHECK DEPENDENCIES
echo [1/4] Checking for Build Tools...

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    set "HAS_DOCKER=0"
    echo [WARNING] Docker not found. APK build will NOT work.
) else (
    set "HAS_DOCKER=1"
    echo [OK] Docker is installed ^(Used for APK^).
)

:: Check Flutter
flutter --version >nul 2>&1
if %errorlevel% neq 0 (
    set "HAS_FLUTTER=0"
    echo [WARNING] Local Flutter SDK not found in PATH. EXE build will NOT work.
) else (
    set "HAS_FLUTTER=1"
    echo [OK] Local Flutter is installed ^(Used for Windows EXE^).
)

:: 2. CREATE PROJECT IF MISSING
if not exist mobile (
    echo.
    echo [2/4] Initializing Flutter Project 'mobile'...
    if "!HAS_FLUTTER!" == "1" (
        flutter create --platforms android,windows mobile
    ) else if "!HAS_DOCKER!" == "1" (
        docker run --rm -v "%cd%":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter create --platforms android,windows mobile"
    ) else (
        echo [ERROR] No Flutter or Docker found. Cannot create project.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Mobile project already exists. SKIPPING initialization.
)

:: 3. APPLY SETTINGS (PATCH)
echo.
echo [3/4] Applying App Branding and Logic...
py scripts/patch_mobile_app.py
if %errorlevel% neq 0 (
    echo [ERROR] Python patch script failed. Ensure Python ^(py^) is installed.
)

:: 4. MENU
:MENU
echo.
echo ====================================================
echo   SELECT BUILD TARGET
echo ====================================================
echo 1^) Build Mobile APK ^(Release^) - Uses Docker
echo 2^) Build Windows EXE ^(Release^) - Uses Local Flutter + VS
echo 3^) Build BOTH
echo 4^) Exit
echo.
set /p opt="Choice: "

if "%opt%"=="1" goto BUILD_APK
if "%opt%"=="2" goto BUILD_WIN
if "%opt%"=="3" goto BUILD_BOTH
if "%opt%"=="4" goto END
goto MENU_ERROR

:BUILD_APK
if "!HAS_DOCKER!" == "0" (
    echo [ABORT] Docker is required for APK build.
    goto END
)
echo.
echo [BUILD] Compiling Release APK via Docker...
docker run --rm -v "%cd%/mobile":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter pub add webview_flutter && flutter build apk --release"
echo.
echo [SUCCESS] APK Created: mobile\build\app\outputs\flutter-apk\app-release.apk
if "%opt%"=="3" goto BUILD_WIN
goto END

:BUILD_WIN
if "!HAS_FLUTTER!" == "0" (
    echo [ABORT] Local Flutter is required for Windows EXE build.
    goto END
)
echo.
echo [BUILD] Compiling Windows EXE...
cd mobile
flutter build windows --release
cd ..
echo.
echo [SUCCESS] EXE Path: mobile\build\windows\runner\Release
goto END

:BUILD_BOTH
goto BUILD_APK

:MENU_ERROR
echo Invalid choice.
pause
goto MENU

:END
echo.
echo ====================================================
echo   PROCESS COMPLETED!
echo ====================================================
pause
endlocal
