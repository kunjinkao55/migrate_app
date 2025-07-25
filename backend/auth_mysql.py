# backend/auth_mysql.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
# 从 extensions 导入 db 对象
from extensions import db
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.post("/register")
def register():
    """注册用户"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # 使用 db.session 来查询
    if db.session.query(User).filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)

    # 使用 db.session 添加和提交
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


@bp.post("/login")
def login():
    """登录"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = db.session.query(User).filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Bad username or password"}), 401
