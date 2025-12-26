"""
Admin Yönetim Route'ları
Yazar, kategori ve kullanıcı yönetimi için CRUD işlemlerini içerir.
Sadece admin rolüne sahip kullanıcılar erişebilir.
"""

from flask import Blueprint, jsonify, request

from datetime import date

from src.decorators import jwt_required
from src.db import db
from src.models import Author, Category, User, Penalty, Loan
from src.security import hash_password


# Admin yönetimi blueprint'i
# URL prefix: /api/admin
admin_bp = Blueprint("admin", __name__)


# ========== YAZAR YÖNETİMİ ==========

@admin_bp.get("/authors")
@jwt_required(role="admin")
def list_authors():
    """
    Tüm yazarları listeler.
    
    Endpoint: GET /api/admin/authors
    
    Returns:
        200: Yazar listesi
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    authors = Author.query.all()
    return jsonify([{"id": a.id, "name": a.name, "bio": a.bio} for a in authors])


@admin_bp.post("/authors")
@jwt_required(role="admin")
def create_author():
    """
    Yeni yazar oluşturur.
    
    Endpoint: POST /api/admin/authors
    
    Request Body:
        {
            "name": "Yazar Adı",
            "bio": "Biyografi" (optional)
        }
    
    Returns:
        201: Yazar oluşturuldu (yazar ID'si)
        400: İsim eksik
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    data = request.get_json() or {}
    if "name" not in data:
        return jsonify({"message": "name is required"}), 400
    author = Author(name=data["name"], bio=data.get("bio"))
    db.session.add(author)
    db.session.commit()
    return jsonify({"id": author.id}), 201


@admin_bp.put("/authors/<int:author_id>")
@jwt_required(role="admin")
def update_author(author_id: int):
    """
    Yazar bilgilerini günceller.
    
    Endpoint: PUT /api/admin/authors/<author_id>
    
    Request Body (tüm alanlar optional):
        {
            "name": "Yeni Yazar Adı",
            "bio": "Yeni Biyografi"
        }
    
    Returns:
        200: Yazar güncellendi
        404: Yazar bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    author = Author.query.get_or_404(author_id)
    data = request.get_json() or {}
    if "name" in data:
        author.name = data["name"]
    if "bio" in data:
        author.bio = data["bio"]
    db.session.commit()
    return jsonify({"message": "updated"})


@admin_bp.delete("/authors/<int:author_id>")
@jwt_required(role="admin")
def delete_author(author_id: int):
    """
    Yazarı siler.
    
    Endpoint: DELETE /api/admin/authors/<author_id>
    
    Returns:
        200: Yazar silindi
        404: Yazar bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "deleted"})


# ========== KATEGORİ YÖNETİMİ ==========

@admin_bp.get("/categories")
@jwt_required(role="admin")
def list_categories():
    """
    Tüm kategorileri listeler.
    
    Endpoint: GET /api/admin/categories
    
    Returns:
        200: Kategori listesi
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    categories = Category.query.all()
    return jsonify(
        [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
    )


@admin_bp.post("/categories")
@jwt_required(role="admin")
def create_category():
    """
    Yeni kategori oluşturur.
    
    Endpoint: POST /api/admin/categories
    
    Request Body:
        {
            "name": "Kategori Adı",
            "description": "Açıklama" (optional)
        }
    
    Returns:
        201: Kategori oluşturuldu (kategori ID'si)
        400: İsim eksik
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    data = request.get_json() or {}
    if "name" not in data:
        return jsonify({"message": "name is required"}), 400
    category = Category(name=data["name"], description=data.get("description"))
    db.session.add(category)
    db.session.commit()
    return jsonify({"id": category.id}), 201


@admin_bp.put("/categories/<int:category_id>")
@jwt_required(role="admin")
def update_category(category_id: int):
    """
    Kategori bilgilerini günceller.
    
    Endpoint: PUT /api/admin/categories/<category_id>
    
    Request Body (tüm alanlar optional):
        {
            "name": "Yeni Kategori Adı",
            "description": "Yeni Açıklama"
        }
    
    Returns:
        200: Kategori güncellendi
        404: Kategori bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    category = Category.query.get_or_404(category_id)
    data = request.get_json() or {}
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    db.session.commit()
    return jsonify({"message": "updated"})


@admin_bp.delete("/categories/<int:category_id>")
@jwt_required(role="admin")
def delete_category(category_id: int):
    """
    Kategoriyi siler.
    
    Endpoint: DELETE /api/admin/categories/<category_id>
    
    Returns:
        200: Kategori silindi
        404: Kategori bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "deleted"})


# ========== KULLANICI YÖNETİMİ ==========

@admin_bp.post("/users")
@jwt_required(role="admin")
def create_user():
    """
    Yeni kullanıcı oluşturur (sadece admin).
    
    Endpoint: POST /api/admin/users
    
    Request Body:
        {
            "full_name": "Ad Soyad",
            "email": "email@example.com",
            "password": "şifre",
            "role": "student" | "staff" | "admin"
        }
    
    Returns:
        201: Kullanıcı oluşturuldu (kullanıcı ID'si)
        400: Eksik alanlar
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    data = request.get_json() or {}
    required = ["full_name", "email", "password", "role"]
    if not all(field in data for field in required):
        return jsonify({"message": "Missing fields"}), 400
    user = User(
        full_name=data["full_name"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
        role=data["role"],
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id}), 201


# ========== CEZA YÖNETİMİ ==========

@admin_bp.get("/penalties")
@jwt_required(role="admin")
def list_all_penalties():
    """
    Tüm cezaları listeler (sadece admin).
    
    Endpoint: GET /api/admin/penalties
    
    Returns:
        200: Tüm cezalar listesi (kullanıcı, kitap, tutar, durum bilgileri dahil)
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    penalties = (
        Penalty.query.join(Loan)
        .join(User)
        .order_by(Penalty.created_at.desc())
        .all()
    )
    result = []
    for p in penalties:
        days_remaining = (p.penalty_end_date - date.today()).days if p.penalty_end_date > date.today() else 0
        is_active = p.penalty_end_date > date.today()
        result.append(
            {
                "id": p.id,
                "user_id": p.user_id,
                "user_name": p.loan.user.full_name if p.loan and p.loan.user else None,
                "user_email": p.loan.user.email if p.loan and p.loan.user else None,
                "loan_id": p.loan_id,
                "book_title": p.loan.book.title if p.loan and p.loan.book else None,
                "days_late": p.days_late,
                "penalty_end_date": p.penalty_end_date.isoformat(),
                "days_remaining": days_remaining,
                "is_active": is_active,
                "created_at": p.created_at.isoformat(),
            }
        )
    return jsonify(result)


@admin_bp.post("/penalties/<int:penalty_id>/remove")
@jwt_required(role="admin")
def remove_penalty(penalty_id: int):
    """
    Cezayı kaldırır (sadece admin) - ceza bitiş tarihini bugüne çeker.
    
    Endpoint: POST /api/admin/penalties/<penalty_id>/remove
    
    Returns:
        200: Ceza kaldırıldı
        404: Ceza bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    penalty = Penalty.query.get_or_404(penalty_id)
    
    # Ceza bitiş tarihini bugüne çek (cezayı kaldır)
    penalty.penalty_end_date = date.today()
    db.session.commit()
    
    return jsonify({
        "message": "Ceza kaldırıldı",
        "penalty_id": penalty.id
    })





