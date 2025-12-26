"""
Ödünç Alma Yönetimi Route'ları
Kitap ödünç alma, iade, istek onaylama/reddetme işlemlerini yönetir.
"""

from datetime import date, timedelta

from flask import Blueprint, jsonify, request, g
from sqlalchemy import text

from src.decorators import jwt_required
from src.db import db
from src.models import Loan, Book, Penalty


# Ödünç alma yönetimi blueprint'i
# URL prefix: /api/loans
loan_bp = Blueprint("loans", __name__)


@loan_bp.post("/")
@jwt_required()
def request_loan():
    """
    Ödünç alma isteği gönderir veya direkt ödünç alır.
    
    Endpoint: POST /api/loans
    
    İşleyiş:
        - Admin: Direkt ödünç alır (status="borrowed", kitap sayısı azalır)
        - Öğrenci/Staff: İstek gönderir (status="requested", kitap sayısı azalmaz)
    
    Request Body:
        {
            "book_id": 1,
            "days": 14 (optional, varsayılan: 14)
        }
    
    Returns:
        201: İstek oluşturuldu veya kitap ödünç verildi
        400: Geçersiz istek (kitap müsait değil, zaten istek var, vb.)
        401: Yetkisiz erişim
        500: Sunucu hatası
    """
    try:
        data = request.get_json() or {}
        book_id = data.get("book_id")
        days = int(data.get("days", 14))

        if not book_id:
            return jsonify({"message": "book_id is required"}), 400

        book = Book.query.get_or_404(book_id)
        if book.available_copies <= 0:
            return jsonify({"message": "Bu kitaptan müsait kopya yok"}), 400

        # Admin direkt ödünç alabilir
        if g.current_user_role == "admin":
            loan = Loan(
                user_id=g.current_user_id,
                book_id=book_id,
                loan_date=date.today(),
                due_date=date.today() + timedelta(days=days),
                status="borrowed",
            )
            book.available_copies -= 1
            db.session.add(loan)
            db.session.commit()
            return jsonify({
                "id": loan.id,
                "message": "Kitap ödünç verildi"
            }), 201
        
        # Öğrenci/staff istek gönderir
        # Bekleyen bir istek var mı kontrol et
        existing = Loan.query.filter_by(
            user_id=g.current_user_id,
            book_id=book_id,
            status="requested"
        ).first()
        
        if existing:
            return jsonify({"message": "Bu kitap için zaten bekleyen bir isteğiniz var"}), 400

        # İstek oluştur (henüz onaylanmadı, kitap sayısı azaltılmaz)
        loan = Loan(
            user_id=g.current_user_id,
            book_id=book_id,
            loan_date=date.today(),  # İstek tarihi
            due_date=date.today() + timedelta(days=days),  # Tahmini iade tarihi
            status="requested",  # İstek durumu
        )
        db.session.add(loan)
        db.session.commit()
        return jsonify({
            "id": loan.id,
            "message": "Ödünç alma isteği gönderildi. Admin onayı bekleniyor."
        }), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"message": f"Sunucu hatası: {str(e)}"}), 500


@loan_bp.post("/<int:loan_id>/return")
@jwt_required()
def return_book(loan_id: int):
    """
    Kitabı iade eder.
    
    Endpoint: POST /api/loans/<loan_id>/return
    
    İşleyiş:
        - İade tarihi kaydedilir
        - Gecikmiş ise status="late", değilse status="returned"
        - Kitap mevcut kopya sayısı artırılır
        - Gecikme varsa otomatik ceza oluşturulur (trigger ile)
    
    Returns:
        200: Kitap iade edildi
        400: Kitap zaten iade edilmiş
        403: Bu işlem için yetkiniz yok
        404: Ödünç kaydı bulunamadı
    """
    loan = Loan.query.get_or_404(loan_id)
    if loan.user_id != g.current_user_id and g.current_user_role != "admin":
        return jsonify({"message": "Not allowed"}), 403

    if loan.return_date is not None:
        return jsonify({"message": "Already returned"}), 400

    # Stored procedure alternatifi: CALL sp_return_book(:loan_id)
    loan.return_date = date.today()
    if loan.return_date > loan.due_date:
        loan.status = "late"
    else:
        loan.status = "returned"

    book = Book.query.get(loan.book_id)
    if book:
        book.available_copies += 1

    db.session.commit()
    return jsonify({"message": "returned"})


