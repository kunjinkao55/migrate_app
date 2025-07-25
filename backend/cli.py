import click
from flask.cli import with_appcontext
from models.user import User
from models.table import Base
from extensions import engine

@click.command('init-db')
@with_appcontext
def init_db():
    """清空所有表并重新创建"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    click.echo('数据库已初始化。')
