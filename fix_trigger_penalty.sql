-- ============================================================================
-- Trigger Güncelleme Scripti - Ceza Sistemi
-- ============================================================================
-- 
-- Bu script, veritabanındaki trigger'ı yeni ceza sistemine göre günceller.
-- Eski sistem: amount ve is_paid sütunları
-- Yeni sistem: penalty_end_date sütunu (1 ay kitap alamama)
--
-- Kullanım:
--   mysql -u root -p smart_library < fix_trigger_penalty.sql
--   veya MySQL Workbench / phpMyAdmin ile çalıştırın
-- ============================================================================

USE smart_library;

-- Mevcut trigger'ı sil
DROP TRIGGER IF EXISTS trg_create_penalty_after_return;

-- Yeni trigger'ı oluştur (penalty_end_date kullanarak)
DELIMITER $$
CREATE TRIGGER trg_create_penalty_after_return
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    DECLARE v_days_late INT;
    DECLARE v_penalty_end_date DATE;

    -- Sadece return_date set edildiğinde ve gecikme varsa çalış
    IF NEW.return_date IS NOT NULL
       AND OLD.return_date IS NULL
       AND NEW.return_date > NEW.due_date
    THEN
        -- Gecikme gün sayısını hesapla
        SET v_days_late = DATEDIFF(NEW.return_date, NEW.due_date);
        
        -- Ceza bitiş tarihini hesapla (iade tarihinden 30 gün sonra = 1 ay)
        SET v_penalty_end_date = DATE_ADD(NEW.return_date, INTERVAL 30 DAY);

        -- Eğer bu loan için zaten bir ceza yoksa oluştur
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

SELECT 'Trigger basariyla guncellendi! Artik penalty_end_date kullaniliyor.' as result;



