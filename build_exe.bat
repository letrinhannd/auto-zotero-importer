@echo off
echo.
echo ===============================================
echo DANG TIEN HANH BUILD AUTO ZOTERO IMPORTER...
echo ===============================================
echo.

REM Dam bao file icon.ico co trong thu muc assets/
set ICON_PATH=assets\icon.ico

REM Ten file chinh
set SCRIPT_PATH=app\main.py

REM Kiem tra PyInstaller da duoc cai chua
where pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo [X] PyInstaller chua duoc cai. Cai bang:
    echo     pip install pyinstaller
    pause
    exit /b
)

REM Thuc thi build
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=%ICON_PATH% ^
    --hidden-import=customtkinter ^
    %SCRIPT_PATH%

echo.
echo BUILD HOAN TAT!
echo File .exe nam trong thu muc /dist/
echo.

pause
