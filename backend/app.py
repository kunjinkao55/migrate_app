from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import jwt
from cli import init_db
from auth_mysql import bp as auth_bp
from migrate_ext.routes import bp as migrate_ext_bp
from models.user import User
from models.table import Base
from extensions import engine


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["JWT_SECRET_KEY"] = "dev-secret"

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(migrate_ext_bp)
app.cli.add_command(init_db)

# 初始化JWT
jwt.init_app(app)

# 确保所有表都被创建
Base.metadata.create_all(bind=engine)

@app.post("/api/migrate")
def migrate():
    data = request.json
    copy_table_data(data["source"], data["target"], data.get("where", ""))
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)