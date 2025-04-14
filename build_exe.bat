@echo off
echo.
echo ===============================================
echo ĐANG TIẾN HÀNH BUILD AUTO ZOTERO IMPORTER...
echo ===============================================
echo.

REM Đảm bảo file icon.ico có trong thư mục assets/
set ICON_PATH=assets\icon.ico

REM Tên file chính
set SCRIPT_PATH=app\main.py

REM Kiểm tra PyInstaller đã được cài chưa
where pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo [X] PyInstaller chưa được cài. Cài bằng:
    echo     pip install pyinstaller
    pause
    exit /b
)

REM Thực thi build
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=%ICON_PATH% ^
    --hidden-import=customtkinter ^
    %SCRIPT_PATH%

echo.
echo [✓] BUILD HOÀN TẤT!
echo => File .exe nằm trong thư mục /dist/
echo.

pause
