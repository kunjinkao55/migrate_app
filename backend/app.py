# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db, jwt, migrate
from auth_mysql import bp as auth_bp
from migrate_ext.routes import bp as migrate_ext_bp
from models.user import User

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    # --- 配置 ---
    # 添加一个用于 session 加密的密钥，内容可以自定义
    app.config["SECRET_KEY"] = "your-super-secret-key-for-sessions" 
    app.config["JWT_SECRET_KEY"] = "dev-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:phi1osopher@localhost:3306/test0base"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- 初始化扩展 ---
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # --- 注册蓝图 ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(migrate_ext_bp)

    return app

# 使用工厂模式创建 app
app = create_app()

@app.post("/api/migrate")
def migrate_func():
    """这是一个之前修正过的测试接口，可以保留或删除"""
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "Request body must be valid JSON"}), 400
    print(f"收到迁移请求: {data}")
    return jsonify({"ok": True, "message": "Migration task started successfully"})

if __name__ == "__main__":
    app.run(debug=True)
