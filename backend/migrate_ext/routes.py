# backend/migrate_ext/routes.py
from flask import Blueprint, request, g
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session
from flask_jwt_extended import jwt_required
from functools import wraps
from utils.db_conn import current_engine

bp = Blueprint("migrate_ext", __name__, url_prefix="/api/migrate")

# ---------------- 装饰器：每请求新建/复用连接 (这个装饰器当前未被使用，但保留) ----------------
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
        try:
            with engine.connect() as connection:
                pass # 尝试建立连接
        except Exception as e:
            return {"msg": f"数据库连接失败: {e}"}, 400
        g.db = engine
        return f(*args, **kwargs)
    return wrapper

# ---------------- 路由 ----------------
@bp.post("/connect")
@jwt_required()
@with_db_conn
def connect():
    return {"msg": "连接成功"}

@bp.get("/tables")
@jwt_required()
def tables():
    try:
        engine = current_engine()
        insp = inspect(engine)
        return {"tables": insp.get_table_names()}
    except Exception as e:
        return {"msg": f"获取表列表失败: {e}"}, 500


@bp.post("/table")
@jwt_required()
def migrate_table():
    try:
        engine = current_engine()
        data = request.json
        source_table = data.get("source_table")
        target_table = data.get("target_table")

        if not source_table or not target_table:
            return {"msg": "源表和目标表名不能为空"}, 400

        with engine.connect() as connection:
            insp = inspect(engine)
            available_tables = insp.get_table_names()
            
            if source_table not in available_tables:
                return {"msg": f"源表 '{source_table}' 不存在"}, 404
            if target_table not in available_tables:
                return {"msg": f"目标表 '{target_table}' 不存在"}, 404

            # 获取源表和目标表的列信息
            source_columns = [col['name'] for col in insp.get_columns(source_table)]
            target_columns = [col['name'] for col in insp.get_columns(target_table)]
            
            # 获取主键列
            pk_columns = set([col['name'] for col in insp.get_pk_constraint(target_table)['constrained_columns']])
            
            # 过滤掉主键列
            columns = [col for col in source_columns if col not in pk_columns]
            
            if not columns:
                return {"msg": "没有可迁移的列"}, 400
                
            # 构建不包含主键的INSERT语句
            columns_str = ', '.join(f'`{col}`' for col in columns)
            sql = text(f"INSERT INTO `{target_table}` ({columns_str}) SELECT {columns_str} FROM `{source_table}`")
            
            with Session(engine) as session:
                try:
                    session.execute(sql)
                    session.commit()
                    return {"msg": "迁移完成"}
                except Exception as e:
                    session.rollback()
                    return {"msg": f"迁移过程中出错: {str(e)}"}, 500
            
    except Exception as e:
        return {"msg": f"迁移失败: {str(e)}"}, 500
