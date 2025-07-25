# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS  # 确保导入了 CORS
from extensions import db, jwt, migrate
from auth_mysql import bp as auth_bp
from migrate_ext.routes import bp as migrate_ext_bp
# 移除 models.user 的导入，因为它没有被直接使用
# from models.user import User

def create_app():
    app = Flask(__name__)
    
    # 关键：请确保您的 CORS 配置与此完全一致
    # 它应该在所有 app.config 设置之前
    CORS(app, supports_credentials=True)

    # --- 配置 ---
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

# ... (文件的其余部分保持不变) ...

if __name__ == "__main__":
    app.run(debug=True)