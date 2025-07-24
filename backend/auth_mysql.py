from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from flask_jwt_extended import create_access_token
from datetime import timedelta
import json

bp = Blueprint("auth_mysql", __name__, url_prefix="/api/auth")

@bp.post("/login")
def login():
    """
    前端发来：
    {
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "root",
      "db": "mydb"
    }
    """
    data = request.json
    data['port'] = str(data['port']) 
    url = f"mysql+pymysql://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['db']}"
    try:
        engine = create_engine(url, pool_pre_ping=True)
        engine.connect().close()          # 直接连一次验证
    except Exception as e:
        return {"msg": str(e)}, 401

    # 登录成功：把连接信息打包进 JWT

    token = create_access_token(
        identity=json.dumps({
            "host": data["host"],
            "port": data["port"],
            "user": data["user"],
            "password": data["password"],
            "db": data["db"]}),
        expires_delta=timedelta(days=1)
)
    return {"access_token": token}