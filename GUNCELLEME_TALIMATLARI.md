# Veritabanı Güncelleme Talimatları

## ⚠️ ÖNEMLİ: Loans Tablosu Status Enum Güncellemesi

"Data truncated for column 'status'" hatası alıyorsanız, veritabanını güncellemeniz gerekiyor.

---

## Yöntem 1: MySQL Workbench (EN KOLAY - ÖNERİLEN) ✅

### Adımlar:

1. **MySQL Workbench'i açın**
   - Başlat menüsünden "MySQL Workbench" arayın ve açın

2. **Localhost'a bağlanın**
   - Sol panelde "Local instance MySQL" veya benzer bir bağlantı görünecek
   - Üzerine tıklayın
   - Root şifrenizi girin
   - "OK" butonuna tıklayın

3. **SQL Script'i açın**
   - Üst menüden: **File → Open SQL Script**
   - Proje klasörünüze gidin: `C:\Users\PC\Desktop\veritabanı`
   - `fix_loan_status.sql` dosyasını seçin
   - "Open" butonuna tıklayın

4. **Script'i çalıştırın**
   - Üst menüden **Execute** butonuna tıklayın (⚡ simgesi)
   - Veya klavye kısayolu: `Ctrl + Shift + Enter`

5. **Sonucu kontrol edin**
   - Alt panelde "Output" sekmesinde sonuçları göreceksiniz
   - "Status enum basariyla guncellendi!" mesajını görmelisiniz

6. **Tamamlandı!** ✅
   - Artık ödünç alma istekleri çalışacak

---

## Yöntem 2: Batch Dosyası (OTOMATİK)

### Adımlar:

1. **Proje klasörüne gidin**
   - `C:\Users\PC\Desktop\veritabanı`

2. **Batch dosyasını çalıştırın**
   - `fix_loan_status.bat` dosyasına **çift tıklayın**
   - Veya PowerShell'de:
     ```powershell
     .\fix_loan_status.bat
     ```

3. **MySQL şifrenizi girin**
   - Komut satırında MySQL root şifrenizi isteyecek
   - Şifrenizi yazın ve Enter'a basın

4. **Sonucu kontrol edin**
   - "Status enum basariyla guncellendi!" mesajını görmelisiniz

---

## Yöntem 3: Komut Satırı (MANUEL)

### Adımlar:

1. **PowerShell'i açın**
   - Windows tuşu + X
   - "Windows PowerShell" veya "Terminal" seçin

2. **Proje klasörüne gidin**
   ```powershell
   cd "C:\Users\PC\Desktop\veritabanı"
   ```

3. **MySQL komutunu çalıştırın**
   ```powershell
   mysql -u root -p < fix_loan_status.sql
   ```

4. **MySQL şifrenizi girin**
   - Şifrenizi yazın ve Enter'a basın

5. **Sonucu kontrol edin**
   - Hata yoksa başarılı demektir

---

## Yöntem 4: phpMyAdmin (XAMPP/WAMP kullanıyorsanız)

### Adımlar:

1. **XAMPP/WAMP Control Panel'i açın**
   - MySQL servisinin çalıştığından emin olun

2. **phpMyAdmin'i açın**
   - Tarayıcıda: http://localhost/phpmyadmin

3. **Veritabanını seçin**
   - Sol panelden `smart_library` veritabanına tıklayın

4. **SQL sekmesine gidin**
   - Üst menüden "SQL" sekmesine tıklayın

5. **SQL kodunu yapıştırın**
   - `fix_loan_status.sql` dosyasını açın
   - İçeriğini kopyalayın
   - phpMyAdmin'deki SQL alanına yapıştırın

6. **Çalıştırın**
   - "Go" veya "Git" butonuna tıklayın

7. **Sonucu kontrol edin**
   - Başarılı mesajını görmelisiniz

---

## ❓ Sorun Giderme

### "Access denied" hatası:
- MySQL root şifrenizi kontrol edin
- `.env` dosyasındaki `DB_PASSWORD` değerini kontrol edin

### "Table doesn't exist" hatası:
- Önce `db_schema.sql` dosyasını çalıştırın
- Veritabanının kurulu olduğundan emin olun

### "Column already exists" hatası:
- Script zaten çalıştırılmış olabilir
- Veritabanı zaten güncel olabilir
- Backend'i yeniden başlatıp test edin

### MySQL komut satırı bulunamıyor:
- MySQL Workbench kullanın (Yöntem 1)
- Veya phpMyAdmin kullanın (Yöntem 4)

---

## ✅ Güncelleme Sonrası

1. **Backend'i yeniden başlatın** (gerekirse)
   ```powershell
   python app.py
   ```

2. **Tarayıcıyı yenileyin** (F5)

3. **Test edin:**
   - Student olarak giriş yapın
   - Bir kitap için "İstek Gönder" butonuna tıklayın
   - Artık 500 hatası görünmemeli

---

## 📝 Notlar

- Bu güncelleme mevcut verileri korur
- Sadece `status` enum'ını günceller
- Veri kaybı olmaz
- Güvenli bir işlemdir

