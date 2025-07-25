from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# 创建 SQLAlchemy 实例，但不绑定 app
db = SQLAlchemy()

# 创建其他扩展实例
jwt = JWTManager()
migrate = Migrate()
