"""
Uygulama Yapılandırma Modülü
Bu modül Flask uygulamasının tüm yapılandırma ayarlarını içerir.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from src.db import init_db


# .env dosyasından ortam değişkenlerini yükle
load_dotenv()


def configure_app(app: Flask) -> None:
    """
    Flask uygulamasını yapılandırır.
    
    Yapılandırma ayarları:
    - SECRET_KEY: JWT token'ları ve session'lar için gizli anahtar
    - Veritabanı bağlantı bilgileri
    - SQLAlchemy ayarları
    - JWT token ayarları
    
    Args:
        app: Yapılandırılacak Flask uygulama nesnesi
    """
    # JWT token'ları ve session'lar için gizli anahtar
    # Üretim ortamında mutlaka .env dosyasında tanımlanmalı
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Veritabanı bağlantı bilgileri (.env dosyasından veya varsayılan değerler)
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_name = os.getenv("DB_NAME", "smart_library")

    # SQLAlchemy veritabanı URI'si
    # Format: mysql+pymysql://kullanıcı:şifre@host/veritabanı_adı
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    
    # SQLAlchemy motor ayarları
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,      # Bağlantı kullanılmadan önce canlılık kontrolü yap
        "pool_recycle": 280,        # 280 saniye sonra bağlantıları yenile
    }
    
    # SQLAlchemy değişiklik takibini kapat (performans için)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # JWT token ayarları
    app.config["JWT_ALGORITHM"] = "HS256"                    # JWT imzalama algoritması
    app.config["JWT_EXPIRES_DELTA"] = timedelta(hours=24)    # Token geçerlilik süresi: 24 saat

    # Veritabanı bağlantısını başlat
    try:
        init_db(app)
    except Exception as e:
        # Veritabanı bağlantı hatası durumunda kullanıcıya bilgi ver
        print(f"⚠️ Veritabanı bağlantı hatası: {e}")
        print(f"💡 Lütfen MySQL veritabanının çalıştığından ve '{db_name}' veritabanının kurulu olduğundan emin olun.")



