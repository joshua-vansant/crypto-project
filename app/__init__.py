from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://crypto_data_v4i1_user:eFI9rRftWJ6PRcviRPVQzkIXbSRHJmfL@dpg-cqtmjl3v2p9s73djqjsg-a.oregon-postgres.render.com/crypto_data_v4i1'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app