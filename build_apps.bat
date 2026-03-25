@echo off
setlocal enabledelayedexpansion

:: ====================================================
::   DROP DOWN STORE - DISTRIBUTION BUILDER
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
set "FLUTTER_CMD=flutter"
if exist "%cd%\flutter\bin\flutter.bat" (
    set "HAS_FLUTTER=1"
    set "PATH=%cd%\flutter\bin;%PATH%"
    echo [OK] Local Flutter found in project root.
) else (
    flutter --version >nul 2>&1
    if %errorlevel% neq 0 (
        set "HAS_FLUTTER=0"
        echo [WARNING] Local Flutter SDK not found. EXE build will NOT work.
    ) else (
        set "HAS_FLUTTER=1"
        echo [OK] Local Flutter is installed ^(Used for Windows EXE^).
    )
)

:: 2. CREATE PROJECT IF MISSING
if not exist mobile (
    echo.
    echo [2/4] Initializing Flutter Project 'mobile'...
    if "!HAS_FLUTTER!" == "1" (
        if exist "%~dp0flutter\bin\flutter.bat" (
            "%~dp0flutter\bin\flutter.bat" create --platforms android,windows mobile
        ) else (
            flutter create --platforms android,windows mobile
        )
    ) else if "!HAS_DOCKER!" == "1" (
        docker run --rm -v "%cd%":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter create --platforms android,windows mobile"
    ) else (
        echo [ERROR] No Flutter or Docker found. Cannot create project.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Mobile project already exists.
)

:: 3. APPLY SETTINGS (PATCH)
echo.
echo [3/4] Applying App Branding and Logic...
python scripts/patch_mobile_app.py
if %errorlevel% neq 0 (
    echo [WARNING] Python patch script failed. Trying 'py' command...
    py scripts/patch_mobile_app.py
)

:: 4. MENU
:MENU
echo.
echo ====================================================
echo   SELECT BUILD TARGET
echo ====================================================
echo 1) Build Mobile APK (Release) - Uses Docker
echo 2) Build Windows EXE (Release) - Uses Local Flutter
echo 3) Build BOTH
echo 4) Exit
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
docker run --rm -v "%cd%/mobile":/app -w /app ghcr.io/cirruslabs/flutter:stable sh -c "flutter pub get && flutter pub run flutter_launcher_icons && flutter build apk --release"
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
flutter pub get
flutter pub run flutter_launcher_icons
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
echo ================== PROCESS COMPLETED ==================
pause
endlocal
