from app import create_app  # Make sure to import your Flask app
from models import db, User, DashboardAccess, DashboardPartEnum, UserRoleEnum
import uuid
app=create_app()
with app.app_context():
    users = User.query.all()
    count = 0

    for user in users:
        existing_permissions = {access.dashboard_part for access in user.access_permissions}
        
        if user.role == UserRoleEnum.ADMIN:
            required_permissions = {
                DashboardPartEnum.DASHBOARD,
                DashboardPartEnum.DEVICES,
                DashboardPartEnum.POLICIES,
            }
        elif user.role == UserRoleEnum.SUPERADMIN:
            required_permissions = {
                DashboardPartEnum.DASHBOARD,
                DashboardPartEnum.USERS,
                DashboardPartEnum.DEVICES,
                DashboardPartEnum.POLICIES,
            }
        else:
            continue  # Unknown role

        # Add missing permissions
        for part in required_permissions - existing_permissions:
            db.session.add(DashboardAccess(
                id=str(uuid.uuid4()),
                user_id=user.id,
                dashboard_part=part
            ))
            count += 1

    db.session.commit()
    print(f"✅ Done. Added {count} missing access permissions.")
