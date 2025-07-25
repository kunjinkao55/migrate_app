# backend/migrate_ext/routes.py
from flask import Blueprint, request, jsonify, session, Response
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session as SQLAlchemySession
from flask_jwt_extended import jwt_required
import uuid
from extensions import db 

bp = Blueprint("migrate_ext", __name__, url_prefix="/api/migrate")

# --- 新增的修复代码 ---
# 这个函数会在该蓝图的所有路由执行前运行
@bp.before_request
def handle_preflight():
    if request.method.upper() == 'OPTIONS':
        # 创建一个空的 200 OK 响应
        response = Response()
        # Flask-CORS 会在 after_request 阶段为这个响应添加正确的 CORS 头
        return response
# --- 修复代码结束 ---


def get_migration_engine():
    """
    从服务器端 session 中获取数据库连接信息并创建 engine。
    如果 session 中没有信息，则返回 None。
    """
    db_creds = session.get('migration_db_creds')
    if not db_creds:
        return None
    
    url = (
        f"mysql+pymysql://{db_creds['user']}:{db_creds['pwd']}@"
        f"{db_creds['host']}:{db_creds['port']}/{db_creds['db']}"
    )
    try:
        engine = create_engine(url, pool_pre_ping=True)
        connection = engine.connect()
        connection.close()
        return engine
    except Exception as e:
        print(f"创建引擎失败: {e}")
        return None

@bp.post("/connect")
@jwt_required()
def connect():
    """
    接收数据库连接信息，验证后存入 session。
    """
    data = request.get_json()
    if not data:
        return jsonify({"msg": "请求体必须是 JSON"}), 400

    required_keys = ['host', 'port', 'user', 'pwd', 'db']
    if not all(key in data for key in required_keys):
        return jsonify({"msg": "缺少数据库连接凭据"}), 400

    session['migration_db_creds'] = {
        'host': data['host'],
        'port': data['port'],
        'user': data['user'],
        'pwd': data['pwd'],
        'db': data['db']
    }

    engine = get_migration_engine()
    if engine is None:
        session.pop('migration_db_creds', None)
        return jsonify({"msg": "数据库连接失败，请检查凭据"}), 400
    
    return jsonify({"msg": "连接成功并已保存会话"})

@bp.get("/tables")
@jwt_required()
def tables():
    """获取当前已连接数据库的表列表"""
    engine = get_migration_engine()
    if engine is None:
        return jsonify({"msg": "数据库未连接或会话已过期，请重新连接"}), 401
        
    try:
        insp = inspect(engine)
        return jsonify({"tables": insp.get_table_names()})
    except Exception as e:
        return jsonify({"msg": f"获取表列表失败: {e}"}), 500

@bp.post("/push")
@jwt_required()
def push_data():
    """
    接收源数据库信息，将数据推送到中转区（应用的数据库）
    """
    data = request.get_json()
    source_table = data.get("source_table")
    
    if not source_table:
        return jsonify({"msg": "源表名不能为空"}), 400

    source_engine = get_migration_engine()
    if source_engine is None:
        return jsonify({"msg": "源数据库未连接或会话已过期，请重新连接"}), 401

    try:
        with source_engine.connect() as connection:
            query = text(f"SELECT * FROM `{source_table}`")
            source_data = connection.execute(query).mappings().all()

            if not source_data:
                return jsonify({"msg": "源表中没有数据可推送"}), 400

            task_id = str(uuid.uuid4())
            temp_table_name = f"temp_migration_{task_id.replace('-', '_')}"
            
            source_columns = source_data[0].keys()
            with db.engine.connect() as app_db_conn:
                columns_def = ", ".join([f"`{col}` TEXT" for col in source_columns])
                create_table_sql = text(f"CREATE TABLE `{temp_table_name}` ({columns_def})")
                app_db_conn.execute(create_table_sql)
                app_db_conn.commit()

                from sqlalchemy import table, column
                temp_table = table(temp_table_name, *[column(c) for c in source_columns])
                app_db_conn.execute(temp_table.insert(), [dict(row) for row in source_data])
                app_db_conn.commit()

        return jsonify({"msg": "数据已成功推送到中转区", "task_id": task_id}), 200

    except Exception as e:
        return jsonify({"msg": f"推送数据失败: {str(e)}"}), 500


@bp.post("/pull")
@jwt_required()
def pull_data():
    """
    根据任务ID，从中转区拉取数据到目标数据库
    """
    data = request.get_json()
    task_id = data.get("task_id")
    target_table = data.get("target_table")

    if not task_id or not target_table:
        return jsonify({"msg": "任务ID和目标表名不能为空"}), 400

    target_engine = get_migration_engine()
    if target_engine is None:
        return jsonify({"msg": "目标数据库未连接或会话已过期，请重新连接"}), 401

    temp_table_name = f"temp_migration_{task_id.replace('-', '_')}"

    try:
        with db.engine.connect() as app_db_conn:
            insp = inspect(db.engine)
            if not insp.has_table(temp_table_name):
                return jsonify({"msg": "无效的任务ID或任务已过期"}), 404
            
            query = text(f"SELECT * FROM `{temp_table_name}`")
            temp_data = app_db_conn.execute(query).mappings().all()
            if not temp_data:
                 return jsonify({"msg": "中转区没有数据可拉取"}), 400
            
            temp_columns = set(temp_data[0].keys())

        with target_engine.connect() as target_conn:
            target_insp = inspect(target_engine)
            if not target_insp.has_table(target_table):
                return jsonify({"msg": f"目标表 '{target_table}' 不存在"}), 404
                
            target_columns = set(col['name'] for col in target_insp.get_columns(target_table))
            
            columns_to_copy = list(temp_columns & target_columns)
            if not columns_to_copy:
                 return jsonify({"msg": "源数据和目标表没有可迁移的共同列"}), 400
            
            from sqlalchemy import table, column
            target_table_obj = table(target_table, *[column(c) for c in columns_to_copy])
            data_to_insert = [{col: row[col] for col in columns_to_copy} for row in temp_data]
            target_conn.execute(target_table_obj.insert(), data_to_insert)
            target_conn.commit()

        with db.engine.connect() as app_db_conn:
            drop_sql = text(f"DROP TABLE `{temp_table_name}`")
            app_db_conn.execute(drop_sql)
            app_db_conn.commit()

        return jsonify({"msg": f"数据已成功拉取到表 '{target_table}'"}), 200

    except Exception as e:
        return jsonify({"msg": f"拉取数据失败: {str(e)}"}), 500