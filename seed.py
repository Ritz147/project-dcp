from models import db, DevicePolicy, User, UserRoleEnum
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pytz
import uuid
from app import create_app

# Convert UTC to IST
def to_ist(dt):
    ist = pytz.timezone("Asia/Kolkata")
    dt = pytz.utc.localize(dt)
    return dt.astimezone(ist)

# Policy names
POLICY_NAMES = [
    "cameraDisabled", "usbFileTransferDisabled", "safeBootDisabled",
    "installAppsDisabled", "uninstallAppsDisabled", "bluetoothDisabled",
    "wifiDisabled", "tetheringDisabled", "cellularDataDisabled", "keyguardDisabled"
]

# Seed Device Policies
def seed_device_policies():
    for policy_name in POLICY_NAMES:
        if not DevicePolicy.query.filter_by(policy_name=policy_name).first():
            policy = DevicePolicy(
                id=str(uuid.uuid4()),
                policy_name=policy_name,
                enabled=True,
                created_at=to_ist(datetime.utcnow()),
                updated_at=to_ist(datetime.utcnow())
            )
            db.session.add(policy)
    try:
        db.session.commit()
        print("✅ Policies seeded.")
    except IntegrityError:
        db.session.rollback()
        print("⚠️ Error seeding policies.")

# Seed Users
def seed_users():
    users = [
        {"username": "admin1", "password": "adminpass1", "role": UserRoleEnum.ADMIN},
        {"username": "admin2", "password": "adminpass2", "role": UserRoleEnum.ADMIN},
        {"username": "superadmin", "password": "superadminpass", "role": UserRoleEnum.SUPERADMIN},
    ]
    for u in users:
        if not User.query.filter_by(username=u["username"]).first():
            user = User(username=u["username"], role=u["role"])
            user.set_password(u["password"])
            db.session.add(user)
            print(f"✅ Added {u['username']}")
    db.session.commit()
    print("🎉 Users seeded.")

# Entry Point
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_device_policies()
        seed_users()
