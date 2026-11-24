-- =====================================================================
-- Yemekhane Otomasyonu · Aşama 4 Değişiklik Talebi Migration Dosyası
-- Dosya: 04_degisiklik.sql
-- Kapsam:
--   1. Yarım Porsiyon Özelliği:
--      - rezervasyonlar tablosuna 'porsiyon' kolonu (tam/yarim, varsayılan 'tam')
--      - sp_rezervasyon_yap saklı yordamının 3 parametreli güncellenmesi
--      - Öğle/Akşam için %60 ücret hesaplaması, Kahvaltı için engel
--      - Geçmiş rezervasyonların 'tam' kabul edilmesi
--   2. Alerjen Uyarısı Özelliği:
--      - kullanici_alerjenleri tablosu (kullanici_id, alerjen_id)
-- =====================================================================
SET NAMES utf8mb4;
USE yemekhane;

-- ---------------------------------------------------------------------
-- 1. Rezervasyonlar tablosuna porsiyon sütunu ekleme (idempotent)
--    Geçmiş tüm kayıtlar varsayılan değer ('tam') sayesinde tam porsiyon sayılır.
-- ---------------------------------------------------------------------
SET @col_exists = (
    SELECT COUNT(*) 
      FROM information_schema.COLUMNS 
     WHERE TABLE_SCHEMA = 'yemekhane' 
       AND TABLE_NAME = 'rezervasyonlar' 
       AND COLUMN_NAME = 'porsiyon'
);
SET @sql_add_col = IF(
    @col_exists = 0,
    'ALTER TABLE rezervasyonlar ADD COLUMN porsiyon ENUM(\'tam\', \'yarim\') NOT NULL DEFAULT \'tam\' AFTER ucret;',
    'SELECT \'porsiyon kolonu zaten mevcut\' AS bilgi;'
);
PREPARE stmt FROM @sql_add_col;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ---------------------------------------------------------------------
-- 2. Kullanıcı Alerjen Tercihleri tablosu
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kullanici_alerjenleri (
    kullanici_id INT UNSIGNED NOT NULL,
    alerjen_id   TINYINT UNSIGNED NOT NULL,
    olusturma    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (kullanici_id, alerjen_id),
    KEY ix_ka_alerjen (alerjen_id),
    CONSTRAINT fk_ka_kullanici FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id) ON DELETE CASCADE,
    CONSTRAINT fk_ka_alerjen   FOREIGN KEY (alerjen_id)   REFERENCES alerjenler (id)   ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. sp_rezervasyon_yap saklı yordamının güncellenmesi
