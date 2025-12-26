@echo off
chcp 65001 >nul
title Odunc Alma Sistemi Guncelleme

echo ========================================
echo  Odunc Alma Sistemi Guncelleme
echo ========================================
echo.
echo Bu script, odunc alma sistemini istek/onay
echo sistemine cevirir.
echo.

REM MySQL komut satırı araçlarının varlığını kontrol et
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL komut satırı araçları bulunamadı!
    echo.
    echo 💡 Lütfen MySQL Workbench ile update_loan_system.sql
    echo    dosyasını çalıştırın.
    echo.
    pause
    exit /b 1
)

echo ✅ MySQL bulundu
echo.
echo MySQL root şifrenizi girin:
mysql -u root -p < update_loan_system.sql

if errorlevel 1 (
    echo.
    echo ❌ Güncelleme başarısız!
    echo.
    echo 💡 Alternatif: MySQL Workbench ile update_loan_system.sql
    echo    dosyasını çalıştırın.
    echo.
) else (
    echo.
    echo ✅ Sistem başarıyla güncellendi!
    echo.
    echo 📋 Yeni durumlar:
    echo    - requested: İstek gönderildi (beklemede)
    echo    - approved: Admin onayladı
    echo    - borrowed: Kitap ödünç alındı
    echo    - returned: Kitap iade edildi
    echo    - late: Geç iade
    echo    - rejected: İstek reddedildi
    echo.
)

pause



