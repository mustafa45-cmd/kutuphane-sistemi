# Akıllı Kütüphane Yönetim Sistemi

Flask (Python) + MySQL + HTML/CSS/JavaScript ile geliştirilmiş kütüphane yönetim sistemi.

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
- Python 3.8+
- MySQL 5.7+ veya 8.0+
- MySQL Workbench veya phpMyAdmin (opsiyonel)

### 2. Kurulum

#### Adım 1: Python Paketlerini Yükle
```batch
install_packages.bat
```
veya manuel olarak:
```bash
python -m pip install -r requirements.txt
```

#### Adım 2: MySQL Veritabanını Kur
```batch
setup_database.bat
```
veya MySQL Workbench ile:
- File → Open SQL Script → `db_schema.sql` seçin
- Execute (⚡) butonuna tıklayın

#### Adım 3: .env Dosyasını Düzenle
`.env` dosyasını açın ve MySQL şifrenizi ekleyin:
```
DB_PASSWORD=sizin_mysql_sifreniz
```

#### Adım 4: Test Kullanıcıları Oluştur (Opsiyonel)
```batch
create_test_user.bat
```

### 3. Uygulamayı Başlat

```batch
start.bat
```

Uygulama başladıktan sonra:
- **Frontend**: http://localhost:5000/static/index.html
- **API Health Check**: http://localhost:5000/api/health

## 📁 Proje Yapısı

```
veritabanı/
├── app.py                 # Ana Flask uygulaması
├── requirements.txt       # Python paketleri
├── db_schema.sql          # MySQL veritabanı şeması
├── .env                   # Ortam değişkenleri (oluşturulacak)
│
├── src/
│   ├── config.py         # Yapılandırma
│   ├── db.py             # Veritabanı bağlantısı
│   ├── models.py         # ORM modelleri
│   ├── security.py       # JWT ve şifreleme
│   ├── decorators.py     # JWT decorator'ları
│   └── routes/
│       ├── auth_routes.py    # Kimlik doğrulama
│       ├── book_routes.py    # Kitap yönetimi
│       ├── loan_routes.py    # Ödünç/iade işlemleri
│       └── admin_routes.py   # Admin CRUD işlemleri
│
├── static/
│   ├── index.html        # Frontend arayüzü
│   ├── styles.css        # CSS stilleri
│   └── main.js          # JavaScript kodları
│
└── Batch Dosyaları:
    ├── start.bat              # Uygulamayı başlat
    ├── setup_database.bat    # Veritabanını kur
    ├── create_test_user.bat  # Test kullanıcıları oluştur
    └── install_packages.bat  # Paketleri yükle
```

## 🔑 Test Kullanıcıları

`create_test_user.bat` çalıştırıldıktan sonra:

- **Admin**: `admin@example.com` / `admin123`
- **Öğrenci**: `student@example.com` / `student123`

## 📡 API Endpoint'leri

### Kimlik Doğrulama
- `POST /api/auth/register` - Kayıt ol
- `POST /api/auth/login` - Giriş yap

### Kitaplar
- `GET /api/books/?q=...` - Kitap ara/listele
- `POST /api/books/` - Kitap ekle (Admin)
- `PUT /api/books/<id>` - Kitap güncelle (Admin)
- `DELETE /api/books/<id>` - Kitap sil (Admin)

### Ödünç İşlemleri
- `POST /api/loans/` - Kitap ödünç al
- `POST /api/loans/<id>/return` - Kitap iade et
- `GET /api/loans/my` - Ödünçlerimi listele
- `GET /api/loans/penalties` - Ceza listesi

### Admin
- `GET /api/admin/authors` - Yazar listesi
- `POST /api/admin/authors` - Yazar ekle
- `PUT /api/admin/authors/<id>` - Yazar güncelle
- `DELETE /api/admin/authors/<id>` - Yazar sil
- (Aynı endpoint'ler categories ve users için de geçerli)

## 🛠️ Sorun Giderme

### "ModuleNotFoundError: No module named 'flask'"
```batch
install_packages.bat
```

### "Can't connect to MySQL server"
- MySQL servisinin çalıştığından emin olun
- `.env` dosyasındaki `DB_PASSWORD` değerini kontrol edin
- `DB_HOST` değerinin doğru olduğundan emin olun

### "Access denied for user"
- MySQL root şifrenizi kontrol edin
- `.env` dosyasındaki `DB_PASSWORD` değerini güncelleyin

### "Database 'smart_library' doesn't exist"
```batch
setup_database.bat
```

## 📝 Notlar

- Uygulama `debug=True` modunda çalışır (geliştirme için)
- Production'da `SECRET_KEY` değerini değiştirin
- MySQL bağlantı bilgileri `.env` dosyasında saklanır
- Frontend ve backend aynı port'ta çalışır (CORS aktif)

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

