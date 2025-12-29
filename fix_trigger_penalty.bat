@echo off
REM ============================================================================
REM Trigger Güncelleme Scripti - Batch Dosyası
REM ============================================================================
REM Bu dosya, veritabanındaki trigger'ı yeni ceza sistemine göre günceller.
REM ============================================================================

echo.
echo ========================================
echo Trigger Guncelleme Scripti
echo ========================================
echo.
echo Bu script, veritabanindaki trigger'i yeni ceza sistemine gore gunceller.
echo Eski sistem: amount ve is_paid sutunlari
echo Yeni sistem: penalty_end_date sutunu (1 ay kitap alamama)
echo.

REM MySQL kullanıcı bilgilerini .env dosyasından oku
for /f "tokens=2 delims==" %%a in ('findstr "DB_USER" .env') do set DB_USER=%%a
for /f "tokens=2 delims==" %%a in ('findstr "DB_PASSWORD" .env') do set DB_PASSWORD=%%a
for /f "tokens=2 delims==" %%a in ('findstr "DB_NAME" .env') do set DB_NAME=%%a

REM Varsayılan değerler
if "%DB_USER%"=="" set DB_USER=root
if "%DB_PASSWORD%"=="" set DB_PASSWORD=
if "%DB_NAME%"=="" set DB_NAME=smart_library

echo Veritabani: %DB_NAME%
echo Kullanici: %DB_USER%
echo.

REM Şifre varsa -p parametresi ekle
if "%DB_PASSWORD%"=="" (
    mysql -u %DB_USER% %DB_NAME% < fix_trigger_penalty.sql
) else (
    mysql -u %DB_USER% -p%DB_PASSWORD% %DB_NAME% < fix_trigger_penalty.sql
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Trigger basariyla guncellendi!
    echo ========================================
    echo.
) else (
    echo.
    echo ========================================
    echo HATA: Trigger guncellenemedi!
    echo ========================================
    echo.
    echo Lutfen MySQL'in calistigindan ve veritabani bilgilerinin dogru oldugundan emin olun.
    echo.
    pause
    exit /b 1
)

pause



