from flask import Blueprint, request
from sqlalchemy import create_engine
from flask_jwt_extended import create_access_token
from datetime import timedelta
from models.user import User
from extensions import SessionLocal
import json

bp = Blueprint("auth_mysql", __name__, url_prefix="/api/auth")

@bp.post("/register")
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"msg": "用户名和密码不能为空"}, 400
        
    with SessionLocal() as session:
        if session.query(User).filter_by(username=username).first():
            return {"msg": "用户名已存在"}, 400
            
        user = User()
        user.username = username
        user.set_password(password)
        session.add(user)
        try:
            session.commit()
            return {"msg": "注册成功"}
        except Exception as e:
            session.rollback()
            return {"msg": f"注册失败: {str(e)}"}, 500

@bp.post("/login")
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"msg": "用户名和密码不能为空"}, 400
        
    with SessionLocal() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            token = create_access_token(
                identity=json.dumps({"user_id": user.id, "username": user.username}),
                expires_delta=timedelta(days=1)
            )
            return {"access_token": token}
        return {"msg": "用户名或密码错误"}, 401