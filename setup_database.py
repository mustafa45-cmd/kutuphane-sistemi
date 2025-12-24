"""
MySQL Veritabanı Kurulum Scripti
Bu script, db_schema.sql dosyasını MySQL'e yükler.
"""
import os
import subprocess
import sys

def setup_database():
    print("=" * 50)
    print("MySQL Veritabanı Kurulum Scripti")
    print("=" * 50)
    print()
    
    # .env dosyasından şifreyi oku (varsa)
    db_password = ""
    db_user = "root"
    db_host = "127.0.0.1"
    
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DB_PASSWORD="):
                    db_password = line.split("=", 1)[1].strip()
                elif line.startswith("DB_USER="):
                    db_user = line.split("=", 1)[1].strip()
                elif line.startswith("DB_HOST="):
                    db_host = line.split("=", 1)[1].strip()
    
    # Şifre yoksa kullanıcıdan iste
    if not db_password:
        db_password = input("MySQL root şifrenizi girin (boş bırakabilirsiniz): ").strip()
    
    sql_file = os.path.join(os.getcwd(), "db_schema.sql")
    
    if not os.path.exists(sql_file):
        print(f"❌ HATA: {sql_file} dosyası bulunamadı!")
        return False
    
    print(f"📄 SQL dosyası: {sql_file}")
    print(f"👤 Kullanıcı: {db_user}")
    print(f"🌐 Host: {db_host}")
    print()
    print("⏳ Veritabanı kurulumu başlatılıyor...")
    print()
    
    # MySQL komutunu oluştur
    if db_password:
        cmd = f'mysql -u {db_user} -p{db_password} -h {db_host} < "{sql_file}"'
    else:
        cmd = f'mysql -u {db_user} -h {db_host} < "{sql_file}"'
    
    try:
        # Komutu çalıştır
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print("✅ Veritabanı başarıyla kuruldu!")
            print()
            print("📋 Kurulu tablolar:")
            print("   - users (kullanıcılar)")
            print("   - authors (yazarlar)")
            print("   - categories (kategoriler)")
            print("   - books (kitaplar)")
            print("   - loans (ödünç işlemleri)")
            print("   - penalties (cezalar)")
            print()
            print("🎉 Kurulum tamamlandı! Artık Flask uygulamanızı çalıştırabilirsiniz.")
            return True
        else:
            print("❌ HATA: Veritabanı kurulumu başarısız oldu!")
            print()
            if result.stderr:
                print("Hata mesajı:")
                print(result.stderr)
            print()
            print("💡 İpuçları:")
            print("   1. MySQL servisinin çalıştığından emin olun")
            print("   2. MySQL root şifrenizi kontrol edin")
            print("   3. MySQL komut satırı araçlarının PATH'te olduğundan emin olun")
            print("   4. Alternatif olarak MySQL Workbench veya phpMyAdmin kullanabilirsiniz")
            return False
            
    except FileNotFoundError:
        print("❌ HATA: MySQL komut satırı araçları bulunamadı!")
        print()
        print("💡 MySQL yüklü değil veya PATH'te değil.")
        print("   Lütfen şu yöntemlerden birini kullanın:")
        print("   1. MySQL Workbench ile db_schema.sql dosyasını çalıştırın")
        print("   2. XAMPP/WAMP ile phpMyAdmin kullanın")
        print("   3. MySQL'i yükleyip PATH'e ekleyin")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)

