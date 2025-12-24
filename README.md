## Akıllı Kütüphane Yönetim Sistemi (Flask + MySQL)

Bu proje, verilen ödev dokümanındaki **Akıllı Kütüphane Yönetim Sistemi** gereksinimlerine göre hazırlanmış bir örnek uygulamadır.  
Backend: **Flask (Python)**, Veritabanı: **MySQL**, Frontend: **HTML/CSS + JavaScript**.  
Referans: `proje2025-2026.pdf` (`file:///d%3A/%C4%B0ndirilenler/proje2025-2026.pdf`)

### Kurulum

1. Sanal ortam oluştur (opsiyonel, ama tavsiye edilir):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Gerekli paketleri yükle:
   ```bash
   pip install -r requirements.txt
   ```

3. MySQL veritabanını oluştur:
   - MySQL’e bağlan ve `db_schema.sql` dosyasını çalıştır:
   ```sql
   SOURCE C:/Users/PC/Desktop/veritabanı/db_schema.sql;
   ```
   - `users` tablosunda hazır bir admin kullanıcı var, şifresinin hash’ini kendin güncelleyebilirsin.

4. `.env` dosyası oluştur:
   ```env
   SECRET_KEY=degistir
   DB_USER=root
   DB_PASSWORD=senin_sifren
   DB_HOST=127.0.0.1
   DB_NAME=smart_library
   ```

5. Backend’i çalıştır:
   ```bash
   python app.py
   ```

6. Frontend’i aç:
   - `static/index.html` dosyasını tarayıcıda aç.
   - API adresi varsayılan olarak `http://localhost:5000/api` şeklindedir (`static/main.js` içinde).

### Ana Özellikler

- **Veritabanı**
  - Tablolar: `users`, `authors`, `categories`, `books`, `loans`, `penalties`
  - İlişkiler: kitap–yazar, kitap–kategori, kullanıcı–ödünç, ödünç–ceza
  - **Stored Procedure**:
    - `sp_borrow_book(user_id, book_id, loan_days)`
    - `sp_return_book(loan_id)`
  - **Trigger**:
    - `trg_create_penalty_after_return`: Geç iade durumunda otomatik ceza kaydı oluşturur.

- **Backend (Flask)**
  - JWT tabanlı kimlik doğrulama (`/api/auth/login`, `/api/auth/register`)
  - Kitap arama ve listeleme (`/api/books/`)
  - Ödünç alma / iade (`/api/loans/`, `/api/loans/<id>/return`, `/api/loans/my`)
  - Ceza görüntüleme (`/api/loans/penalties`)
  - Admin uçları (`/api/admin/...`):
    - Yazar CRUD
    - Kategori CRUD
    - Kullanıcı oluşturma (admin tarafından)

- **Frontend (HTML/CSS + JS)**
  - Login formu
  - Kitap arama ve listeleme
  - Ödünç alma butonu
  - Kullanıcının ödünç aldığı kitaplar ve iade işlemi

### Test / Postman

- Çalışan API uçlarını Postman ile test edebilirsin:
  - `POST /api/auth/login`
  - `GET /api/books/?q=python`
  - `POST /api/loans/`
  - `POST /api/loans/{id}/return`
  - `GET /api/loans/my`
  - `GET /api/loans/penalties`
  - `GET/POST/PUT/DELETE /api/admin/authors`
  - `GET/POST/PUT/DELETE /api/admin/categories`

Swagger veya Postman koleksiyonu istersen, bu README’ye eklenebilir.



