-- Ödünç alma sistemini istek/onay sistemine çevirme
-- Loan status enum'ını güncelle

USE smart_library;

-- Mevcut enum'ı değiştirmek için önce tabloyu güncelle
ALTER TABLE loans MODIFY COLUMN status ENUM(
    'requested',    -- İstek gönderildi (beklemede)
    'approved',     -- Admin onayladı (henüz alınmadı)
    'borrowed',     -- Kitap ödünç alındı
    'returned',     -- Kitap iade edildi
    'late',         -- Geç iade
    'rejected'      -- İstek reddedildi
) NOT NULL DEFAULT 'requested';

-- Mevcut kayıtları güncelle (eğer varsa)
UPDATE loans SET status = 'borrowed' WHERE status = 'borrowed' AND return_date IS NULL;
UPDATE loans SET status = 'returned' WHERE status = 'returned' OR return_date IS NOT NULL;

