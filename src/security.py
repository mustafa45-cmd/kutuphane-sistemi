"""
Güvenlik Modülü
Şifre hash'leme ve JWT token oluşturma/doğrulama işlemlerini içerir.
"""

import datetime
import os
from typing import Any, Dict

import jwt
from flask import current_app
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    """
    Şifreyi pbkdf2_sha256 algoritması ile hash'ler.
    
    Args:
        password: Hash'lenecek şifre (düz metin)
    
    Returns:
        str: Hash'lenmiş şifre
    """
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verilen şifrenin hash ile eşleşip eşleşmediğini kontrol eder.
    
    Args:
        password: Kontrol edilecek şifre (düz metin)
        password_hash: Veritabanından gelen hash'lenmiş şifre
    
    Returns:
        bool: Şifre doğruysa True, yanlışsa False
    """
    try:
        return pbkdf2_sha256.verify(password, password_hash)
    except (ValueError, TypeError) as e:
        # Geçersiz hash formatı durumunda (örn: eski veritabanı kayıtları)
        print(f"Password verification error: {e}")
        return False


def create_access_token(user_id: int, role: str) -> str:
    """
    JWT (JSON Web Token) erişim token'ı oluşturur.
    
    Token içeriği:
    - sub: Kullanıcı ID (string formatında, JWT standardına uygun)
    - user_id: Kullanıcı ID (integer formatında, geriye dönük uyumluluk için)
    - role: Kullanıcı rolü (student, staff, admin)
    - iat: Token oluşturulma zamanı
    - exp: Token sona erme zamanı
    
    Args:
        user_id: Token'ın oluşturulacağı kullanıcının ID'si
        role: Kullanıcının rolü
    
    Returns:
        str: JWT token (string formatında)
    """
    # Gizli anahtarı ve algoritmayı yapılandırmadan al
    secret_key = current_app.config.get("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-change-me"))
    algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
    expires_delta = current_app.config.get(
        "JWT_EXPIRES_DELTA", datetime.timedelta(hours=2)
    )
    
    # Token payload'ını oluştur
    now = datetime.datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": str(user_id),      # JWT standardına göre sub string olmalı
        "user_id": user_id,       # Integer user_id'yi de ekle (geriye dönük uyumluluk için)
        "role": role,             # Kullanıcı rolü
        "iat": now,               # Issued at (oluşturulma zamanı)
        "exp": now + expires_delta,  # Expiration (sona erme zamanı)
    }
    
    # Token'ı oluştur ve döndür
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    JWT token'ı decode eder ve içeriğini döndürür.
    
    Args:
        token: Decode edilecek JWT token
    
    Returns:
        Dict[str, Any]: Token içeriği (payload)
    
    Raises:
        jwt.ExpiredSignatureError: Token süresi dolmuşsa
        jwt.InvalidTokenError: Token geçersizse
    """
    try:
        # current_app context'i varsa kullan, yoksa env'den al
        try:
            secret_key = current_app.config.get("SECRET_KEY")
            algorithm = current_app.config.get("JWT_ALGORITHM", "HS256")
        except RuntimeError:
            # Context yoksa env'den al (örn: test ortamında)
            secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            algorithm = "HS256"
        
        if not secret_key:
            secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
        
        # Token'ı decode et
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        # Token süresi dolmuş
        raise
    except jwt.InvalidTokenError as e:
        # Token geçersiz (imza hatası, format hatası, vb.)
        raise



