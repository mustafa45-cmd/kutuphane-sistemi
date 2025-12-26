"""
Decorator Modülü
API endpoint'lerini korumak için JWT tabanlı authentication decorator'ları içerir.
"""

from functools import wraps
from typing import Callable, Any
import os

from flask import request, jsonify, g, current_app
from jwt import InvalidTokenError, ExpiredSignatureError, decode as jwt_decode

from src.security import decode_access_token


def jwt_required(role: str | None = None) -> Callable:
    """
    JWT token doğrulaması yapan decorator.
    
    Bu decorator ile işaretlenen endpoint'ler:
    - Authorization header'ında geçerli bir Bearer token gerektirir
    - Token'ı decode eder ve kullanıcı bilgilerini Flask g nesnesine ekler
    - İsteğe bağlı olarak belirli bir rol kontrolü yapar
    
    Kullanım:
        @jwt_required()  # Sadece giriş yapmış kullanıcılar erişebilir
        @jwt_required(role="admin")  # Sadece admin rolü erişebilir
    
    Args:
        role: İsteğe bağlı rol kontrolü. None ise sadece giriş yapmış olmak yeterli.
    
    Returns:
        Callable: Decorator fonksiyonu
    
    Örnek:
        @book_bp.get("/")
        @jwt_required()
        def list_books():
            # g.current_user_id ve g.current_user_role kullanılabilir
            pass
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            # Authorization header'ını kontrol et
            auth_header = request.headers.get("Authorization", "")
            parts = auth_header.split()
            
            # Format: "Bearer <token>"
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"message": "Missing or invalid Authorization header"}), 401

            token = parts[1]
            
            # Secret key'i al (current_app context'i varsa oradan, yoksa env'den)
            try:
                secret_key = current_app.config.get("SECRET_KEY")
            except RuntimeError:
                secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            
            if not secret_key:
                secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            
            try:
                # Token'ı decode et
                # Direkt jwt.decode kullan (daha güvenilir)
                payload = jwt_decode(token, secret_key, algorithms=["HS256"])
            except ExpiredSignatureError:
                # Token süresi dolmuş
                return jsonify({"message": "Token expired"}), 401
            except InvalidTokenError as e:
                # Token geçersiz
                return jsonify({"message": f"Invalid token: {str(e)}"}), 401
            except Exception as e:
                # Diğer hatalar
                return jsonify({"message": f"Token decode error: {str(e)}"}), 401

            # Rol kontrolü (eğer belirtilmişse)
            if role is not None and payload.get("role") != role:
                return jsonify({"message": "Insufficient permissions"}), 403

            # Kullanıcı bilgilerini Flask g nesnesine ekle
            # sub string olabilir, user_id integer olarak da saklanabilir
            user_id = payload.get("user_id") or int(payload.get("sub", 0))
            g.current_user_id = user_id              # Mevcut kullanıcının ID'si
            g.current_user_role = payload.get("role")  # Mevcut kullanıcının rolü
            
            # Orijinal fonksiyonu çalıştır
            return fn(*args, **kwargs)

        return wrapper

    return decorator



