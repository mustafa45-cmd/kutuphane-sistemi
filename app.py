from flask import Flask
from flask_cors import CORS

from src.config import configure_app
from src.routes.auth_routes import auth_bp
from src.routes.book_routes import book_bp
from src.routes.loan_routes import loan_bp
from src.routes.admin_routes import admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    configure_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(book_bp, url_prefix="/api/books")
    app.register_blueprint(loan_bp, url_prefix="/api/loans")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)



