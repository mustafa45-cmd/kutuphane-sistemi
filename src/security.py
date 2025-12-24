import datetime
import os
from typing import Any, Dict

import jwt
from flask import current_app
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return pbkdf2_sha256.verify(password, password_hash)
    except (ValueError, TypeError) as e:
        # Geçersiz hash formatı durumunda
        print(f"Password verification error: {e}")
        return False


def create_access_token(user_id: int, role: str) -> str:
    secret_key = current_app.config.get("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-change-me"))
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    expires_delta = current_app.config.get(
        "JWT_EXPIRES_DELTA", datetime.timedelta(hours=2)
    )
    now = datetime.datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": str(user_id),  # JWT standardına göre sub string olmalı
        "user_id": user_id,   # Integer user_id'yi de ekle (geriye dönük uyumluluk için)
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        # current_app context'i varsa kullan, yoksa env'den al
        try:
            secret_key = current_app.config.get("SECRET_KEY")
            algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
        except RuntimeError:
            # Context yoksa env'den al
            secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            algorithm = "HS256"
        
        if not secret_key:
            secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
        
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise
    except jwt.InvalidTokenError as e:
        raise



