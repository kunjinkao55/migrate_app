from flask_jwt_extended import get_jwt_identity
from sqlalchemy import create_engine
import json
def current_engine():
    """
    根据 JWT 里保存的 MySQL 账号信息，返回一个 SQLAlchemy Engine
    """
    identity = json.loads(get_jwt_identity())
    url = f"mysql+pymysql://{identity['user']}:{identity['password']}@{identity['host']}:{identity['port']}/{identity['db']}"
    return create_engine(url, pool_pre_ping=True)