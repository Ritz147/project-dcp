from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import enum
from sqlalchemy import Enum as SQLAlchemyEnum

db=SQLAlchemy()

import pytz

def to_ist(dt):
    ist = pytz.timezone("Asia/Kolkata")
    # Assume naive datetime is in UTC
    dt = pytz.utc.localize(dt)
    return dt.astimezone(ist)

class DeviceStatusEnum(enum.Enum):
    ACTIVE="active"
    INACTIVE="inactive"

class SMSTypeEnum(enum.Enum):
    OUTBOX= "outbox"
    INBOX= "inbox"

class DeviceInfo(db.Model):
    __tablename__="device_info"
    device_id=db.Column(db.String,primary_key=True)
    os_version=db.Column(db.String(100),default="")
    phone_name=db.Column(db.String(100),default="")
    brand=db.Column(db.String(100),default="")
    manufacturer=db.Column(db.String(100),default="")
    host=db.Column(db.String(100),default="")
    created_at=db.Column(db.DateTime,default=to_ist(datetime.utcnow()))
    #Relationships
    call_logs=db.relationship('CallLog',backref='device',lazy=True , cascade="all,delete-orphan")
    location=db.relationship('DeviceLocation',backref='device',lazy=True,cascade='all,delete-orphan')
    status=db.relationship('DeviceStatus',backref='device',lazy=True,cascade='all,delete-orphan')

class CallLog(db.Model):
    __tablename__='call_logs'
    call_id=db.Column(db.String,primary_key=True)
    device_id=db.Column(db.String,db.ForeignKey('device_info.device_id'),nullable=False)
    call_duration = db.Column(db.String(8), default="00:00:00")
    user_id=db.Column(db.String(100),default="")
    version=db.Column(db.String(20),default="")
    phone_number=db.Column(db.String(10),default="")
    timestamp=db.Column(db.DateTime,default=to_ist(datetime.utcnow()))
    name=db.Column(db.String(100),default="")
    type=db.Column(db.String(20),default="")
    number_type=db.Column(db.String(50),default="")
    number_label=db.Column(db.String(50), default="")
    cached_number_type=db.Column(db.String(50),default="")
    cached_number_label = db.Column(db.String(50), default="")
    cached_matched_number = db.Column(db.String(20), default="")
    sim_display_name=db.Column(db.String(50),default="")
    phone_account_id = db.Column(db.String(100), default="")

class DeviceLocation(db.Model):
    __tablename__='device_location'
    id=db.Column(db.String,default=lambda:str(uuid.uuid4()),primary_key=True)
    device_id=db.Column(db.String,db.ForeignKey('device_info.device_id'),nullable=False)
    latitude=db.Column(db.Float,default=0.0)
    longitude=db.Column(db.Float,default=0.0)
    accuracy=db.Column(db.Float,default=0.0)
    timestamp=db.Column(db.DateTime,default=to_ist(datetime.utcnow()))

class DeviceStatus(db.Model):
    __tablename__='device_status'
    id=db.Column(db.String,default=lambda:str(uuid.uuid4()),primary_key=True)
    device_id=db.Column(db.String,db.ForeignKey('device_info.device_id'),nullable=False)
    timestamp=db.Column(db.DateTime,default=to_ist(datetime.utcnow()))
    status=db.Column(SQLAlchemyEnum(DeviceStatusEnum),default=DeviceStatusEnum.ACTIVE,nullable=False)

class SMSLog(db.Model):
    __tablename__='sms_logs'
    id=db.Column(db.String,default=lambda:str(uuid.uuid4()),primary_key=True)
    device_id=db.Column(db.String,db.ForeignKey('device_info.device_id'),nullable=False)
    address=db.Column(db.String(),default="")
    body=db.Column(db.Text,default="")
    timestamp=db.Column(db.DateTime,default=to_ist(datetime.utcnow()))
    type=db.Column(SQLAlchemyEnum(SMSTypeEnum),default=SMSTypeEnum.OUTBOX, nullable=False)

class DevicePolicy(db.Model):
    __tablename__ = "device_policies"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_name = db.Column(db.String(100), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    action = db.Column(db.String(50), nullable=True)  # e.g., "block_app", "block_url"
    package_name = db.Column(db.String(200), nullable=True)  # e.g., com.whatsapp
    created_at = db.Column(db.DateTime, default=lambda: to_ist(datetime.utcnow()))
    updated_at = db.Column(db.DateTime, default=lambda: to_ist(datetime.utcnow()), onupdate=lambda: to_ist(datetime.utcnow()))
    assigned_devices = db.relationship('DevicePolicyAssignment', backref='policy', cascade='all, delete-orphan')

class DevicePolicyAssignment(db.Model):
    __tablename__ = "device_policy_assignments"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = db.Column(db.String, db.ForeignKey('device_policies.id'), nullable=False)
    policy_version=db.Column(db.Integer,nullable=False)
    device_id = db.Column(db.String, db.ForeignKey('device_info.device_id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=lambda: to_ist(datetime.utcnow())) 
    device = db.relationship('DeviceInfo', backref=db.backref('policy_assignments', cascade='all, delete-orphan'))

from werkzeug.security import generate_password_hash,check_password_hash
class UserRoleEnum(enum.Enum):
   ADMIN="admin"
   SUPERADMIN="superadmin"

class DashboardPartEnum(enum.Enum):
    DASHBOARD="dashboard"
    USERS="users"
    DEVICES="devices"
    POLICIES="policies" 

class User(db.Model):
    __tablename__="users"
    id=db.Column(db.String,primary_key=True,default=lambda:str(uuid.uuid4()))
    username=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(200),nullable=False)
    role=db.Column(SQLAlchemyEnum(UserRoleEnum),nullable=False)
    created_at=db.Column(db.DateTime,default=lambda: to_ist(datetime.utcnow()))
    access_permissions=db.relationship("DashboardAccess",backref="user",cascade="all,delete-orphan")
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    
class DashboardAccess(db.Model):
    __tablename__="dashboard_access"
    id=db.Column(db.String,primary_key=True , default=lambda:str(uuid.uuid4()))
    user_id=db.Column(db.String , db.ForeignKey("users.id"),nullable=False)
    dashboard_part=db.Column(SQLAlchemyEnum(DashboardPartEnum),nullable=False)

class InstalledApp(db.Model):
    __tablename__ = "installed_apps"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    package_name = db.Column(db.String(200), unique=True, nullable=False)

class InstalledAppPerDevice(db.Model):
    __tablename__ = "installed_apps_per_device"
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String, db.ForeignKey('device_info.device_id'), nullable=False)
    package_name = db.Column(db.String, db.ForeignKey('installed_apps.package_name'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: to_ist(datetime.utcnow()))
