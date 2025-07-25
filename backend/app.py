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

# 这是被修正的接口
@app.post("/api/migrate")
def migrate_func():
    """处理迁移请求的接口"""
    # 1. 使用 get_json() 来安全地获取数据
    data = request.get_json()

    # 2. 检查数据是否存在
    if data is None:
        # 如果前端没有发送JSON数据，返回一个明确的JSON错误信息，而不是让服务器崩溃
        return jsonify({"msg": "Request body must be valid JSON"}), 400

    # 在这里可以添加您真实的迁移逻辑
    # 例如: source = data.get('source'), target = data.get('target') etc.
    print(f"收到迁移请求: {data}")

    # 3. 返回一个成功的JSON响应
    return jsonify({"ok": True, "message": "Migration task started successfully"})


if __name__ == "__main__":
    app.run(debug=True)
