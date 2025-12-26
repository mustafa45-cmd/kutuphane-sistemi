-- ============================================================================
-- Loan Status Enum Güvenli Güncelleme Scripti
-- ============================================================================
-- 
-- Bu script, loans tablosundaki status enum'ını güvenli şekilde günceller.
-- Mevcut veriler korunur ve yeni enum değerlerine uygun şekilde dönüştürülür.
--
-- Yeni enum değerleri:
--   - requested: İstek gönderildi (beklemede)
--   - approved: Admin onayladı (henüz alınmadı)
--   - borrowed: Kitap ödünç alındı
--   - returned: Kitap iade edildi
--   - late: Geç iade
--   - rejected: İstek reddedildi
--
-- Kullanım:
--   mysql -u root -p smart_library < fix_loan_status.sql
--   veya MySQL Workbench / phpMyAdmin ile çalıştırın
--
-- Not: Bu script veri kaybına neden olmaz. Geçici sütun kullanarak
--      güvenli bir şekilde güncelleme yapar.
-- ============================================================================

USE smart_library;

-- Önce mevcut verileri kontrol et
SELECT status, COUNT(*) as count FROM loans GROUP BY status;

-- Eğer loans tablosunda veri varsa, önce geçici bir sütun oluştur
ALTER TABLE loans ADD COLUMN status_temp VARCHAR(20) NULL;

-- Mevcut status değerlerini geçici sütuna kopyala
UPDATE loans SET status_temp = status;

-- Eski status sütununu sil
ALTER TABLE loans DROP COLUMN status;

-- Yeni status sütununu oluştur
ALTER TABLE loans ADD COLUMN status ENUM(
    'requested',    -- İstek gönderildi (beklemede)
    'approved',     -- Admin onayladı (henüz alınmadı)
    'borrowed',     -- Kitap ödünç alındı
    'returned',     -- Kitap iade edildi
    'late',         -- Geç iade
    'rejected'      -- İstek reddedildi
) NOT NULL DEFAULT 'requested';

-- Geçici sütundaki değerleri yeni sütuna kopyala
UPDATE loans SET status = 
    CASE 
        WHEN status_temp = 'borrowed' AND return_date IS NULL THEN 'borrowed'
        WHEN status_temp = 'returned' OR return_date IS NOT NULL THEN 
            CASE 
                WHEN return_date > due_date THEN 'late'
                ELSE 'returned'
            END
        WHEN status_temp = 'late' THEN 'late'
        ELSE 'requested'
    END;

-- Geçici sütunu sil
ALTER TABLE loans DROP COLUMN status_temp;

-- Sonucu kontrol et
SELECT status, COUNT(*) as count FROM loans GROUP BY status;

SELECT 'Status enum basariyla guncellendi!' as result;
