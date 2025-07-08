
from dotenv import load_dotenv
import os

from flask import Flask
from models import db
from routes.device import device_routes
from routes.auth import login_route
from routes.policy import policy_route 
from routes.users import user_route
from routes.dashboard import dashboard_route
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_cors import CORS
load_dotenv()
def create_app():
    app=Flask(__name__)
     app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_DAYS", 1)))
    #apply cors to allow frontend access
    CORS(app,supports_credentials=True)
    jwt = JWTManager(app)
    db.init_app(app)
    app.register_blueprint(device_routes, url_prefix='')
    app.register_blueprint(login_route, url_prefix='')
    app.register_blueprint(policy_route, url_prefix='')
    app.register_blueprint(user_route, url_prefix='')
    app.register_blueprint(dashboard_route,url_prefix='')
    with app.app_context():
            print("Creating tables...")
            db.create_all()
            print("Tables created.")
    return app

if __name__ == '__main__':
    create_app().run(debug=True)