# backend/migrate_ext/routes.py
from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session as SQLAlchemySession
from flask_jwt_extended import jwt_required

bp = Blueprint("migrate_ext", __name__, url_prefix="/api/migrate")

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
        # 测试连接是否成功
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

    # 将凭据存储在服务器 session 中
    session['migration_db_creds'] = {
        'host': data['host'],
        'port': data['port'],
        'user': data['user'],
        'pwd': data['pwd'],
        'db': data['db']
    }

    # 尝试连接以验证凭据
    engine = get_migration_engine()
    if engine is None:
        session.pop('migration_db_creds', None) # 如果连接失败，清除 session
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

@bp.post("/table")
@jwt_required()
def migrate_table():
    """执行表数据迁移"""
    engine = get_migration_engine()
    if engine is None:
        return jsonify({"msg": "数据库未连接或会话已过期，请重新连接"}), 401
        
    data = request.get_json()
    if not data:
        return jsonify({"msg": "请求体必须是 JSON"}), 400

    source_table = data.get("source_table")
    target_table = data.get("target_table")

    if not source_table or not target_table:
        return jsonify({"msg": "源表和目标表名不能为空"}), 400

    try:
        with engine.connect() as connection:
            insp = inspect(engine)
            available_tables = insp.get_table_names()
            
            if source_table not in available_tables:
                return jsonify({"msg": f"源表 '{source_table}' 不存在"}), 404
            if target_table not in available_tables:
                return jsonify({"msg": f"目标表 '{target_table}' 不存在"}), 404

            # --- 优化后的列匹配逻辑 ---
            source_columns = set(col['name'] for col in insp.get_columns(source_table))
            target_columns = set(col['name'] for col in insp.get_columns(target_table))
            
            pk_info = insp.get_pk_constraint(target_table)
            pk_columns = set(pk_info['constrained_columns']) if pk_info else set()

            # 要复制的列是源表和目标表的交集，并从中排除目标表的主键
            columns_to_copy = list((source_columns & target_columns) - pk_columns)
            
            if not columns_to_copy:
                return jsonify({"msg": "没有可迁移的共同列"}), 400
                
            columns_str = ', '.join(f'`{col}`' for col in columns_to_copy)
            sql = text(f"INSERT INTO `{target_table}` ({columns_str}) SELECT {columns_str} FROM `{source_table}`")
            
            with SQLAlchemySession(engine) as db_session:
                try:
                    db_session.execute(sql)
                    db_session.commit()
                    return jsonify({"msg": "迁移完成"})
                except Exception as e:
                    db_session.rollback()
                    return jsonify({"msg": f"迁移过程中出错: {str(e)}"}), 500
            
    except Exception as e:
        return jsonify({"msg": f"迁移失败: {str(e)}"}), 500
