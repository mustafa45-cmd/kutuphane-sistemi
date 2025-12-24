-- Akıllı Kütüphane Yönetim Sistemi - MySQL Şeması
-- Referans: `proje2025-2026.pdf` (Akıllı Kütüphane Yönetim Sistemi)

CREATE DATABASE IF NOT EXISTS smart_library
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_library;

-- Kullanıcı rolleri için enum benzeri çözüm (student, staff, admin)
CREATE TABLE users (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(100)     NOT NULL,
    email        VARCHAR(120)     NOT NULL UNIQUE,
    password_hash VARCHAR(255)    NOT NULL,
    role         ENUM('student','staff','admin') NOT NULL DEFAULT 'student',
    is_active    TINYINT(1)       NOT NULL DEFAULT 1,
    created_at   DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE authors (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(120) NOT NULL,
    bio       TEXT         NULL
);

CREATE TABLE categories (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(80) NOT NULL UNIQUE,
    description TEXT      NULL
);

CREATE TABLE books (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    title         VARCHAR(200) NOT NULL,
    isbn          VARCHAR(20)  NOT NULL UNIQUE,
    author_id     INT          NOT NULL,
    category_id   INT          NOT NULL,
    total_copies  INT          NOT NULL DEFAULT 1,
    available_copies INT       NOT NULL DEFAULT 1,
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_books_author
      FOREIGN KEY (author_id) REFERENCES authors(id)
      ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_books_category
      FOREIGN KEY (category_id) REFERENCES categories(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE loans (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL,
    book_id        INT          NOT NULL,
    loan_date      DATE         NOT NULL,
    due_date       DATE         NOT NULL,
    return_date    DATE         NULL,
    status         ENUM('borrowed','returned','late') NOT NULL DEFAULT 'borrowed',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_loans_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_loans_book
      FOREIGN KEY (book_id) REFERENCES books(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE penalties (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    loan_id      INT          NOT NULL UNIQUE,
    user_id      INT          NOT NULL,
    amount       DECIMAL(10,2) NOT NULL,
    days_late    INT          NOT NULL,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_paid      TINYINT(1)   NOT NULL DEFAULT 0,
    CONSTRAINT fk_penalties_loan
      FOREIGN KEY (loan_id) REFERENCES loans(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_penalties_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

-- Örnek indeksler
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_books_category ON books(category_id);
CREATE INDEX idx_loans_user ON loans(user_id);
CREATE INDEX idx_loans_book ON loans(book_id);

-- STORED PROCEDURE: Kitap ödünç verme (iş kuralları ile)
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

-- STORED PROCEDURE: Kitap iade etme
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

-- TRIGGER: Geç iade durumunda otomatik ceza oluşturma
-- Geri dönüş yapıldığında, return_date > due_date ise satır ekler
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

-- Örnek başlangıç verileri
INSERT INTO users(full_name, email, password_hash, role)
VALUES
('Admin User', 'admin@example.com', 'CHANGE_ME_HASH', 'admin');



