from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms import PasswordField
from wtforms.validators import EqualTo

class PostForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField("内容", validators=[DataRequired()])
    submit = SubmitField("发布文章")

class LoginForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    submit = SubmitField("登录")

class RegisterForm(FlaskForm):
    username = StringField("用户名", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    confirm = PasswordField("确认密码", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("注册")