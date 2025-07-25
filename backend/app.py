# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from extensions import jwt, migrate, engine
# from cli import init_db
# from auth_mysql import bp as auth_bp
# from migrate_ext.routes import bp as migrate_ext_bp
# from models.user import User
# from models.table import Base
# from extensions import engine


# app = Flask(__name__)
# CORS(app, supports_credentials=True)
# app.config["JWT_SECRET_KEY"] = "dev-secret"

# # 注册蓝图
# app.register_blueprint(auth_bp)
# app.register_blueprint(migrate_ext_bp)
# app.cli.add_command(init_db)

# # 初始化JWT
# jwt.init_app(app)

# # 确保所有表都被创建
# Base.metadata.create_all(bind=engine)

# @app.post("/api/migrate")
# def migrate():
#     data = request.json
#     copy_table_data(data["source"], data["target"], data.get("where", ""))
#     return jsonify({"ok": True})

# if __name__ == "__main__":
#     app.run(debug=True)
# backend/app.py

# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
# 从 extensions 导入所有扩展实例
from extensions import db, jwt, migrate
#from cli import init_db
from auth_mysql import bp as auth_bp
from migrate_ext.routes import bp as migrate_ext_bp
# 确保模型被导入，以便 Alembic 能够检测到
from models.user import User

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # --- 配置 ---
    app.config["JWT_SECRET_KEY"] = "dev-secret" # 应该使用更安全的密钥
    # 从环境变量或配置文件读取数据库URI
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:phi1osopher@localhost:3306/test0base"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- 初始化扩展 ---
    db.init_app(app)
    jwt.init_app(app)
    # 正确地将 db 对象传递给 migrate
    migrate.init_app(app, db)

    # --- 注册蓝图和命令 ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(migrate_ext_bp)
    #app.cli.add_command(init_db)

    return app

# 使用工厂模式创建 app
app = create_app()

@app.post("/api/migrate")
def migrate_func():
    data = request.json
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
