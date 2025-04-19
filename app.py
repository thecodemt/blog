from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Post
from forms import PostForm
from flask import abort
import markdown
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from forms import LoginForm, RegisterForm
from flask import Markup


app = Flask(__name__)

# 基础配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于CSRF防护

# 初始化数据库
db.init_app(app)

@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown.markdown(text, extensions=['extra']))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 首页：展示文章列表
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# 文章详情页
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    if post is None:
        abort(404)
    
    # 使用 markdown 渲染内容为 HTML
    content_html = markdown.markdown(post.content, extensions=['fenced_code', 'codehilite'])

    return render_template('post_detail.html', post=post, content_html=content_html)

# 发表新文章
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html', form=form)


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm(obj=post)  # 用原内容初始化表单

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('edit.html', form=form, post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
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
    logout_user()
    return redirect(url_for('index'))

# 搜索文章标题
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    results = Post.query.filter(Post.title.contains(query)).order_by(Post.created_at.desc()).all()
    return render_template('search.html', results=results, query=query)


# 启动程序
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
