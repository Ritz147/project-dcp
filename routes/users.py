from flask import Blueprint, request, jsonify, current_app
from models import db, User, DashboardAccess, DashboardPartEnum, UserRoleEnum
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps
import jwt

user_route = Blueprint('user_route', __name__)

def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"error": "Token missing"}), 401

        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            user = User.query.get(data["user_id"])
            if not user or user.role != UserRoleEnum.SUPERADMIN:
                return jsonify({"error": "Forbidden"}), 403
        except Exception as e:
            return jsonify({"error": "Invalid token", "details": str(e)}), 401

        return f(user, *args, **kwargs)
    return decorated


class UserApi:
    @staticmethod
    @user_route.route('/get-all-users', methods=['GET'])
    def get_all_users():
        try:
            users = User.query.all()
            result = [
                {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ]
            return jsonify({"success": True, "users": result}), 200
        except SQLAlchemyError as e:
            return jsonify({"error": "Database error", "details": str(e)}), 500

    @staticmethod
    @user_route.route('/get-user-details/<user_id>', methods=['GET'])
    def get_user_details(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            permissions = [
                access.dashboard_part.value
                for access in user.access_permissions
            ]

            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "created_at": user.created_at.isoformat(),
                    "access_permissions": permissions
                }
            }), 200
        except SQLAlchemyError as e:
            return jsonify({"error": "Database error", "details": str(e)}), 500

    @staticmethod
    @user_route.route('/edit-user-access/<user_id>', methods=['PUT'])
    @superadmin_required
    def edit_user_access(current_user, user_id):
        try:
            data = request.get_json()
            new_access = data.get("access_permissions")

            if not isinstance(new_access, list):
                return jsonify({"error": "access_permissions must be a list"}), 400

            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            # Clear old access
            DashboardAccess.query.filter_by(user_id=user_id).delete()

            # Add new access
            for part in new_access:
                try:
                    part_enum = DashboardPartEnum[part]
                    db.session.add(DashboardAccess(user_id=user_id, dashboard_part=part_enum))
                except KeyError:
                    return jsonify({"error": f"Invalid dashboard part: {part}"}), 400

            db.session.commit()
            return jsonify({"success": True, "message": "Permissions updated"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "details": str(e)}), 500
