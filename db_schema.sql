-- ============================================================================
-- Akıllı Kütüphane Yönetim Sistemi - MySQL Veritabanı Şeması
-- ============================================================================
-- 
-- Bu dosya, kütüphane yönetim sistemi için gerekli tüm veritabanı yapısını içerir:
--   - Tablolar (users, authors, categories, books, loans, penalties)
--   - Foreign key ilişkileri
--   - Indexler (performans için)
--   - Stored procedure'ler (sp_borrow_book, sp_return_book)
--   - Trigger'lar (trg_create_penalty_after_return)
--
-- Referans: `proje2025-2026.pdf` (Akıllı Kütüphane Yönetim Sistemi)
--
-- Kullanım:
--   1. MySQL komut satırı: mysql -u root -p < db_schema.sql
--   2. MySQL Workbench: File > Run SQL Script
--   3. phpMyAdmin: SQL sekmesi > Import
--   4. Python script: python setup_database.py
-- ============================================================================

-- Veritabanını oluştur (yoksa)
CREATE DATABASE IF NOT EXISTS smart_library
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_library;

-- ============================================================================
-- TABLOLAR
-- ============================================================================

-- Kullanıcılar Tablosu
-- Sistemdeki tüm kullanıcıları (öğrenci, personel, admin) içerir
-- Roller: student (öğrenci), staff (personel), admin (yönetici)
CREATE TABLE users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(100)     NOT NULL,
    email        VARCHAR(120)     NOT NULL UNIQUE,
    password_hash VARCHAR(255)    NOT NULL,
    role         ENUM('student','staff','admin') NOT NULL DEFAULT 'student',
    is_active    TINYINT(1)       NOT NULL DEFAULT 1,
    created_at   DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Yazarlar Tablosu
-- Kitap yazarlarını içerir
CREATE TABLE authors (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(120) NOT NULL,
    bio       TEXT         NULL  -- Yazar biyografisi (opsiyonel)
);

-- Kategoriler Tablosu
-- Kitap kategorilerini içerir (örn: Roman, Polisiye, Bilim Kurgu)
CREATE TABLE categories (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(80) NOT NULL UNIQUE,  -- Kategori adı (benzersiz)
    description TEXT      NULL              -- Kategori açıklaması (opsiyonel)
);

