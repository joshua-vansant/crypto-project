from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://render_1_ssjk_user:wwuDljEgJ5HoCD0D5HrCfBf5YK6crvCp@dpg-cqtd6raj1k6c738j8g30-a.oregon-postgres.render.com/render_1_ssjk'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app