@echo off
chcp 65001 >nul
title Paket Yükleme

echo ========================================
echo  Python Paketleri Yükleniyor...
echo ========================================
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo.
    echo 💡 Lütfen Python'u yükleyin: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python bulundu
python --version
echo.

REM requirements.txt dosyasının varlığını kontrol et
if not exist requirements.txt (
    echo ❌ requirements.txt dosyası bulunamadı!
    pause
    exit /b 1
)

echo 📦 Paketler yükleniyor...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ❌ Paket yükleme başarısız!
    echo.
    echo 💡 İpuçları:
    echo    - İnternet bağlantınızı kontrol edin
    echo    - pip'i güncelleyin: python -m pip install --upgrade pip
    echo.
) else (
    echo.
    echo ✅ Tüm paketler başarıyla yüklendi!
    echo.
    echo 📋 Yüklü paketler:
    python -m pip list | findstr /i "flask pymysql sqlalchemy jwt passlib"
    echo.
)

pause