@loan_bp.get("/my")
@jwt_required()
def my_loans():
    """
    Kullanıcının kendi ödünç istekleri ve ödünçlerini listeler.
    
    Endpoint: GET /api/loans/my
    
    Returns:
        200: Ödünç listesi (durum, tarihler, ceza bilgileri dahil)
        401: Yetkisiz erişim
    """
    loans = (
        Loan.query.filter_by(user_id=g.current_user_id)
        .order_by(Loan.created_at.desc())
        .all()
    )
    result = []
    for l in loans:
        penalty = None
        if l.penalty:
            penalty = {
                "amount": float(l.penalty.amount),
                "days_late": l.penalty.days_late,
                "is_paid": l.penalty.is_paid,
            }
        result.append(
            {
                "id": l.id,
                "book_id": l.book_id,
                "book_title": l.book.title if l.book else None,
                "loan_date": l.loan_date.isoformat(),
                "due_date": l.due_date.isoformat(),
                "return_date": l.return_date.isoformat() if l.return_date else None,
                "status": l.status,
                "penalty": penalty,
            }
        )
    return jsonify(result)


@loan_bp.get("/requests")
@jwt_required(role="admin")
def list_requests():
    """
    Tüm bekleyen ödünç isteklerini listeler (sadece admin).
    
    Endpoint: GET /api/loans/requests
    
    Returns:
        200: Bekleyen istek listesi (kullanıcı, kitap, tarih bilgileri dahil)
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    requests = (
        Loan.query.filter_by(status="requested")
        .order_by(Loan.created_at.asc())
        .all()
    )
    result = []
    for req in requests:
        result.append(
            {
                "id": req.id,
                "user_id": req.user_id,
                "user_name": req.user.full_name if req.user else None,
                "user_email": req.user.email if req.user else None,
                "book_id": req.book_id,
                "book_title": req.book.title if req.book else None,
                "book_available": req.book.available_copies if req.book else 0,
                "request_date": req.loan_date.isoformat(),
                "due_date": req.due_date.isoformat(),
                "created_at": req.created_at.isoformat(),
            }
        )
    return jsonify(result)


@loan_bp.post("/<int:loan_id>/approve")
@jwt_required(role="admin")
def approve_loan(loan_id: int):
    """
    Ödünç alma isteğini onaylar (sadece admin).
    
    Endpoint: POST /api/loans/<loan_id>/approve
    
    İşleyiş:
        - İstek durumu "requested" -> "borrowed" olur
        - Kitap mevcut kopya sayısı 1 azalır
        - Ödünç alma tarihi güncellenir
    
    Returns:
        200: İstek onaylandı
        400: İstek zaten onaylanmış veya reddedilmiş
        404: İstek veya kitap bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != "requested":
        return jsonify({"message": "Sadece bekleyen istekler onaylanabilir"}), 400
    
    book = Book.query.get(loan.book_id)
    if not book:
        return jsonify({"message": "Kitap bulunamadı"}), 404
    
    if book.available_copies <= 0:
        return jsonify({"message": "Bu kitaptan müsait kopya kalmamış"}), 400
    
    # İsteği onayla: kitabı azalt ve durumu güncelle
    book.available_copies -= 1
    loan.status = "borrowed"
    loan.loan_date = date.today()  # Onaylandığı tarih
    
    db.session.commit()
    return jsonify({
        "message": "Ödünç alma isteği onaylandı",
        "loan_id": loan.id
    })


@loan_bp.post("/<int:loan_id>/reject")
@jwt_required(role="admin")
def reject_loan(loan_id: int):
    """
    Ödünç alma isteğini reddeder (sadece admin).
    
    Endpoint: POST /api/loans/<loan_id>/reject
    
    İşleyiş:
        - İstek durumu "requested" -> "rejected" olur
        - Kitap sayısı değişmez (çünkü henüz ödünç verilmemişti)
    
    Returns:
        200: İstek reddedildi
        400: İstek zaten onaylanmış veya reddedilmiş
        404: İstek bulunamadı
        401: Yetkisiz erişim
        403: Admin yetkisi gerekli
    """
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != "requested":
        return jsonify({"message": "Sadece bekleyen istekler reddedilebilir"}), 400
    
    loan.status = "rejected"
    db.session.commit()
    return jsonify({
        "message": "Ödünç alma isteği reddedildi",
        "loan_id": loan.id
    })


@loan_bp.get("/penalties")
@jwt_required()
def my_penalties():
    """
    Kullanıcının cezalarını listeler.
    
    Endpoint: GET /api/loans/penalties
    
    Returns:
        200: Ceza listesi (tutar, gecikme günü, ödeme durumu dahil)
        401: Yetkisiz erişim
    """
    penalties = (
        Penalty.query.join(Loan)
        .filter(Penalty.user_id == g.current_user_id)
        .order_by(Penalty.created_at.desc())
        .all()
    )
    result = []
    for p in penalties:
        result.append(
            {
                "id": p.id,
                "loan_id": p.loan_id,
                "book_title": p.loan.book.title if p.loan and p.loan.book else None,
                "amount": float(p.amount),
                "days_late": p.days_late,
                "is_paid": p.is_paid,
                "created_at": p.created_at.isoformat(),
            }
        )
    return jsonify(result)



