# backend/auth_mysql.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db
from models.user import User
# 导入 sqlalchemy 的异常，以便更精确地捕获
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.post("/register")
def register():
    """注册用户"""
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Request body must be JSON"}), 400
        
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if db.session.query(User).filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)
    
    db.session.add(user)
    
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        # 捕获所有 SQLAlchemy 的错误
        db.session.rollback() # 回滚事务
        # 将具体的错误信息返回给前端
        return jsonify({"msg": f"Database error: {str(e)}"}), 500
    except Exception as e:
        # 捕获其他未知错误
        db.session.rollback()
        return jsonify({"msg": f"An unexpected error occurred: {str(e)}"}), 500


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
