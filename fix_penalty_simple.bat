@echo off
chcp 65001 >nul
echo ========================================
echo Ceza Sütunu Düzeltme (Basit)
echo ========================================
echo.
echo Bu script, veritabanına penalty_end_date sütununu ekler.
echo.
echo Lutfen MySQL root sifrenizi girin:
mysql -u root -p smart_library < fix_penalty_simple.sql
if %errorlevel% == 0 (
    echo.
    echo [SUCCESS] Ceza sütunu basariyla eklendi!
    echo Artik sistem calisacak.
) else (
    echo.
    echo [ERROR] Guncelleme basarisiz oldu!
    echo.
    echo Alternatif yontemler:
    echo 1. MySQL Workbench ile fix_penalty_simple.sql dosyasini calistirin
    echo 2. phpMyAdmin ile SQL sekmesinden calistirin
)
pause

