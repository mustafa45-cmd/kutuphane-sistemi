"""
Kimlik Doğrulama Route'ları
Kullanıcı kayıt ve giriş işlemlerini yönetir.
"""

from flask import Blueprint, jsonify, request

from src.db import db
from src.models import User
from src.security import hash_password, verify_password, create_access_token


# Kimlik doğrulama blueprint'i
# URL prefix: /api/auth
auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    """
    Yeni kullanıcı kaydı oluşturur.
    
    Endpoint: POST /api/auth/register
    
    Request Body:
        {
            "full_name": "Ad Soyad",
            "email": "email@example.com",
            "password": "şifre"
        }
    
    Returns:
        201: Kayıt başarılı (kullanıcı bilgileri)
        400: Eksik veya geçersiz veri
        409: E-posta zaten kayıtlı
        500: Sunucu hatası
    """
    try:
        data = request.get_json() or {}
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not full_name or not email or not password:
            return jsonify({"message": "Ad soyad, e-posta ve şifre gereklidir"}), 400

        if len(password) < 6:
            return jsonify({"message": "Şifre en az 6 karakter olmalıdır"}), 400

        if "@" not in email or "." not in email:
            return jsonify({"message": "Geçerli bir e-posta adresi giriniz"}), 400

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"message": "Bu e-posta adresi zaten kayıtlı"}), 409

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role="student",
        )
        db.session.add(user)
        db.session.commit()
        return jsonify(
            {"id": user.id, "full_name": user.full_name, "email": user.email, "role": user.role}
        ), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"message": f"Kayıt sırasında hata oluştu: {str(e)}"}), 500


@auth_bp.post("/login")
def login():
    """
    Kullanıcı girişi yapar ve JWT token döndürür.
    
    Endpoint: POST /api/auth/login
    
    Request Body:
        {
            "email": "email@example.com",
            "password": "şifre"
        }
    
    Returns:
        200: Giriş başarılı (token ve kullanıcı bilgileri)
        400: E-posta veya şifre eksik
        401: Geçersiz e-posta veya şifre
        500: Sunucu hatası
    """
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "email and password are required"}), 400

        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"message": "Geçersiz e-posta veya şifre"}), 401

        token = create_access_token(user.id, user.role)
        return jsonify(
            {
                "access_token": token,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role,
                },
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"message": f"Sunucu hatası: {str(e)}"}), 500



