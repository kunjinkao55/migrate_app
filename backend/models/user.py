# 1. 从 sqlalchemy 导入 Text, Integer, String
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

# 假设您的 Base 是从 .table 文件导入的
from .table import Base

class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    
    # 2. 将 password_hash 字段的类型改为 Text
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)

    def set_password(self, password):
        """设置密码，自动进行哈希加密"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """校验密码是否正确"""
        return check_password_hash(self.password_hash, password)