-- Kitaplar Tablosu
-- Kütüphanedeki kitapları içerir
-- Her kitap bir yazara ve bir kategoriye aittir
CREATE TABLE books (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,           -- Kitap başlığı
    isbn          VARCHAR(20)  NOT NULL UNIQUE,    -- ISBN numarası (benzersiz)
    author_id     INT          NOT NULL,           -- Yazar ID (foreign key)
    category_id   INT          NOT NULL,           -- Kategori ID (foreign key)
    total_copies  INT          NOT NULL DEFAULT 1,  -- Toplam kopya sayısı
    available_copies INT       NOT NULL DEFAULT 1,  -- Mevcut kopya sayısı
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Kayıt tarihi
    CONSTRAINT fk_books_author
      FOREIGN KEY (author_id) REFERENCES authors(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_books_category
      FOREIGN KEY (category_id) REFERENCES categories(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Ödünç Alma Tablosu
-- Kullanıcıların kitapları ödünç alma işlemlerini içerir
-- Durumlar: borrowed (ödünç alındı), returned (iade edildi), late (geç iade)
-- Not: Bu tablo daha sonra 'requested', 'approved', 'rejected' durumları eklenmiştir
CREATE TABLE loans (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL,          -- Kullanıcı ID (foreign key)
    book_id        INT          NOT NULL,          -- Kitap ID (foreign key)
    loan_date      DATE         NOT NULL,          -- Ödünç alma tarihi
    due_date       DATE         NOT NULL,          -- İade tarihi
    return_date    DATE         NULL,              -- Gerçek iade tarihi (opsiyonel)
    status         ENUM('borrowed','returned','late') NOT NULL DEFAULT 'borrowed',  -- Durum
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Kayıt tarihi
    CONSTRAINT fk_loans_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_loans_book
      FOREIGN KEY (book_id) REFERENCES books(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Cezalar Tablosu
-- Gecikmiş kitap iadeleri için otomatik olarak oluşturulan cezaları içerir
-- Trigger (trg_create_penalty_after_return) ile otomatik oluşturulur
CREATE TABLE penalties (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    loan_id      INT          NOT NULL UNIQUE,     -- Ödünç kaydı ID (benzersiz, foreign key)
    user_id      INT          NOT NULL,            -- Kullanıcı ID (foreign key)
    amount       DECIMAL(10,2) NOT NULL,          -- Ceza tutarı (10,2 formatında)
    days_late    INT          NOT NULL,           -- Gecikme gün sayısı
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Ceza oluşturulma tarihi
    is_paid      TINYINT(1)   NOT NULL DEFAULT 0,  -- Ceza ödendi mi? (0: hayır, 1: evet)
    CONSTRAINT fk_penalties_loan
      FOREIGN KEY (loan_id) REFERENCES loans(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_penalties_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- İNDEKSLER (Performans İyileştirmeleri)
-- ============================================================================
-- Arama ve sorgu performansını artırmak için oluşturulan indeksler

CREATE INDEX idx_books_title ON books(title);  -- Kitap başlığına göre arama
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_category ON books(category_id);
CREATE INDEX idx_loans_user ON loans(user_id);
CREATE INDEX idx_loans_book ON loans(book_id);

-- ============================================================================
-- STORED PROCEDURE'LER
-- ============================================================================

-- Kitap Ödünç Verme Stored Procedure
-- İş kuralları:
--   - Kitap mevcut olmalı
--   - Müsait kopya sayısı > 0 olmalı
--   - Ödünç kaydı oluşturulur
--   - Kitap mevcut kopya sayısı 1 azalır
DELIMITER $$
CREATE PROCEDURE sp_borrow_book(
    IN p_user_id INT,
    IN p_book_id INT,
    IN p_loan_days INT
)
BEGIN
    DECLARE v_available INT;

    SELECT available_copies INTO v_available
    FROM books
    WHERE id = p_book_id
    FOR UPDATE;

    IF v_available IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Book not found';
    END IF;

    IF v_available <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No available copies for this book';
    END IF;

    INSERT INTO loans(user_id, book_id, loan_date, due_date, status)
    VALUES (
        p_user_id,
        p_book_id,
        CURDATE(),
        DATE_ADD(CURDATE(), INTERVAL p_loan_days DAY),
        'borrowed'
    );

    UPDATE books
    SET available_copies = available_copies - 1
    WHERE id = p_book_id;
END$$
DELIMITER ;

-- Kitap İade Etme Stored Procedure
-- İş kuralları:
--   - Ödünç kaydı bulunmalı
--   - İade tarihi güncellenir
--   - Durum 'returned' olur
--   - Kitap mevcut kopya sayısı 1 artar
--   - Gecikme varsa trigger otomatik ceza oluşturur
DELIMITER $$
CREATE PROCEDURE sp_return_book(
    IN p_loan_id INT
)
BEGIN
    DECLARE v_book_id INT;

    SELECT book_id INTO v_book_id
    FROM loans
    WHERE id = p_loan_id
    FOR UPDATE;

    IF v_book_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Loan not found';
    END IF;

    UPDATE loans
    SET return_date = CURDATE(),
        status = 'returned'
    WHERE id = p_loan_id;

    UPDATE books
    SET available_copies = available_copies + 1
    WHERE id = v_book_id;
END$$
DELIMITER ;

-- ============================================================================
-- TRIGGER'LAR
-- ============================================================================

-- Geç İade Ceza Oluşturma Trigger'ı
-- Çalışma zamanı: loans tablosunda UPDATE işlemi sonrası
-- Mantık:
--   - return_date > due_date ise (geç iade)
--   - Gecikme gün sayısı hesaplanır
--   - Günlük 5 birim ceza uygulanır (days_late * 5.00)
--   - penalties tablosuna yeni kayıt eklenir
--   - Eğer ceza zaten varsa tekrar eklenmez
DELIMITER $$
CREATE TRIGGER trg_create_penalty_after_return
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    DECLARE v_days_late INT;

    IF NEW.return_date IS NOT NULL
       AND NEW.return_date > NEW.due_date
    THEN
        SET v_days_late = DATEDIFF(NEW.return_date, NEW.due_date);

        IF NOT EXISTS (SELECT 1 FROM penalties WHERE loan_id = NEW.id) THEN
            INSERT INTO penalties(loan_id, user_id, amount, days_late)
            VALUES (
                NEW.id,
                NEW.user_id,
                v_days_late * 5.00, -- günlük 5 birim ceza
                v_days_late
            );
        END IF;
    END IF;
END$$
DELIMITER ;

-- ============================================================================
-- ÖRNEK VERİLER (Opsiyonel)
-- ============================================================================
-- Not: Bu veriler sadece örnek amaçlıdır.
-- Gerçek kullanıcılar create_test_user.py scripti ile oluşturulmalıdır.

INSERT INTO users(full_name, email, password_hash, role)
VALUES
('Admin User', 'admin@example.com', 'CHANGE_ME_HASH', 'admin');





