from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token
from models import db, User
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import jwt  # PyJWT

login_route = Blueprint('login_route', __name__)

class LoginApi:
    @staticmethod
    @login_route.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return jsonify({"error": "Username and password are required"}), 400

            user = User.query.filter_by(username=username).first()

            if not user or not user.check_password(password):
                return jsonify({"error": "Invalid credentials"}), 401

            # Payload for manual JWT
            payload = {
                "user_id": user.id,
                "username": user.username,
                "role": user.role.value,
                "exp": datetime.utcnow() + timedelta(hours=12)
            }

            # Generate JWT manually (for frontend/local decoding)
            token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

            # Also create access token using flask_jwt_extended (optional, backend-protected routes)
            flask_jwt_token = create_access_token(identity=user.id)

            return jsonify({
                "success": True,
                "token": token,  # frontend use
                "access_token": flask_jwt_token,  # optional: backend use
                "role": user.role.value
            }), 200

        except SQLAlchemyError as e:
            return jsonify({"error": "Database error", "details": str(e)}), 500
        except Exception as e:
            return jsonify({"error": "Server error", "details":  str(e)}), 500
