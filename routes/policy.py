from flask import Blueprint, jsonify , request
from models import db , DevicePolicy , DevicePolicyAssignment , DeviceInfo
from sqlalchemy.exc import SQLAlchemyError

policy_route = Blueprint('policy_route', __name__)

class PolicyApi:
    @staticmethod
    @policy_route.route('/get-all-policies', methods=['GET'])
    def get_all_policies():
        try:
            policies = DevicePolicy.query.all()
            result = [
                {
                    "id": policy.id,
                    "policy_name": policy.policy_name,
                    "enabled": policy.enabled,
                    "action":policy.action,
                    "created_at": policy.created_at.isoformat(),
                    "updated_at": policy.updated_at.isoformat(),
                    "assigned_devices":len(policy.assigned_devices),
                    "policy_version":policy.policy_version

                }
                for policy in policies
            ]
            return jsonify({
                "success": True,
                "policies": result
            }), 200
        except SQLAlchemyError as e:
            return jsonify({
                "error": "Database error",
                "details": str(e)
            }), 500
        except Exception as e:
            return jsonify({
                "error": "Server error",
                "details": str(e)
            }), 500
    

    @staticmethod
    @policy_route.route('/toggle-policy', methods=['POST'])
    def toggle_policy():
            try:
                data = request.get_json()
                policy_id = data.get("policy_id")

                if not policy_id:
                    return jsonify({"error": "Policy ID is required"}), 400

                policy = DevicePolicy.query.filter(DevicePolicy.id == policy_id).first()
                if not policy:
                    return jsonify({"error": "Policy not found"}), 404

                policy.enabled = not policy.enabled
                db.session.commit()

                return jsonify({
                    "success": True,
                    "policy_id": policy.id,
                    "new_status": policy.enabled
                }), 200

            except SQLAlchemyError as e:
                db.session.rollback()
                print("SQLAlchemyError:", str(e))  # ✅ Print to terminal
                return jsonify({"error": "Database error", "details": str(e)}), 500
            except Exception as e:
                print("Unhandled Exception:", str(e))  # ✅ Print to terminal
                return jsonify({"error": "Server error", "details": str(e)}), 500
    
    @staticmethod
    @policy_route.route('/device-policy-assignments', methods=['GET'])
    def get_assignments():
        try:
            assignments = DevicePolicyAssignment.query.all()
            result = [
                {
                    "assignment_id": a.id,
                    "device_id": a.device_id,
                    "policy_id": a.policy_id,
                    "policy_name": a.policy.policy_name,
                    "assigned_at": a.assigned_at.isoformat()
                } for a in assignments
            ]
            return jsonify({"success": True, "assignments": result}), 200
        except Exception as e:
            return jsonify({"error": "Server error", "details": str(e)}), 500
    
    @staticmethod
    @policy_route.route('/assign-policy', methods=['POST'])
    def assign_policy():
        try:
            data = request.get_json()
            device_id = data.get("device_id")
            policy_id = data.get("policy_id")

            if not device_id or not policy_id:
                return jsonify({"error": "Device ID and Policy ID are required"}), 400

            # Avoid duplicate assignment
            exists = DevicePolicyAssignment.query.filter_by(device_id=device_id, policy_id=policy_id).first()
            if exists:
                return jsonify({"error": "Policy already assigned to this device"}), 409

            assignment = DevicePolicyAssignment(device_id=device_id, policy_id=policy_id)
            db.session.add(assignment)
            db.session.commit()

            return jsonify({"success": True, "assignment_id": assignment.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/toggle-device-policy', methods=['POST'])
    def toggle_device_policy():
        try:
            data = request.get_json()
            device_id = data.get("device_id")
            policy_id = data.get("policy_id")

            if not device_id or not policy_id:
                return jsonify({"error": "Device ID and Policy ID required"}), 400

            assignment = DevicePolicyAssignment.query.filter_by(device_id=device_id, policy_id=policy_id).first()
            if assignment:
                db.session.delete(assignment)
                db.session.commit()
                return jsonify({"success": True, "action": "unassigned"}), 200
            else:
                new_assignment = DevicePolicyAssignment(device_id=device_id, policy_id=policy_id)
                db.session.add(new_assignment)
                db.session.commit()
                return jsonify({"success": True, "action": "assigned"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/toggle-assignment-policy', methods=['POST'])
    def toggle_assignment_policy():
        try:
            data = request.get_json()
            device_id = data.get("device_id")
            policy_id = data.get("policy_id")

            if not device_id or not policy_id:
                return jsonify({"error": "Device ID and Policy ID required"}), 400

            assignment = DevicePolicyAssignment.query.filter_by(device_id=device_id, policy_id=policy_id).first()
            if assignment:
                db.session.delete(assignment)
                db.session.commit()
                return jsonify({"success": True, "action": "unassigned"}), 200
            else:
                new_assignment = DevicePolicyAssignment(device_id=device_id, policy_id=policy_id)
                db.session.add(new_assignment)
                db.session.commit()
                return jsonify({"success": True, "action": "assigned"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/unassign-policy', methods=['DELETE'])
    def unassign_policy():
        try:
            data = request.get_json()
            device_id = data.get("device_id")
            policy_id = data.get("policy_id")

            assignment = DevicePolicyAssignment.query.filter_by(device_id=device_id, policy_id=policy_id).first()
            if not assignment:
                return jsonify({"error": "No such assignment"}), 404

            db.session.delete(assignment)
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/devices-by-policy/<policy_id>', methods=['GET'])
    def get_devices_by_policy(policy_id):
        try:
            assignments = DevicePolicyAssignment.query.filter_by(policy_id=policy_id).all()
            result = [
                {
                    "device_id": a.device_id,
                    "phone_name": a.device.phone_name,
                    "brand": a.device.brand
                }
                for a in assignments
            ]
            return jsonify({"success": True, "devices": result}), 200
        except Exception as e:
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/policies-with-devices', methods=['GET'])
    def get_policies_with_devices():
        try:
            policies = DevicePolicy.query.all()
            result = []
            for policy in policies:
                assigned = {a.device_id for a in policy.assigned_devices}
                all_devices = DeviceInfo.query.all()
                devices = []
                for d in all_devices:
                    devices.append({
                        "device_id": d.device_id,
                        "device_name": d.phone_name,
                        "assigned": d.device_id in assigned
                    })
                result.append({
                    "policy_id": policy.id,
                    "policy_name": policy.policy_name,
                    "devices": devices
                })
            return jsonify({"success": True, "policies": result}), 200
        except Exception as e:
            return jsonify({"error": "Server error", "details": str(e)}), 500

    
    @staticmethod
    @policy_route.route('/get-device-policies', methods=['GET'])
    def get_device_policies():
        try:
            device_id = request.args.get("device_id")
            if not device_id:
                return jsonify({"error": "Device ID is required"}), 400

            # All policies
            all_policies = DevicePolicy.query.all()

            # Assigned policy ids for this device
            assigned_ids = {
                a.policy_id
                for a in DevicePolicyAssignment.query.filter_by(device_id=device_id).all()
            }

            policies = []
            for p in all_policies:
                if p.id in assigned_ids:
                    policies.append({
                        "id": p.id,
                        "policy_name": p.policy_name,
                        "enabled": p.enabled,
                        "created_at": p.created_at.isoformat(),
                        "updated_at": p.updated_at.isoformat(),
                        "action":p.action,
                        "package_name":p.package_name
                    })

            return jsonify({"success": True, "policies": policies}), 200

        except Exception as e:
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @staticmethod
    @policy_route.route('/create-policy', methods=['POST'])
    def create_policy():
        data = request.get_json()
        try:
            name = data.get("policy_name")
            enabled = data.get("enabled", True)
            action = data.get("action", "")
            package_name = data.get("package_name", "")
            policy_version = data.get("policy_version", 1)
            device_ids = data.get("device_ids", [])

            if not name:
                return jsonify({"success": False, "message": "Policy name required"}), 400

            # Create the policy
            new_policy = DevicePolicy(
                policy_name=name,
                enabled=enabled,
                action=action,
                package_name=package_name,
                policy_version=policy_version
            )
            db.session.add(new_policy)
            db.session.commit()

            # Device ID existence check
            existing_device_ids = {d.device_id for d in DeviceInfo.query.all()}
            skipped_devices = []

            for device_id in device_ids:
                if device_id in existing_device_ids:
                    print(f"[✔] Device exists: {device_id}")
                    assignment = DevicePolicyAssignment(device_id=device_id, policy_id=new_policy.id)
                    db.session.add(assignment)
                else:
                    print(f"[✘] Device NOT found in DB: {device_id}")
                    skipped_devices.append(device_id)

            db.session.commit()

            return jsonify({
                "success": True,
                "policy_id": new_policy.id,
                "skipped_devices": skipped_devices
            }), 201

        except KeyError as ke:
            return jsonify({"success": False, "message": f"Missing field: {str(ke)}"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500
