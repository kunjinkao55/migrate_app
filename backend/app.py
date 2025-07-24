from routes.migrate import bp as migrate_bp
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.migrate import copy_table_data
from migrate_ext.routes import bp as migrate_ext_bp
from extensions import jwt
from flask_jwt_extended import JWTManager
#from cli import init_db
from auth_mysql import bp as auth_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(migrate_ext_bp)
#app.cli.add_command(init_db)
CORS(app, supports_credentials=True)
jwt.init_app(app)
app.config["JWT_SECRET_KEY"] = "dev-secret"

@app.post("/api/migrate")
def migrate():
    data = request.json
    copy_table_data(data["source"], data["target"], data.get("where", ""))
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)