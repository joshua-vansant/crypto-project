from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://jmvs_project_storage_user:3CaSFRahhno5g1xINy0mGPrH7Mo2D61T@dpg-cqtqjpjv2p9s73ci779g-a.oregon-postgres.render.com/jmvs_project_storage'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app