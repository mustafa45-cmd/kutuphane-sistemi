"""
Akıllı Kütüphane Yönetim Sistemi - Ana Uygulama Dosyası
Bu dosya Flask uygulamasının giriş noktasıdır.
"""

from flask import Flask
from flask_cors import CORS

from src.config import configure_app
from src.routes.auth_routes import auth_bp
from src.routes.book_routes import book_bp
from src.routes.loan_routes import loan_bp
from src.routes.admin_routes import admin_bp


def create_app() -> Flask:
    """
    Flask uygulamasını oluşturur ve yapılandırır.
    
    Returns:
        Flask: Yapılandırılmış Flask uygulama nesnesi
    """
    # Flask uygulamasını oluştur
    app = Flask(__name__)
    
    # Uygulama yapılandırmasını yükle (veritabanı, JWT, vb.)
    configure_app(app)
    
    # CORS (Cross-Origin Resource Sharing) ayarları
    # Tüm kaynaklardan /api/* endpoint'lerine erişime izin ver
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # API Blueprint'lerini kaydet
    # Her blueprint farklı bir modül için route'ları gruplar
    app.register_blueprint(auth_bp, url_prefix="/api/auth")      # Kimlik doğrulama endpoint'leri
    app.register_blueprint(book_bp, url_prefix="/api/books")     # Kitap yönetimi endpoint'leri
    app.register_blueprint(loan_bp, url_prefix="/api/loans")     # Ödünç alma endpoint'leri
    app.register_blueprint(admin_bp, url_prefix="/api/admin")    # Admin endpoint'leri

    # Sağlık kontrolü endpoint'i
    # Uygulamanın çalışıp çalışmadığını kontrol etmek için kullanılır
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    # Uygulama doğrudan çalıştırıldığında (python app.py)
    app = create_app()
    # Debug modunda çalıştır (geliştirme için)
    app.run(debug=True)





