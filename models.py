from flask_sqlalchemy import SQLAlchemy  # 导入SQLAlchemy ORM
from datetime import datetime  # 导入日期时间处理模块
from flask_login import UserMixin  # 导入用户认证所需的基类
from werkzeug.security import generate_password_hash, check_password_hash  # 导入密码加密相关函数

# 创建数据库实例
db = SQLAlchemy()

class Post(db.Model):
    """博客文章数据模型
    存储博客文章的相关信息，包括标题、内容、创建时间和作者关联
    """
    id = db.Column(db.Integer, primary_key=True)  # 文章唯一标识符
    title = db.Column(db.String(100), nullable=False)  # 文章标题，不可为空，最大长度100字符
    content = db.Column(db.Text, nullable=False)  # 文章内容，不可为空，文本类型
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 文章创建时间，默认为当前UTC时间
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 外键，关联到用户表的id字段

class User(db.Model, UserMixin):
    """用户数据模型
    存储用户信息，继承UserMixin以支持Flask-Login的用户认证功能
    """
    id = db.Column(db.Integer, primary_key=True)  # 用户唯一标识符
    username = db.Column(db.String(64), unique=True, nullable=False)  # 用户名，唯一且不可为空
    password_hash = db.Column(db.String(128), nullable=False)  # 存储加密后的密码哈希值

    # 建立与Post模型的一对多关系，backref创建反向引用，lazy=True使用懒加载
    posts = db.relationship('Post', backref='author', lazy=True)

    def set_password(self, password):
        """设置用户密码
        将明文密码转换为加密哈希值存储
        Args:
            password: 明文密码
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证用户密码
        检查提供的密码是否与存储的密码哈希值匹配
        Args:
            password: 待验证的明文密码
        Returns:
            bool: 密码是否正确
        """
        return check_password_hash(self.password_hash, password)
