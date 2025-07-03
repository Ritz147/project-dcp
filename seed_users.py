
from models import db, User, UserRoleEnum
from app import create_app
def seed_users():
    app = create_app()
    with app.app_context():
        db.create_all()

        users_to_seed = [
            {
                "username": "admin1",
                "password": "adminpass1",
                "role": UserRoleEnum.ADMIN
            },
            {
                "username": "admin2",
                "password": "adminpass2",
                "role": UserRoleEnum.ADMIN
            },
            {
                "username": "superadmin",
                "password": "superadminpass",
                "role": UserRoleEnum.SUPERADMIN
            }
        ]

        for user_data in users_to_seed:
            if not User.query.filter_by(username=user_data["username"]).first():
                user = User(
                    username=user_data["username"],
                    role=user_data["role"]
                )
                user.set_password(user_data["password"])
                db.session.add(user)
                print(f"✅ Seeded user: {user_data['username']}")

        db.session.commit()
        print("🎉 All seed users added.")

if __name__ == "__main__":
    seed_users()