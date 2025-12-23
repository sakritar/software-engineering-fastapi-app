from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy()


def create_app(conf: Optional[dict] = None):
    app = Flask(__name__)

    conf = conf or {}

    app.config['SQLALCHEMY_DATABASE_URI'] = conf.get('SQLALCHEMY_DATABASE_URI', SQLALCHEMY_DATABASE_URI)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = conf.get(
        'SQLALCHEMY_TRACK_MODIFICATIONS',
        SQLALCHEMY_TRACK_MODIFICATIONS
    )

    db.init_app(app)

    from app.routes import posts_bp
    app.register_blueprint(posts_bp)

    return app
