"""
Veritabanı Modelleri
SQLAlchemy ORM modelleri - Veritabanı tablolarını Python sınıfları olarak temsil eder.
"""

from datetime import datetime, date

from src.db import db


class User(db.Model):
    """
    Kullanıcı Modeli
    Sistemdeki tüm kullanıcıları (öğrenci, personel, admin) temsil eder.
    """
    __tablename__ = "users"

    # Temel bilgiler
    id = db.Column(db.Integer, primary_key=True)                                    # Birincil anahtar
    full_name = db.Column(db.String(100), nullable=False)                           # Ad soyad
    email = db.Column(db.String(120), unique=True, nullable=False)                  # E-posta (benzersiz)
    password_hash = db.Column(db.String(255), nullable=False)                     # Şifre hash'i (pbkdf2_sha256)
    role = db.Column(db.Enum("student", "staff", "admin", name="role_enum"), nullable=False)  # Kullanıcı rolü
    is_active = db.Column(db.Boolean, nullable=False, default=True)                 # Hesap aktif mi?
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)     # Kayıt tarihi

    # İlişkiler
    loans = db.relationship("Loan", back_populates="user", lazy=True)               # Kullanıcının ödünç aldığı kitaplar


class Author(db.Model):
    """
    Yazar Modeli
    Kitap yazarlarını temsil eder.
    """
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)                                    # Birincil anahtar
    name = db.Column(db.String(120), nullable=False)                                # Yazar adı
    bio = db.Column(db.Text)                                                        # Yazar biyografisi (opsiyonel)

    # İlişkiler
    books = db.relationship("Book", back_populates="author", lazy=True)              # Yazarın kitapları


class Category(db.Model):
    """
    Kategori Modeli
    Kitap kategorilerini temsil eder (örn: Roman, Bilim, Tarih).
    """
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)                                    # Birincil anahtar
    name = db.Column(db.String(80), nullable=False, unique=True)                    # Kategori adı (benzersiz)
    description = db.Column(db.Text)                                                # Kategori açıklaması (opsiyonel)

    # İlişkiler
    books = db.relationship("Book", back_populates="category", lazy=True)            # Bu kategorideki kitaplar


class Book(db.Model):
    """
    Kitap Modeli
    Kütüphanedeki kitapları temsil eder.
    """
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)                                    # Birincil anahtar
    title = db.Column(db.String(200), nullable=False)                               # Kitap başlığı
    isbn = db.Column(db.String(20), nullable=False, unique=True)                     # ISBN numarası (benzersiz)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)  # Yazar ID (yabancı anahtar)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)  # Kategori ID (yabancı anahtar)
    total_copies = db.Column(db.Integer, nullable=False, default=1)                  # Toplam kopya sayısı
    available_copies = db.Column(db.Integer, nullable=False, default=1)             # Mevcut kopya sayısı
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)     # Kayıt tarihi

    # İlişkiler
    author = db.relationship("Author", back_populates="books")                       # Kitabın yazarı
    category = db.relationship("Category", back_populates="books")                   # Kitabın kategorisi
    loans = db.relationship("Loan", back_populates="book", lazy=True)                # Bu kitabın ödünç alma kayıtları


class Loan(db.Model):
    """
    Ödünç Alma Modeli
    Kullanıcıların kitapları ödünç alma işlemlerini temsil eder.
    
    Durumlar:
    - requested: İstek gönderildi (öğrenci tarafından)
    - approved: İstek onaylandı (admin tarafından)
    - borrowed: Kitap ödünç alındı
    - returned: Kitap iade edildi
    - late: Gecikmiş iade
    - rejected: İstek reddedildi
    """
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)                                      # Birincil anahtar
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)      # Kullanıcı ID (yabancı anahtar)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)      # Kitap ID (yabancı anahtar)
    loan_date = db.Column(db.Date, nullable=False, default=date.today)               # Ödünç alma tarihi
    due_date = db.Column(db.Date, nullable=False)                                  # İade tarihi
    return_date = db.Column(db.Date)                                                # Gerçek iade tarihi (opsiyonel)
    status = db.Column(
        db.Enum("requested", "approved", "borrowed", "returned", "late", "rejected", name="loan_status_enum"),
        nullable=False,
        default="requested",                                                          # Varsayılan durum: istek gönderildi
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)     # Kayıt tarihi

    # İlişkiler
    user = db.relationship("User", back_populates="loans")                           # Ödünç alan kullanıcı
    book = db.relationship("Book", back_populates="loans")                           # Ödünç alınan kitap
    penalty = db.relationship("Penalty", back_populates="loan", uselist=False, lazy=True)  # Gecikme cezası (varsa)


class Penalty(db.Model):
    """
    Ceza Modeli
    Gecikmiş kitap iadeleri için otomatik olarak oluşturulan cezaları temsil eder.
    """
    __tablename__ = "penalties"

    id = db.Column(db.Integer, primary_key=True)                                     # Birincil anahtar
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), unique=True, nullable=False)  # Ödünç alma ID (benzersiz, yabancı anahtar)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)      # Kullanıcı ID (yabancı anahtar)
    amount = db.Column(db.Numeric(10, 2), nullable=False)                           # Ceza tutarı (10,2 formatında)
    days_late = db.Column(db.Integer, nullable=False)                               # Gecikme gün sayısı
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)     # Ceza oluşturulma tarihi
    is_paid = db.Column(db.Boolean, nullable=False, default=False)                   # Ceza ödendi mi?

    # İlişkiler
    loan = db.relationship("Loan", back_populates="penalty")                         # İlgili ödünç alma kaydı



