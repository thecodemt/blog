from flask import Flask, render_template, request, redirect, url_for, abort  # 导入Flask核心功能
from models import db, Post  # 导入数据模型
from forms import PostForm  # 导入文章表单
import markdown  # 导入Markdown解析器
from flask_login import LoginManager, login_user, logout_user, login_required, current_user  # 导入用户认证相关功能
from models import User  # 导入用户模型
from forms import LoginForm, RegisterForm  # 导入登录和注册表单
from flask import Markup  # 导入HTML标记处理工具


app = Flask(__name__)  # 创建Flask应用实例

# 应用配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'  # 设置SQLite数据库URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭SQLAlchemy的修改跟踪功能
app.config['SECRET_KEY'] = 'your-secret-key'  # 设置应用密钥，用于会话安全

# 初始化数据库
db.init_app(app)

# 系统限制配置
MAX_USERS = 100  # 最大用户注册数量
MAX_POSTS = 1000  # 最大文章数量

@app.template_filter('markdown')
def markdown_filter(text):
    """自定义模板过滤器，用于渲染Markdown文本
    Args:
        text: Markdown格式的文本
    Returns:
        转换后的HTML标记
    """
    return Markup(markdown.markdown(text, extensions=['extra']))

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 设置登录视图的端点

@login_manager.user_loader
def load_user(user_id):
    """加载用户的回调函数
    Args:
        user_id: 用户ID
    Returns:
        User对象或None
    """
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """首页路由
    显示按创建时间倒序排列的文章列表
    """
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """文章详情页路由
    Args:
        post_id: 文章ID
    Returns:
        渲染后的文章详情页面
    """
    post = Post.query.get(post_id)
    if post is None:
        abort(404)  # 文章不存在时返回404错误
    
    # 使用markdown渲染文章内容
    content_html = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])

    return render_template('post_detail.html', post=post, content_html=content_html)

@app.route('/create', methods=['GET', 'POST'])
@login_required  # 需要登录才能访问
def create():
    """创建新文章的路由
    处理GET请求显示创建表单，POST请求处理表单提交
    """
    # 检查是否超过最大文章数限制
    post_count = Post.query.count()
    if post_count >= MAX_POSTS:
        return "文章数已达到最大值，无法再发布新文章！"

    form = PostForm()
    if form.validate_on_submit():  # 验证表单提交
        new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', form=form)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    """编辑文章的路由
    Args:
        post_id: 要编辑的文章ID
    Returns:
        GET请求返回编辑表单，POST请求处理表单提交
    """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # 非作者不能编辑文章
    form = PostForm(obj=post)

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('edit.html', form=form, post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    """删除文章的路由
    Args:
        post_id: 要删除的文章ID
    Returns:
        删除后重定向到首页
    """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # 非作者不能删除文章
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册路由
    处理用户注册表单的显示和提交
    """
    # 检查是否超过最大用户数限制
    user_count = User.query.count()
    if user_count >= MAX_USERS:
        return "用户数已达到最大值，无法再注册新用户！"

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            return "用户名已存在"
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录路由
    处理用户登录表单的显示和提交
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        return "用户名或密码错误"
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """用户登出路由
    处理用户登出请求
    """
    logout_user()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """搜索文章路由
    根据标题关键词搜索文章
    """
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    results = Post.query.filter(Post.title.contains(query)).order_by(Post.created_at.desc()).all()
    return render_template('search.html', results=results, query=query)


# 应用入口
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建所有数据库表
    app.run(debug=True)  # 以调试模式运行应用