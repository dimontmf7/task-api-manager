from flask import Flask
from .db import db
from .routes import api
from .auth import auth_bp
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'c0a156954253f90bf7ef2cbc9b21185abf8ee7fccb95da1d0c23c0be67739100'  

    db.init_app(app)
    api.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        db.create_all()

    return app
