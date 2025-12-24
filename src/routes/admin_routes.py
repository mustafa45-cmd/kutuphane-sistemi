from flask import Blueprint, jsonify, request

from src.decorators import jwt_required
from src.db import db
from src.models import Author, Category, User
from src.security import hash_password


admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/authors")
@jwt_required(role="admin")
def list_authors():
    authors = Author.query.all()
    return jsonify([{"id": a.id, "name": a.name, "bio": a.bio} for a in authors])


@admin_bp.post("/authors")
@jwt_required(role="admin")
def create_author():
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
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return jsonify({"message": "deleted"})


@admin_bp.get("/categories")
@jwt_required(role="admin")
def list_categories():
    categories = Category.query.all()
    return jsonify(
        [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
    )


@admin_bp.post("/categories")
@jwt_required(role="admin")
def create_category():
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
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "deleted"})


@admin_bp.post("/users")
@jwt_required(role="admin")
def create_user():
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



