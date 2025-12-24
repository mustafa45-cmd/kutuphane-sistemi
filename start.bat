@echo off
chcp 65001 >nul
title Akıllı Kütüphane Yönetim Sistemi - Başlatılıyor...

echo ========================================
echo  Akıllı Kütüphane Yönetim Sistemi
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

REM Gerekli paketlerin yüklü olup olmadığını kontrol et
echo 📦 Paketler kontrol ediliyor...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask bulunamadı. Paketler yükleniyor...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Paket yükleme başarısız!
        pause
        exit /b 1
    )
    echo ✅ Paketler yüklendi
) else (
    echo ✅ Gerekli paketler yüklü
)
echo.

REM .env dosyasının varlığını kontrol et
if not exist .env (
    echo ⚠️  .env dosyası bulunamadı. Oluşturuluyor...
    (
        echo SECRET_KEY=dev-secret-key-change-in-production-2025
        echo DB_USER=root
        echo DB_PASSWORD=
        echo DB_HOST=127.0.0.1
        echo DB_NAME=smart_library
    ) > .env
    echo ✅ .env dosyası oluşturuldu
    echo.
    echo ⚠️  LÜTFEN .env DOSYASINA MYSQL ŞİFRENİZİ EKLEYİN!
    echo.
) else (
    echo ✅ .env dosyası mevcut
)
echo.

REM Veritabanı kontrolü (isteğe bağlı - hata vermez)
echo 🔍 Veritabanı bağlantısı test ediliyor...
python -c "from app import create_app; app = create_app(); from src.db import db; app.app_context().push(); db.engine.connect()" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Veritabanı bağlantı hatası!
    echo.
    echo 💡 Lütfen şunları kontrol edin:
    echo    1. MySQL servisinin çalıştığından emin olun
    echo    2. db_schema.sql dosyasını MySQL'de çalıştırın
    echo    3. .env dosyasındaki DB_PASSWORD değerini kontrol edin
    echo.
    echo ⚠️  Uygulama başlatılıyor ama veritabanı hatası alabilirsiniz...
    echo.
) else (
    echo ✅ Veritabanı bağlantısı başarılı
)
echo.

echo ========================================
echo  Flask Uygulaması Başlatılıyor...
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:5000/static/index.html
echo 🔌 API: http://localhost:5000/api/health
echo.
echo ⚠️  Uygulamayı durdurmak için Ctrl+C tuşlarına basın
echo.
echo ========================================
echo.

REM Flask uygulamasını başlat
python app.py

pause

