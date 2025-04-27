from flask_wtf import FlaskForm  # 导入Flask-WTF表单基类
from wtforms import StringField, TextAreaField, SubmitField  # 导入常用的表单字段类型
from wtforms.validators import DataRequired, Length  # 导入字段验证器
from wtforms import PasswordField  # 导入密码字段类型
from wtforms.validators import EqualTo  # 导入字段值相等验证器

class PostForm(FlaskForm):
    """博客文章表单类
    用于创建和编辑博客文章的表单，包含标题和内容字段
    """
    title = StringField("标题", validators=[
        DataRequired(),  # 确保标题不为空
        Length(min=1, max=100)  # 限制标题长度在1-100字符之间
    ])
    content = TextAreaField("内容", validators=[
        DataRequired()  # 确保文章内容不为空
    ])
    submit = SubmitField("发布文章")  # 表单提交按钮

class LoginForm(FlaskForm):
    """用户登录表单类
    处理用户登录的表单，包含用户名和密码字段
    """
    username = StringField("用户名", validators=[
        DataRequired()  # 确保用户名不为空
    ])
    password = PasswordField("密码", validators=[
        DataRequired()  # 确保密码不为空
    ])
    submit = SubmitField("登录")  # 登录按钮

class RegisterForm(FlaskForm):
    """用户注册表单类
    处理新用户注册的表单，包含用户名、密码和确认密码字段
    """
    username = StringField("用户名", validators=[
        DataRequired()  # 确保用户名不为空
    ])
    password = PasswordField("密码", validators=[
        DataRequired()  # 确保密码不为空
    ])
    confirm = PasswordField("确认密码", validators=[
        DataRequired(),  # 确保确认密码不为空
        EqualTo('password')  # 确保确认密码与密码字段值相同
    ])
    submit = SubmitField("注册")  # 注册按钮