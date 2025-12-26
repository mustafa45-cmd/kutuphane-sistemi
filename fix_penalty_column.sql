-- ============================================================================
-- Ceza Sütunu Düzeltme Scripti (Basit Versiyon)
-- ============================================================================
-- Bu script sadece eksik sütunu ekler, mevcut verileri korur
-- ============================================================================

USE smart_library;

-- penalty_end_date sütununu ekle (eğer yoksa hata vermez, sadece uyarı verir)
-- Önce kontrol et, sonra ekle
SET @dbname = DATABASE();
SET @tablename = "penalties";
SET @columnname = "penalty_end_date";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = @columnname)
  ) > 0,
  "SELECT 'Sütun zaten var' as result;",
  CONCAT("ALTER TABLE ", @tablename, " ADD COLUMN ", @columnname, " DATE NULL;")
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists;

-- amount sütununu kaldır (eğer varsa)
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = 'amount')
  ) > 0,
  "ALTER TABLE penalties DROP COLUMN amount;",
  "SELECT 'amount sütunu yok' as result;"
));
PREPARE dropIfExists FROM @preparedStatement;
EXECUTE dropIfExists;
DEALLOCATE PREPARE dropIfExists;

-- is_paid sütununu kaldır (eğer varsa)
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      (table_name = @tablename)
      AND (table_schema = @dbname)
      AND (column_name = 'is_paid')
  ) > 0,
  "ALTER TABLE penalties DROP COLUMN is_paid;",
  "SELECT 'is_paid sütunu yok' as result;"
));
PREPARE dropIfExists2 FROM @preparedStatement;
EXECUTE dropIfExists2;
DEALLOCATE PREPARE dropIfExists2;

-- Mevcut cezalar için bitiş tarihi ayarla (eğer NULL ise)
UPDATE penalties 
SET penalty_end_date = DATE_ADD(created_at, INTERVAL 30 DAY)
WHERE penalty_end_date IS NULL;

-- Sütunu NOT NULL yap
ALTER TABLE penalties 
  MODIFY COLUMN penalty_end_date DATE NOT NULL DEFAULT (DATE_ADD(CURDATE(), INTERVAL 30 DAY));

SELECT 'Ceza sütunu basariyla eklendi!' as result;

