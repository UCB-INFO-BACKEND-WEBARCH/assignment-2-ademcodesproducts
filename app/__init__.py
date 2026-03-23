import os
from flask import Flask
from flask_migrate import Migrate
from app.models import db


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 'postgresql://postgres:password@localhost:5432/taskdb'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    from app.routes.tasks import tasks
    from app.routes.categories import categories
    app.register_blueprint(tasks)
    app.register_blueprint(categories)

    return app
