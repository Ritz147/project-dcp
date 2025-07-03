from models import db, DevicePolicy
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pytz
import uuid

# ✅ Import create_app from your app.py
from app import create_app

# IST conversion helper
def to_ist(dt):
    ist = pytz.timezone("Asia/Kolkata")
    dt = pytz.utc.localize(dt)
    return dt.astimezone(ist)

# Your list of policies
POLICY_NAMES = [
    "cameraDisabled",
    "usbFileTransferDisabled",
    "safeBootDisabled",
    "installAppsDisabled",
    "uninstallAppsDisabled",
    "bluetoothDisabled",
    "wifiDisabled",
    "tetheringDisabled",
    "cellularDataDisabled",
    "keyguardDisabled"
]

# Function to seed policies
def seed_device_policies():
    for policy_name in POLICY_NAMES:
        existing = DevicePolicy.query.filter_by(policy_name=policy_name).first()
        if not existing:
            new_policy = DevicePolicy(
                id=str(uuid.uuid4()),
                policy_name=policy_name,
                enabled=True,
                created_at=to_ist(datetime.utcnow()),
                updated_at=to_ist(datetime.utcnow())
            )
            db.session.add(new_policy)
    
    try:
        db.session.commit()
        print("✅ Policies seeded successfully.")
    except IntegrityError:
        db.session.rollback()
        print("⚠️ Integrity error occurred. Possibly due to duplicates.")

# Entry point
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_device_policies()
