from sqlalchemy import select, delete
from ..extensions import SessionLocal
from ..models.table import Base, TestTable1, TestTable2

def create_tables():
    from ..extensions import engine
    Base.metadata.create_all(bind=engine)

def drop_tables():
    from ..extensions import engine
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

def delete_object(model, oid):
    with SessionLocal() as s:
        s.execute(delete(model).where(model.id == oid))
        s.commit()

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

if __name__ == '__main__':
    run_tests()