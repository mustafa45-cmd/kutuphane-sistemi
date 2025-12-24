from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from src.decorators import jwt_required
from src.db import db
from src.models import Book, Author, Category


book_bp = Blueprint("books", __name__)


@book_bp.get("/")
def list_books():
    from src.models import Loan
    import jwt
    import os
    
    q = request.args.get("q", "").strip()
    query = Book.query.join(Author).join(Category)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Book.title.ilike(like), Author.name.ilike(like), Category.name.ilike(like))
        )
    
    # Kullanıcı giriş yapmışsa, ödünç aldığı kitapları filtrele
    user_id = None
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split()[1]
            # Token'ı decode et
            try:
                secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                user_id = payload.get("user_id") or int(payload.get("sub", 0))
            except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, ValueError):
                pass
    except Exception:
        pass
    
    books = query.all()
    result = []
    
    # Kullanıcının aktif ödünçlerini al (borrowed, requested veya approved)
    borrowed_book_ids = set()
    if user_id:
        active_loans = Loan.query.filter_by(user_id=user_id).filter(
            Loan.status.in_(["borrowed", "requested", "approved"])
        ).all()
        borrowed_book_ids = {loan.book_id for loan in active_loans}
    
    for b in books:
        # Kullanıcı bu kitabı ödünç aldıysa listeye ekleme
        if b.id in borrowed_book_ids:
            continue
            
        result.append(
            {
                "id": b.id,
                "title": b.title,
                "isbn": b.isbn,
                "author": b.author.name,
                "author_id": b.author_id,
                "category": b.category.name,
                "category_id": b.category_id,
                "total_copies": b.total_copies,
                "available_copies": b.available_copies,
            }
        )
    return jsonify(result)


@book_bp.post("/")
@jwt_required(role="admin")
def create_book():
    data = request.get_json() or {}
    required = ["title", "isbn", "author_id", "category_id", "total_copies"]
    if not all(field in data for field in required):
        return jsonify({"message": "Missing fields"}), 400

    book = Book(
        title=data["title"],
        isbn=data["isbn"],
        author_id=data["author_id"],
        category_id=data["category_id"],
        total_copies=data["total_copies"],
        available_copies=data.get("available_copies", data["total_copies"]),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({"id": book.id}), 201


@book_bp.put("/<int:book_id>")
@jwt_required(role="admin")
def update_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    data = request.get_json() or {}

    for field in ["title", "isbn", "author_id", "category_id", "total_copies", "available_copies"]:
        if field in data:
            setattr(book, field, data[field])

    db.session.commit()
    return jsonify({"message": "updated"})


@book_bp.delete("/<int:book_id>")
@jwt_required(role="admin")
def delete_book(book_id: int):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "deleted"})



