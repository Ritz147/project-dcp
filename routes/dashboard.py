# File: dashboard_routes.py

from flask import Blueprint, jsonify
from models import db, User, DeviceInfo, DevicePolicy, DeviceStatus
from datetime import datetime, timedelta
from sqlalchemy import func


dashboard_route = Blueprint("dashboard_route", __name__)

@dashboard_route.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    try:
        # Total counts
        total_users = User.query.count()
        total_devices = DeviceInfo.query.count()
        total_policies = DevicePolicy.query.count()

        # Active devices (latest status within 1 minute)
        one_min_ago = datetime.utcnow() - timedelta(minutes=1)
        subquery = db.session.query(
            DeviceStatus.device_id,
            func.max(DeviceStatus.timestamp).label("latest")
        ).group_by(DeviceStatus.device_id).subquery()

        recent_statuses = db.session.query(DeviceStatus.device_id).join(
            subquery,
            (DeviceStatus.device_id == subquery.c.device_id) &
            (DeviceStatus.timestamp == subquery.c.latest)
        ).filter(DeviceStatus.timestamp >= one_min_ago).distinct().count()

        active_devices = recent_statuses

        # Simulated chart data (flat/zero values for now)
        chart_data = []
        today = datetime.utcnow().date()
        for i in range(7):
            date = today - timedelta(days=6 - i)
            chart_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "devices": 0  # Replace with real count later
            })

        return jsonify({
            "success": True,
            "data": {
                "total_users": total_users,
                "total_devices": total_devices,
                "total_policies": total_policies,
                "active_devices": active_devices,
                "trend": {
                    "users": None,
                    "devices": None,
                    "policies": None,
                    "active_devices": None
                },
                "active_device_chart": chart_data
            }
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
