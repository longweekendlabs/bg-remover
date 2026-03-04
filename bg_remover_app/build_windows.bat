@echo off
setlocal EnableDelayedExpansion

:: build_windows.bat — Build BG Remover for Windows
:: Outputs: win\BGRemover-v{VERSION}-win64-portable.zip
::          win\BGRemover-v{VERSION}-win64-Setup.exe  (if Inno Setup is installed)

echo ==========================================================
echo  BG Remover — Windows Build
echo ==========================================================

:: ── Read version ────────────────────────────────────────────────────────────
for /f "delims=" %%v in ('python -c "from version import __version__; print(__version__)"') do (
    set "VERSION=%%v"
)
if not defined VERSION (
    echo ERROR: Could not read version from version.py
    exit /b 1
)
echo Version: %VERSION%

set "APP_NAME=BGRemover"
set "PKG_PREFIX=BGRemover-v%VERSION%-win64"

:: ── Find PyInstaller ─────────────────────────────────────────────────────────
set "PYINSTALLER="
for %%p in (pyinstaller.exe pyinstaller) do (
    if not defined PYINSTALLER (
        where %%p >nul 2>&1 && set "PYINSTALLER=%%p"
    )
)
if not defined PYINSTALLER (
    echo ERROR: pyinstaller not found in PATH
    exit /b 1
)

:: ── 1. PyInstaller binary ────────────────────────────────────────────────────
echo.
echo [1/2] Running PyInstaller...
"%PYINSTALLER%" bg_remover_app.spec --clean --noconfirm ^
    --distpath dist --workpath build
if errorlevel 1 (
    echo ERROR: PyInstaller failed
    exit /b 1
)

if not exist "dist\%APP_NAME%.exe" (
    echo ERROR: dist\%APP_NAME%.exe not found after build
    exit /b 1
)

:: ── 2. Portable ZIP ──────────────────────────────────────────────────────────
echo.
echo [2/2] Creating portable ZIP...
if not exist win mkdir win

set "ZIP_NAME=%PKG_PREFIX%-portable.zip"
if exist "win\%ZIP_NAME%" del /f "win\%ZIP_NAME%"
powershell -NoProfile -Command ^
    "Compress-Archive -Path 'dist\%APP_NAME%.exe' -DestinationPath 'win\%ZIP_NAME%'"
echo     win\%ZIP_NAME%

:: ── 3. Inno Setup installer (optional) ───────────────────────────────────────
echo.
echo [3] Looking for Inno Setup...
set "ISCC="
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) do (
    if not defined ISCC (
        if exist %%p set "ISCC=%%~p"
    )
)
if not defined ISCC (
    where ISCC.exe >nul 2>&1 && for /f "delims=" %%f in ('where ISCC.exe') do set "ISCC=%%f"
)

if defined ISCC (
    echo     Found: !ISCC!
    "!ISCC!" /DAppVersion=%VERSION% installer.iss
    if errorlevel 1 (
        echo WARNING: Inno Setup failed — skipping installer
    ) else (
        if exist "Output\%APP_NAME%-*-win64-Setup.exe" (
            move /y "Output\%APP_NAME%-*-win64-Setup.exe" win\ >nul
            echo     win\%APP_NAME%-v%VERSION%-win64-Setup.exe
        )
    )
) else (
    echo     Inno Setup not found — skipping installer
    echo     Install from: https://jrsoftware.org/isdl.php
)

echo.
echo ==========================================================
echo  Done. Packages in win\:
dir /b win\
echo ==========================================================
