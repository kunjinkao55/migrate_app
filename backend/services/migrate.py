from sqlalchemy import select, delete
from extensions import SessionLocal
from models.table import Base, TestTable1, TestTable2

def create_tables():
    from extensions import engine
    Base.metadata.create_all(bind=engine)

def drop_tables():
    from extensions import engine
    Base.metadata.drop_all(bind=engine)

def add_objects(objects):
    with SessionLocal() as s:
        s.add_all(objects)
        s.commit()

def get_all_objects(model):
    with SessionLocal() as s:
        return s.scalars(select(model)).all()

def update_object(model, oid, update_data):
    with SessionLocal() as s:
        obj = s.get(model, oid)
        if obj:
            for k, v in update_data.items():
                setattr(obj, k, v)
            s.commit()

# def delete_object(model, oid):
#     with SessionLocal() as s:
#         s.execute(delete(model).where(model.id == oid))
#         s.commit()

# 建议的修改
def delete_object(model, oid):
    with SessionLocal() as s:
        # 1. 先用 session.get() 获取要删除的对象，这个方法经过优化，会优先从会话缓存中查找
        obj = s.get(model, oid)
        if obj:
            # 2. 如果对象存在，直接将其删除
            s.delete(obj)
            s.commit()
        # else: 可以选择在这里打印一个日志，表明对象未找到

# 原始版本 - 不使用懒加载
"""
def copy_table_data(source_model, target_model, condition=None):
    with SessionLocal() as s:
        q = select(source_model)
        if condition is not None:
            q = q.where(condition)
        rows = s.scalars(q).all()
        new_objs = [target_model(**{c.name: getattr(r, c.name)
                                    for c in source_model.__table__.columns
                                    if not c.primary_key})
                    for r in rows]
        s.add_all(new_objs)
        s.commit()
"""
#lazy loading version
def copy_table_data(source_model, target_model, condition=None):
    with SessionLocal() as s:
        q = select(source_model)
        if condition is not None:
            q = q.where(condition)
        
        # 在 select 语句上调用 execution_options，而不是在 session 上
        stream = s.scalars(q.execution_options(stream_results=True))
        
        batch_size = 1000  # 每次处理1000条
        new_objs_batch = []
        for r in stream:
            new_obj_data = {c.name: getattr(r, c.name)
                            for c in source_model.__table__.columns
                            if not c.primary_key}
            new_objs_batch.append(target_model(**new_obj_data))
            
            if len(new_objs_batch) >= batch_size:
                s.add_all(new_objs_batch)
                s.commit() # 提交批次
                new_objs_batch = [] # 清空批次
        
        # 提交最后一批不足batch_size的数据
        if new_objs_batch:
            s.add_all(new_objs_batch)
            s.commit()

'''测试函数'''

def print_table_data(model):
    objects = get_all_objects(model)
    print(f"\n=== {model.__tablename__} 数据 ===")
    for obj in objects:
        print(f"ID: {obj.id}, 姓名: {obj.name}, 性别: {obj.sex}, 创建时间: {obj.created_at}")

def run_tests():
    drop_tables()
    create_tables()
    add_objects([
        TestTable1(id=1, name='Jules', sex='Male'),
        TestTable1(id=2, name='Vincent', sex='Male'),
        TestTable1(id=3, name='Mia', sex='Female')
    ])
    copy_table_data(TestTable1, TestTable2, TestTable1.sex == 'Male')
    print("✅ 测试完成")
    print_table_data(TestTable1)
    print_table_data(TestTable2)