"""
Test Kullanıcısı Oluşturma Scripti

Bu script, sistemi test etmek için varsayılan kullanıcılar oluşturur:
- Admin kullanıcı: admin@example.com / admin123
- Öğrenci kullanıcı: student@example.com / student123

Kullanım:
    python create_test_user.py

Not: Veritabanı kurulduktan sonra bu scripti çalıştırın.
     Eğer kullanıcılar zaten varsa, şifreleri güncellenir.
"""
import sys
from app import create_app
from src.db import db
from src.models import User
from src.security import hash_password

def create_test_users():
    app = create_app()
    
    with app.app_context():
        try:
            # Admin kullanıcısı
            admin_email = "admin@example.com"
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(
                    full_name="Admin User",
                    email=admin_email,
                    password_hash=hash_password("admin123"),
                    role="admin"
                )
                db.session.add(admin)
                print(f"[OK] Admin kullanicisi olusturuldu: {admin_email} / admin123")
            else:
                # Mevcut kullanıcının şifresini güncelle
                admin.password_hash = hash_password("admin123")
                admin.role = "admin"
                admin.is_active = True
                print(f"[OK] Admin kullanicisi sifresi guncellendi: {admin_email} / admin123")
            
            # Öğrenci kullanıcısı
            student_email = "student@example.com"
            student = User.query.filter_by(email=student_email).first()
            if not student:
                student = User(
                    full_name="Test Student",
                    email=student_email,
                    password_hash=hash_password("student123"),
                    role="student"
                )
                db.session.add(student)
                print(f"[OK] Ogrenci kullanicisi olusturuldu: {student_email} / student123")
            else:
                # Mevcut kullanıcının şifresini güncelle
                student.password_hash = hash_password("student123")
                student.role = "student"
                student.is_active = True
                print(f"[OK] Ogrenci kullanicisi sifresi guncellendi: {student_email} / student123")
            
            db.session.commit()
            print("\n[SUCCESS] Test kullanicilari hazir!")
            print("\nGiris bilgileri:")
            print(f"  Admin: {admin_email} / admin123")
            print(f"  Ogrenci: {student_email} / student123")
            
        except Exception as e:
            print(f"[ERROR] Hata: {e}")
            print("\n[INFO] Lutfen once MySQL veritabanini kurun:")
            print("   1. db_schema.sql dosyasini MySQL'de calistirin")
            print("   2. .env dosyasindaki DB_PASSWORD degerini kontrol edin")
            sys.exit(1)

if __name__ == "__main__":
    create_test_users()

