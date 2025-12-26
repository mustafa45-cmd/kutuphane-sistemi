-- ============================================================================
-- Ceza Sütunu Düzeltme Scripti (En Basit Versiyon)
-- ============================================================================
-- Bu script sadece eksik sütunu ekler
-- Eğer hata alırsanız, sadece ilgili satırı çalıştırın
-- ============================================================================

USE smart_library;

-- 1. penalty_end_date sütununu ekle
ALTER TABLE penalties ADD COLUMN penalty_end_date DATE NULL;

-- 2. Mevcut cezalar için bitiş tarihi ayarla
UPDATE penalties 
SET penalty_end_date = DATE_ADD(created_at, INTERVAL 30 DAY)
WHERE penalty_end_date IS NULL;

-- 3. Sütunu NOT NULL yap
ALTER TABLE penalties 
  MODIFY COLUMN penalty_end_date DATE NOT NULL DEFAULT (DATE_ADD(CURDATE(), INTERVAL 30 DAY));

-- 4. (Opsiyonel) Eski sütunları kaldır (eğer varsa ve hata vermiyorsa)
-- ALTER TABLE penalties DROP COLUMN amount;
-- ALTER TABLE penalties DROP COLUMN is_paid;

SELECT 'Ceza sütunu basariyla eklendi!' as result;

