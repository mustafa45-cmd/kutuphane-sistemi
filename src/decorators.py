from functools import wraps
from typing import Callable, Any
import os

from flask import request, jsonify, g, current_app
from jwt import InvalidTokenError, ExpiredSignatureError, decode as jwt_decode

from src.security import decode_access_token


def jwt_required(role: str | None = None) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            auth_header = request.headers.get("Authorization", "")
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                return jsonify({"message": "Missing or invalid Authorization header"}), 401

            token = parts[1]
            
            # Secret key'i al
            try:
                secret_key = current_app.config.get("SECRET_KEY")
            except RuntimeError:
                secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            
            if not secret_key:
                secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")
            
            try:
                # Direkt jwt.decode kullan (daha güvenilir)
                payload = jwt_decode(token, secret_key, algorithms=["HS256"])
            except ExpiredSignatureError:
                return jsonify({"message": "Token expired"}), 401
            except InvalidTokenError as e:
                return jsonify({"message": f"Invalid token: {str(e)}"}), 401
            except Exception as e:
                return jsonify({"message": f"Token decode error: {str(e)}"}), 401

            if role is not None and payload.get("role") != role:
                return jsonify({"message": "Insufficient permissions"}), 403

            # sub string olabilir, user_id integer olarak da saklanabilir
            user_id = payload.get("user_id") or int(payload.get("sub", 0))
            g.current_user_id = user_id
            g.current_user_role = payload.get("role")
            return fn(*args, **kwargs)

        return wrapper

    return decorator



