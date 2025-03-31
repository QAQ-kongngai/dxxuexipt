from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)                          # ✅ 1. 先创建 app 实例
    app.config.from_object(Config)                 # ✅ 2. 加载配置类
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER  # ✅ 3. 再单独添加上传目录配置

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
