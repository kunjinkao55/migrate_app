
from werkzeug.security import generate_password_hash, check_password_hash
# 从 extensions 导入 db 对象
from extensions import db

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 使用 db.Text
    password_hash = db.Column(db.Text, nullable=False)

    def set_password(self, password):
        """设置密码，自动进行哈希加密"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """校验密码是否正确"""
        return check_password_hash(self.password_hash, password)
