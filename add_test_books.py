"""
Test Kitapları Ekleme Scripti

Bu script, sisteme test amaçlı kitaplar, yazarlar ve kategoriler ekler.
Toplam 10 kitap, 7 yazar ve 5 kategori oluşturulur.

Kullanım:
    python add_test_books.py

Not: Veritabanı ve test kullanıcıları kurulduktan sonra çalıştırın.
     Aynı ISBN'li kitaplar tekrar eklenmez (mevcut olanlar atlanır).
"""
import sys
from app import create_app
from src.db import db
from src.models import Author, Category, Book

def add_test_books():
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 50)
            print("Test Kitaplari Ekleniyor...")
            print("=" * 50)
            print()
            
            # Yazarları oluştur
            authors_data = [
                {"name": "Orhan Pamuk", "bio": "Nobel Edebiyat Ödülü sahibi Türk yazar"},
                {"name": "Elif Şafak", "bio": "Çok satan roman yazarı"},
                {"name": "Yaşar Kemal", "bio": "Türk edebiyatının usta yazarı"},
                {"name": "Ahmet Ümit", "bio": "Polisiye roman yazarı"},
                {"name": "Stephen King", "bio": "Korku ve gerilim yazarı"},
                {"name": "J.K. Rowling", "bio": "Harry Potter serisinin yazarı"},
                {"name": "George Orwell", "bio": "Distopya edebiyatı yazarı"},
            ]
            
            authors = {}
            print("Yazarlar olusturuluyor...")
            for author_data in authors_data:
                author = Author.query.filter_by(name=author_data["name"]).first()
                if not author:
                    author = Author(name=author_data["name"], bio=author_data["bio"])
                    db.session.add(author)
                    db.session.flush()  # ID'yi almak için
                    print(f"  [OK] {author_data['name']}")
                else:
                    print(f"  [INFO] {author_data['name']} zaten var")
                authors[author_data["name"]] = author
            
            # Kategorileri oluştur
            categories_data = [
                {"name": "Roman", "description": "Kurgu romanlar"},
                {"name": "Polisiye", "description": "Suç ve gerilim romanları"},
                {"name": "Bilim Kurgu", "description": "Bilim kurgu eserleri"},
                {"name": "Fantastik", "description": "Fantastik edebiyat"},
                {"name": "Klasik", "description": "Klasik edebiyat eserleri"},
            ]
            
            categories = {}
            print("\nKategoriler olusturuluyor...")
            for cat_data in categories_data:
                category = Category.query.filter_by(name=cat_data["name"]).first()
                if not category:
                    category = Category(name=cat_data["name"], description=cat_data["description"])
                    db.session.add(category)
                    db.session.flush()  # ID'yi almak için
                    print(f"  [OK] {cat_data['name']}")
                else:
                    print(f"  [INFO] {cat_data['name']} zaten var")
                categories[cat_data["name"]] = category
            
            db.session.commit()
            print("\nYazarlar ve kategoriler hazir!")
            
            # Kitapları oluştur
            books_data = [
                {
                    "title": "Kırmızı Saçlı Kadın",
                    "isbn": "978-975-08-1234-5",
                    "author": "Orhan Pamuk",
                    "category": "Roman",
                    "total_copies": 3,
                },
                {
                    "title": "Aşk",
                    "isbn": "978-975-08-2345-6",
                    "author": "Elif Şafak",
                    "category": "Roman",
                    "total_copies": 5,
                },
                {
                    "title": "İnce Memed",
                    "isbn": "978-975-08-3456-7",
                    "author": "Yaşar Kemal",
                    "category": "Klasik",
                    "total_copies": 4,
                },
                {
                    "title": "İstanbul Hatırası",
                    "isbn": "978-975-08-4567-8",
                    "author": "Ahmet Ümit",
                    "category": "Polisiye",
                    "total_copies": 6,
                },
                {
                    "title": "The Shining",
                    "isbn": "978-0-385-12167-5",
                    "author": "Stephen King",
                    "category": "Polisiye",
                    "total_copies": 3,
                },
                {
                    "title": "Harry Potter ve Felsefe Taşı",
                    "isbn": "978-975-08-5678-9",
                    "author": "J.K. Rowling",
                    "category": "Fantastik",
                    "total_copies": 8,
                },
                {
                    "title": "1984",
                    "isbn": "978-975-08-6789-0",
                    "author": "George Orwell",
                    "category": "Bilim Kurgu",
                    "total_copies": 5,
                },
                {
                    "title": "Beyaz Kale",
                    "isbn": "978-975-08-7890-1",
                    "author": "Orhan Pamuk",
                    "category": "Roman",
                    "total_copies": 4,
                },
                {
                    "title": "Baba ve Piç",
                    "isbn": "978-975-08-8901-2",
                    "author": "Elif Şafak",
                    "category": "Roman",
                    "total_copies": 3,
                },
                {
                    "title": "Yer Demir Gök Bakır",
                    "isbn": "978-975-08-9012-3",
                    "author": "Yaşar Kemal",
                    "category": "Klasik",
                    "total_copies": 2,
                },
            ]
            
            print("\nKitaplar ekleniyor...")
            added_count = 0
            for book_data in books_data:
                # Aynı ISBN'li kitap var mı kontrol et
                existing = Book.query.filter_by(isbn=book_data["isbn"]).first()
                if existing:
                    print(f"  [INFO] '{book_data['title']}' zaten var (ISBN: {book_data['isbn']})")
                    continue
                
                author = authors.get(book_data["author"])
                category = categories.get(book_data["category"])
                
                if not author or not category:
                    print(f"  [ERROR] '{book_data['title']}' eklenemedi: Yazar veya kategori bulunamadı")
                    continue
                
                book = Book(
                    title=book_data["title"],
                    isbn=book_data["isbn"],
                    author_id=author.id,
                    category_id=category.id,
                    total_copies=book_data["total_copies"],
                    available_copies=book_data["total_copies"],  # Başlangıçta hepsi müsait
                )
                db.session.add(book)
                added_count += 1
                print(f"  [OK] {book_data['title']} - {book_data['author']} ({book_data['category']})")
            
            db.session.commit()
            
            print()
            print("=" * 50)
            print(f"[SUCCESS] {added_count} yeni kitap eklendi!")
            print("=" * 50)
            print()
            print("Toplam kitap sayisi:", Book.query.count())
            print("Toplam yazar sayisi:", Author.query.count())
            print("Toplam kategori sayisi:", Category.query.count())
            
        except Exception as e:
            print(f"\n[ERROR] Hata: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    add_test_books()



