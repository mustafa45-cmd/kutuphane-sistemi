@echo off
echo ========================================
echo Ceza Sistemi Guncelleme Scripti
echo ========================================
echo.
echo Bu script, para cezasi sistemini 1 ay kitap alamama cezasina cevirir.
echo.
echo Lutfen MySQL root sifrenizi girin:
mysql -u root -p smart_library < update_penalty_system.sql
if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] Ceza sistemi basariyla guncellendi!
    echo Artik para cezasi yerine 1 ay kitap alamama cezasi uygulanacak.
) else (
    echo.
    echo [ERROR] Guncelleme basarisiz oldu!
    echo Lutfen MySQL'in calistigindan ve sifrenin dogru oldugundan emin olun.
)
pause

