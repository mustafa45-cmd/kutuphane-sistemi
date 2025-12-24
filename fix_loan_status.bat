@echo off
chcp 65001 >nul
title Loans Status Enum Guncelleme

echo ========================================
echo  Loans Status Enum Guncelleme
echo ========================================
echo.
echo Bu script, loans tablosundaki status
echo enum'ini gunceller (requested, approved, vb.)
echo.

REM MySQL komut satırı araçlarının varlığını kontrol et
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL komut satırı araçları bulunamadı!
    echo.
    echo 💡 Lütfen MySQL Workbench ile fix_loan_status.sql
    echo    dosyasını çalıştırın.
    echo.
    pause
    exit /b 1
)

echo ✅ MySQL bulundu
echo.
echo MySQL root şifrenizi girin:
echo.
echo NOT: Bu script loans tablosundaki status enum'ini gunceller.
echo      Eger loans tablosunda veri varsa, veriler korunacaktir.
echo.
mysql -u root -p < fix_loan_status.sql

if errorlevel 1 (
    echo.
    echo ❌ Güncelleme başarısız!
    echo.
    echo 💡 Alternatif: MySQL Workbench ile fix_loan_status.sql
    echo    dosyasını çalıştırın.
    echo.
) else (
    echo.
    echo ✅ Status enum başarıyla güncellendi!
    echo.
    echo 📋 Yeni durumlar:
    echo    - requested: İstek gönderildi
    echo    - approved: Admin onayladı
    echo    - borrowed: Kitap ödünç alındı
    echo    - returned: Kitap iade edildi
    echo    - late: Geç iade
    echo    - rejected: İstek reddedildi
    echo.
)

pause

