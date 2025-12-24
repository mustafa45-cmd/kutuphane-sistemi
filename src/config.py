import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask

from src.db import init_db


load_dotenv()


def configure_app(app: Flask) -> None:
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_name = os.getenv("DB_NAME", "smart_library")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config["JWT_EXPIRES_DELTA"] = timedelta(hours=24)  # 24 saat geçerli

    try:
        init_db(app)
    except Exception as e:
        print(f"⚠️ Veritabanı bağlantı hatası: {e}")
        print(f"💡 Lütfen MySQL veritabanının çalıştığından ve '{db_name}' veritabanının kurulu olduğundan emin olun.")



