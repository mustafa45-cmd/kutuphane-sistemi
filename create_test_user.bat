@echo off
chcp 65001 >nul
title Test Kullanıcıları Oluşturma

echo ========================================
echo  Test Kullanıcıları Oluşturuluyor...
echo ========================================
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    pause
    exit /b 1
)

REM create_test_user.py dosyasının varlığını kontrol et
if not exist create_test_user.py (
    echo ❌ create_test_user.py dosyası bulunamadı!
    pause
    exit /b 1
)

echo 🔄 Test kullanıcıları oluşturuluyor...
echo.

python create_test_user.py

if errorlevel 1 (
    echo.
    echo ❌ Kullanıcı oluşturma başarısız!
    echo.
    echo 💡 Lütfen şunları kontrol edin:
    echo    1. MySQL veritabanının kurulu olduğundan emin olun
    echo    2. .env dosyasındaki DB_PASSWORD değerini kontrol edin
    echo    3. Veritabanı bağlantısını test edin
    echo.
) else (
    echo.
    echo ✅ Test kullanıcıları hazır!
    echo.
    echo 📝 Giriş bilgileri:
    echo    Admin: admin@example.com / admin123
    echo    Öğrenci: student@example.com / student123
    echo.
)

pause



