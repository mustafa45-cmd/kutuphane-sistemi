-- ============================================================================
-- Ceza Sistemi Güncelleme Scripti
-- ============================================================================
-- 
-- Bu script, para cezası sistemini 1 ay kitap alamama cezasına çevirir.
-- 
-- Değişiklikler:
--   - penalties.amount sütunu kaldırılır
--   - penalties.is_paid sütunu kaldırılır
--   - penalties.penalty_end_date sütunu eklenir (1 ay sonra)
--
-- Kullanım:
--   mysql -u root -p smart_library < update_penalty_system.sql
--   veya MySQL Workbench / phpMyAdmin ile çalıştırın
-- ============================================================================

USE smart_library;

-- Mevcut cezaları geçici sütunlara kopyala
ALTER TABLE penalties ADD COLUMN penalty_end_date_temp DATE NULL;
ALTER TABLE penalties ADD COLUMN days_late_temp INT NULL;

-- Mevcut verileri kopyala (eğer varsa)
UPDATE penalties 
SET days_late_temp = days_late,
    penalty_end_date_temp = DATE_ADD(created_at, INTERVAL 30 DAY);

-- Eski sütunları sil
ALTER TABLE penalties DROP COLUMN amount;
ALTER TABLE penalties DROP COLUMN is_paid;

-- Yeni sütunları ekle
ALTER TABLE penalties 
  ADD COLUMN penalty_end_date DATE NOT NULL DEFAULT (DATE_ADD(CURDATE(), INTERVAL 30 DAY));

-- Geçici sütunlardan verileri kopyala
UPDATE penalties 
SET penalty_end_date = COALESCE(penalty_end_date_temp, DATE_ADD(created_at, INTERVAL 30 DAY)),
    days_late = COALESCE(days_late_temp, 0)
WHERE penalty_end_date_temp IS NOT NULL OR days_late_temp IS NOT NULL;

-- Geçici sütunları sil
ALTER TABLE penalties DROP COLUMN penalty_end_date_temp;
ALTER TABLE penalties DROP COLUMN days_late_temp;

-- Trigger'ı güncelle
DROP TRIGGER IF EXISTS trg_create_penalty_after_return;

DELIMITER $$
CREATE TRIGGER trg_create_penalty_after_return
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    DECLARE v_days_late INT;
    DECLARE v_penalty_end_date DATE;

    IF NEW.return_date IS NOT NULL
       AND NEW.return_date > NEW.due_date
    THEN
        SET v_days_late = DATEDIFF(NEW.return_date, NEW.due_date);
        SET v_penalty_end_date = DATE_ADD(NEW.return_date, INTERVAL 30 DAY); -- 1 ay = 30 gün

        IF NOT EXISTS (SELECT 1 FROM penalties WHERE loan_id = NEW.id) THEN
            INSERT INTO penalties(loan_id, user_id, days_late, penalty_end_date)
            VALUES (
                NEW.id,
                NEW.user_id,
                v_days_late,
                v_penalty_end_date
            );
        END IF;
    END IF;
END$$
DELIMITER ;

SELECT 'Ceza sistemi basariyla guncellendi! Artik para cezasi yerine 1 ay kitap alamama cezasi uygulanacak.' as result;

