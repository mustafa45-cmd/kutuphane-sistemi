@echo off
chcp 65001 >nul
title Veritabanı Kurulumu

echo ========================================
echo  MySQL Veritabanı Kurulumu
echo ========================================
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    pause
    exit /b 1
)

REM db_schema.sql dosyasının varlığını kontrol et
if not exist db_schema.sql (
    echo ❌ db_schema.sql dosyası bulunamadı!
    pause
    exit /b 1
)

echo 📄 SQL dosyası: db_schema.sql
echo.

REM MySQL komut satırı araçlarının varlığını kontrol et
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL komut satırı araçları bulunamadı!
    echo.
    echo 💡 Lütfen şu yöntemlerden birini kullanın:
    echo    1. MySQL Workbench ile db_schema.sql dosyasını çalıştırın
    echo    2. phpMyAdmin ile db_schema.sql dosyasını import edin
    echo    3. MySQL'i yükleyip PATH'e ekleyin
    echo.
    echo 🔄 Python script ile denemek için: python setup_database.py
    echo.
    pause
    exit /b 1
)

echo ✅ MySQL bulundu
echo.
echo MySQL root şifrenizi girin:
mysql -u root -p < db_schema.sql

if errorlevel 1 (
    echo.
    echo ❌ Veritabanı kurulumu başarısız!
    echo.
    echo 💡 İpuçları:
    echo    - MySQL root şifrenizi kontrol edin
    echo    - MySQL servisinin çalıştığından emin olun
    echo    - Alternatif: python setup_database.py
    echo.
) else (
    echo.
    echo ✅ Veritabanı başarıyla kuruldu!
    echo.
    echo 📋 Kurulu tablolar:
    echo    - users (kullanıcılar)
    echo    - authors (yazarlar)
    echo    - categories (kategoriler)
    echo    - books (kitaplar)
    echo    - loans (ödünç işlemleri)
    echo    - penalties (cezalar)
    echo.
    echo 🎉 Kurulum tamamlandı!
    echo.
    echo 💡 Test kullanıcıları oluşturmak için: create_test_user.bat
    echo.
)

pause
