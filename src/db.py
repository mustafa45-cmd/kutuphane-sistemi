"""
Veritabanı Modülü
SQLAlchemy veritabanı nesnesini ve başlatma fonksiyonunu içerir.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# SQLAlchemy veritabanı nesnesi
# Tüm modeller bu nesneyi kullanarak tanımlanır
db = SQLAlchemy()


def init_db(app: Flask) -> None:
    """
    SQLAlchemy veritabanı nesnesini Flask uygulamasına bağlar.
    
    Args:
        app: Flask uygulama nesnesi
    """
    db.init_app(app)





