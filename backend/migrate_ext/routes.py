# backend/migrate_ext/routes.py
from flask import Blueprint, request, g, current_app
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from flask_jwt_extended import jwt_required
from functools import wraps
from utils.db_conn import current_engine
from sqlalchemy import inspect
bp = Blueprint("migrate_ext", __name__, url_prefix="/api/migrate")




# ---------------- 装饰器：每请求新建/复用连接 ----------------
def with_db_conn(f):
    """
    装饰器：
    1. 从请求体拿到 host/port/user/pwd/db，创建 engine
    2. 把 engine 存入 g.db
    3. 视图函数结束后自动关闭
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.json
        url = (
            f"mysql+pymysql://{data['user']}:{data['pwd']}@"
            f"{data['host']}:{data['port']}/{data['db']}"
        )
        engine = create_engine(url, pool_pre_ping=True)
        # 校验一次连接
        try:
            engine.connect().close()
        except Exception as e:
            return {"msg": str(e)}, 400
        g.db = engine
        return f(*args, **kwargs)
    return wrapper

# ---------------- 路由 ----------------
@bp.post("/connect")
@jwt_required()
@with_db_conn
def connect():
    # 连接成功后 g.db 已可用
    return {"msg": "连接成功"}

# @bp.get("/tables")
# @jwt_required()
# @with_db_conn
# def tables():
#     insp = inspect(g.db)
#     return {"tables": insp.get_table_names()}
@bp.get("/tables")
@jwt_required()
def tables():
    engine = current_engine()
    insp = inspect(engine)
    return {"tables": insp.get_table_names()}

# @bp.post("/table")
# @jwt_required()
# @with_db_conn
# def migrate_table():
#     data = request.json
#     src, dst = data["source_table"], data["target_table"]

#     # 简单演示：直接 INSERT … SELECT
#     sql = f"INSERT INTO {dst} SELECT * FROM {src}"
#     try:
#         with Session(g.db) as s:
#             s.exec_driver_sql(sql)
#             s.commit()
#     except Exception as e:
#         return {"msg": str(e)}, 500
#     return {"msg": "迁移完成"}

@bp.post("/table")
@jwt_required()
def migrate_table():
    engine = current_engine()
    data = request.json
    sql = f"INSERT INTO {data['target_table']} SELECT * FROM {data['source_table']}"
    with Session(engine) as s:
        s.exec_driver_sql(sql)
        s.commit()
    return {"msg": "迁移完成"}