--    p_porsiyon: 'tam' veya 'yarim' (NULL ise 'tam' sayılır)
--    - Kahvaltıda (ogun_id = 1) yarım porsiyon seçilirse SIGNAL SQLSTATE '45000'
--    - Öğle (ogun_id = 2) ve Akşam (ogun_id = 3) için yarım porsiyon seçilirse
--      ücret tam fiyatın %60'ı (ROUND(tam_fiyat * 0.60, 2)) hesaplanır.
-- ---------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_rezervasyon_yap;
DELIMITER $$
CREATE PROCEDURE sp_rezervasyon_yap(
    IN p_kullanici_id INT UNSIGNED,
    IN p_menu_id      INT UNSIGNED,
    IN p_porsiyon     VARCHAR(10)
)
BEGIN
    DECLARE v_rol          VARCHAR(10)  DEFAULT NULL;
    DECLARE v_aktif        TINYINT      DEFAULT NULL;
    DECLARE v_bakiye       DECIMAL(10,2) DEFAULT NULL;
    DECLARE v_son          DATETIME     DEFAULT NULL;
    DECLARE v_kapasite     INT          DEFAULT NULL;
    DECLARE v_ogr_fiyat    DECIMAL(8,2) DEFAULT NULL;
    DECLARE v_per_fiyat    DECIMAL(8,2) DEFAULT NULL;
    DECLARE v_ucret        DECIMAL(8,2) DEFAULT NULL;
    DECLARE v_dolu         INT          DEFAULT 0;
    DECLARE v_mevcut_id    INT UNSIGNED DEFAULT NULL;
    DECLARE v_mevcut_durum VARCHAR(12)  DEFAULT NULL;
    DECLARE v_rez_id       INT UNSIGNED DEFAULT NULL;
    DECLARE v_ogun_id      TINYINT UNSIGNED DEFAULT NULL;
    DECLARE v_porsiyon     VARCHAR(10)  DEFAULT 'tam';

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

    START TRANSACTION;

    -- Porsiyon belirleme ve normalizasyon
    IF p_porsiyon IS NOT NULL AND LOWER(TRIM(p_porsiyon)) = 'yarim' THEN
        SET v_porsiyon = 'yarim';
    ELSE
        SET v_porsiyon = 'tam';
    END IF;

    -- Kullanıcı satırını kilitle (eşzamanlı bakiye işlemlerine karşı)
    SELECT rol, aktif, bakiye INTO v_rol, v_aktif, v_bakiye
      FROM kullanicilar WHERE id = p_kullanici_id FOR UPDATE;
    IF v_rol IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Kullanıcı bulunamadı.';
    END IF;
    IF v_aktif = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Hesabınız pasif durumda.';
    END IF;

    -- Menü satırını kilitle (eşzamanlı kapasite kontrolüne karşı)
    SELECT TIMESTAMP(m.tarih, o.son_saat), yh.kapasite, m.ogrenci_fiyati, m.personel_fiyati, m.ogun_id
      INTO v_son, v_kapasite, v_ogr_fiyat, v_per_fiyat, v_ogun_id
      FROM menuler m
      JOIN ogunler o       ON o.id  = m.ogun_id
      JOIN yemekhaneler yh ON yh.id = m.yemekhane_id
     WHERE m.id = p_menu_id
       FOR UPDATE;
    IF v_son IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Menü bulunamadı.';
    END IF;
    IF NOW() >= v_son THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bu menü için rezervasyon süresi doldu.';
    END IF;

    -- Kural: Kahvaltı öğününde (ogun_id = 1) yarım porsiyon seçilemez!
    IF v_ogun_id = 1 AND v_porsiyon = 'yarim' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Kahvaltı öğününde yarım porsiyon seçilemez.';
    END IF;

    -- Kullanıcının bu menü için mevcut rezervasyonunu kontrol et
    SELECT id, durum INTO v_mevcut_id, v_mevcut_durum
      FROM rezervasyonlar
     WHERE kullanici_id = p_kullanici_id AND menu_id = p_menu_id
       FOR UPDATE;
    IF v_mevcut_durum IN ('aktif', 'kullanildi') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bu menü için zaten rezervasyonunuz var.';
    END IF;

    -- Yemekhane kapasite kontrolü
    SELECT COUNT(*) INTO v_dolu
      FROM rezervasyonlar
     WHERE menu_id = p_menu_id AND durum IN ('aktif', 'kullanildi');
    IF v_dolu >= v_kapasite THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Yemekhane kapasitesi dolu.';
    END IF;

    -- Ücret hesaplama:
    -- 1. Rol bazlı tam fiyat:
    SET v_ucret = IF(v_rol = 'ogrenci', v_ogr_fiyat, v_per_fiyat);
    -- 2. Yarım porsiyon ise tam fiyatın %60'ı:
    IF v_porsiyon = 'yarim' THEN
        SET v_ucret = ROUND(v_ucret * 0.60, 2);
    END IF;

    IF v_bakiye < v_ucret THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bakiye yetersiz.';
    END IF;

    IF v_mevcut_id IS NULL THEN
        INSERT INTO rezervasyonlar (kullanici_id, menu_id, durum, ucret, porsiyon)
        VALUES (p_kullanici_id, p_menu_id, 'aktif', v_ucret, v_porsiyon);
        SET v_rez_id = LAST_INSERT_ID();
    ELSE
        -- Daha önce iptal edilmiş kayıt yeniden etkinleşir
        UPDATE rezervasyonlar
           SET durum = 'aktif', ucret = v_ucret, porsiyon = v_porsiyon, olusturma = NOW(),
               iptal_zamani = NULL, kullanma_zamani = NULL
         WHERE id = v_mevcut_id;
        SET v_rez_id = v_mevcut_id;
    END IF;

    UPDATE kullanicilar SET bakiye = bakiye - v_ucret WHERE id = p_kullanici_id;

    INSERT INTO bakiye_hareketleri (kullanici_id, tur, tutar, rezervasyon_id, aciklama)
    VALUES (
        p_kullanici_id, 
        'rezervasyon', 
        -v_ucret, 
        v_rez_id, 
        IF(v_porsiyon = 'yarim', 'Rezervasyon (Yarım Porsiyon)', 'Rezervasyon')
    );

    COMMIT;

    SELECT v_rez_id AS rezervasyon_id, v_ucret AS ucret, v_bakiye - v_ucret AS bakiye, v_porsiyon AS porsiyon;
END$$
DELIMITER ;
