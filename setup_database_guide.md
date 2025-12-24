# MySQL Veritabanı Kurulum Rehberi

## Yöntem 1: MySQL Workbench (Önerilen - Görsel Arayüz)

1. **MySQL Workbench'i açın**
2. **Yeni bir bağlantı oluşturun:**
   - Hostname: `127.0.0.1` veya `localhost`
   - Port: `3306`
   - Username: `root`
   - Password: (MySQL root şifreniz)
3. **Bağlanın**
4. **SQL dosyasını çalıştırın:**
   - File → Open SQL Script
   - `db_schema.sql` dosyasını seçin
   - Execute (⚡) butonuna tıklayın

## Yöntem 2: phpMyAdmin (XAMPP/WAMP ile)

1. **XAMPP/WAMP Control Panel'i açın**
2. **MySQL'i başlatın**
3. **Tarayıcıda phpMyAdmin'i açın:**
   - http://localhost/phpmyadmin
4. **Import sekmesine gidin**
5. **`db_schema.sql` dosyasını seçin ve Import'a tıklayın**

## Yöntem 3: Komut Satırı (MySQL CLI)

### Windows PowerShell:
```powershell
# MySQL root şifrenizle giriş yapın
mysql -u root -p < db_schema.sql
```

### Alternatif (interaktif):
```powershell
mysql -u root -p
# Şifrenizi girin, sonra:
source C:/Users/PC/Desktop/veritabanı/db_schema.sql;
# veya
\. C:/Users/PC/Desktop/veritabanı/db_schema.sql
```

## Yöntem 4: Python Script ile (MySQL yüklüyse)

Eğer MySQL yüklüyse, Python ile de çalıştırabilirsiniz:

```python
import subprocess
import os

# MySQL root şifrenizi buraya yazın
password = "sizin_sifreniz"

# db_schema.sql dosyasının tam yolu
sql_file = os.path.join(os.getcwd(), "db_schema.sql")

# MySQL komutunu çalıştır
cmd = f'mysql -u root -p{password} < "{sql_file}"'
subprocess.run(cmd, shell=True)
```

## Kurulum Sonrası Kontrol

Veritabanının başarıyla kurulduğunu kontrol etmek için:

```sql
-- MySQL'e bağlanın
mysql -u root -p

-- Veritabanını seçin
USE smart_library;

-- Tabloları listeleyin
SHOW TABLES;

-- Örnek: Kullanıcı tablosunu kontrol edin
SELECT * FROM users;
```

## .env Dosyasını Güncelleyin

Veritabanı kurulduktan sonra, `.env` dosyasındaki şifreyi güncelleyin:

```
DB_USER=root
DB_PASSWORD=sizin_mysql_sifreniz
DB_HOST=127.0.0.1
DB_NAME=smart_library
```

## Sorun Giderme

### "Access denied" hatası:
- MySQL root şifrenizi kontrol edin
- `.env` dosyasındaki `DB_PASSWORD` değerini güncelleyin

### "Can't connect to MySQL server" hatası:
- MySQL servisinin çalıştığından emin olun
- XAMPP/WAMP kullanıyorsanız, MySQL servisini başlatın

### "Database already exists" hatası:
- Veritabanı zaten var. Silmek için:
  ```sql
  DROP DATABASE IF EXISTS smart_library;
  ```
  Sonra tekrar `db_schema.sql` dosyasını çalıştırın.

