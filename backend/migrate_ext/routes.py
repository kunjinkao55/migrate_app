# backend/migrate_ext/routes.py
from flask import Blueprint, request, jsonify, session
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session as SQLAlchemySession
from flask_jwt_extended import jwt_required
import uuid
from extensions import db # 导入应用自身的db实例

bp = Blueprint("migrate_ext", __name__, url_prefix="/api/migrate")

# ... (get_migration_engine 和 connect, tables 函数保持不变) ...

@bp.post("/push")
@jwt_required()
def push_data():
    """
    接收源数据库信息，将数据推送到中转区（应用的数据库）
    """
    data = request.get_json()
    source_table = data.get("source_table")
    # 这里可以扩展，增加where条件等
    # where_clause = data.get("where_clause", "1=1") 

    if not source_table:
        return jsonify({"msg": "源表名不能为空"}), 400

    # 使用 session 中保存的连接信息创建源数据库引擎
    source_engine = get_migration_engine()
    if source_engine is None:
        return jsonify({"msg": "源数据库未连接或会话已过期，请重新连接"}), 401

    try:
        with source_engine.connect() as connection:
            # 1. 查询源表数据
            # 为了安全和性能，实际应用中应进行分页和更严格的SQL校验
            query = text(f"SELECT * FROM `{source_table}`")
            source_data = connection.execute(query).mappings().all()

            if not source_data:
                return jsonify({"msg": "源表中没有数据可推送"}), 400

            # 2. 创建一个唯一任务ID和对应的临时表名
            task_id = str(uuid.uuid4())
            temp_table_name = f"temp_migration_{task_id.replace('-', '_')}"
            
            # 3. 获取列信息并在应用数据库中创建临时表
            source_columns = source_data[0].keys()
            # 使用应用自身的数据库引擎 (db.engine)
            with db.engine.connect() as app_db_conn:
                # 动态生成CREATE TABLE语句
                # 注意：这里的类型推断很简单，实际应用可能需要更复杂的类型映射
                columns_def = ", ".join([f"`{col}` TEXT" for col in source_columns])
                create_table_sql = text(f"CREATE TABLE `{temp_table_name}` ({columns_def})")
                app_db_conn.execute(create_table_sql)
                app_db_conn.commit()

                # 4. 将数据插入临时表
                # 使用 SQLAlchemy Core API 来构建插入语句
                from sqlalchemy import table, column
                temp_table = table(temp_table_name, *[column(c) for c in source_columns])
                # 批量插入
                app_db_conn.execute(temp_table.insert(), [dict(row) for row in source_data])
                app_db_conn.commit()


        return jsonify({"msg": "数据已成功推送到中转区", "task_id": task_id}), 200

    except Exception as e:
        # 简单的错误处理
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

    # 使用 session 中保存的连接信息创建目标数据库引擎
    target_engine = get_migration_engine()
    if target_engine is None:
        return jsonify({"msg": "目标数据库未连接或会话已过期，请重新连接"}), 401

    temp_table_name = f"temp_migration_{task_id.replace('-', '_')}"

    try:
        # 1. 从应用数据库中读取临时表数据
        with db.engine.connect() as app_db_conn:
            insp = inspect(db.engine)
            if not insp.has_table(temp_table_name):
                return jsonify({"msg": "无效的任务ID或任务已过期"}), 404
            
            query = text(f"SELECT * FROM `{temp_table_name}`")
            temp_data = app_db_conn.execute(query).mappings().all()
            if not temp_data:
                 return jsonify({"msg": "中转区没有数据可拉取"}), 400
            
            temp_columns = set(temp_data[0].keys())

        # 2. 将数据写入目标表
        with target_engine.connect() as target_conn:
            target_insp = inspect(target_engine)
            if not target_insp.has_table(target_table):
                return jsonify({"msg": f"目标表 '{target_table}' 不存在"}), 404
                
            target_columns = set(col['name'] for col in target_insp.get_columns(target_table))
            
            # 找出共同的列进行迁移
            columns_to_copy = list(temp_columns & target_columns)
            if not columns_to_copy:
                 return jsonify({"msg": "源数据和目标表没有可迁移的共同列"}), 400
            
            # 使用 SQLAlchemy Core API 构建插入语句以防止SQL注入
            from sqlalchemy import table, column
            target_table_obj = table(target_table, *[column(c) for c in columns_to_copy])

            # 准备要插入的数据
            data_to_insert = [{col: row[col] for col in columns_to_copy} for row in temp_data]

            target_conn.execute(target_table_obj.insert(), data_to_insert)
            target_conn.commit()

        # 3. (可选) 清理临时表
        with db.engine.connect() as app_db_conn:
            drop_sql = text(f"DROP TABLE `{temp_table_name}`")
            app_db_conn.execute(drop_sql)
            app_db_conn.commit()

        return jsonify({"msg": f"数据已成功拉取到表 '{target_table}'"}), 200

    except Exception as e:
        return jsonify({"msg": f"拉取数据失败: {str(e)}"}), 500