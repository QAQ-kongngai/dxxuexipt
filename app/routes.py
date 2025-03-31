from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Task, Submission, Announcement
from app.forms import LoginForm, RegisterForm, TaskForm, SubmissionForm, AnnouncementForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

bp = Blueprint('main', __name__)

# 首页 - 控制面板
@bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('用户名或密码错误')
    return render_template('login.html', form=form)

# 注册
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录。')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# 注销
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# 教师发布任务
@bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.role != 'admin':
        flash('只有管理员可以发布任务')
        return redirect(url_for('main.dashboard'))

    form = TaskForm()
    if form.validate_on_submit():
        filename = None
        if form.attachment.data:
            filename = secure_filename(form.attachment.data.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.attachment.data.save(save_path)

        task = Task(
            title=form.title.data,
            description=form.description.data,
            deadline=form.deadline.data,
        )
        db.session.add(task)
        db.session.commit()
        flash('任务发布成功！')
        return redirect(url_for('main.list_tasks'))

    return render_template('create_task.html', form=form)

# 任务列表
@bp.route('/tasks')
@login_required
def list_tasks():
    tasks = Task.query.order_by(Task.deadline.desc()).all()
    return render_template('task_list.html', tasks=tasks)

# 学生提交作业
@bp.route('/tasks/<int:task_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = SubmissionForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)

        # 自动重命名：任务名_用户名_时间戳.扩展名
        ext = os.path.splitext(filename)[1]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{task.title}_{current_user.username}_{timestamp}{ext}"

        # 分类保存路径：uploads/任务名/
        task_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], task.title)
        os.makedirs(task_folder, exist_ok=True)
        save_path = os.path.join(task_folder, new_filename)
        file.save(save_path)

        # 记录数据库
        submission = Submission(
            user_id=current_user.id,
            task_id=task.id,
            filename=new_filename
        )
        db.session.add(submission)
        db.session.commit()
        flash('作业提交成功！')
        return redirect(url_for('main.list_tasks'))

    return render_template('submit_task.html', task=task, form=form)

# 教师查看提交记录
@bp.route('/tasks/<int:task_id>/submissions')
@login_required
def view_submissions(task_id):
    if current_user.role != 'admin':
        flash('只有管理员可以查看提交记录')
        return redirect(url_for('main.dashboard'))

    task = Task.query.get_or_404(task_id)
    submissions = Submission.query.filter_by(task_id=task.id).order_by(Submission.timestamp.desc()).all()

    return render_template('view_submissions.html', task=task, submissions=submissions)

# ✅ 教师发布公告
@bp.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    if current_user.role != 'admin':
        flash('只有管理员可以发布公告')
        return redirect(url_for('main.dashboard'))

    form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(title=form.title.data, content=form.content.data)
        db.session.add(announcement)
        db.session.commit()
        flash('公告发布成功！')
        return redirect(url_for('main.list_announcements'))
    
    return render_template('create_announcement.html', form=form)

# 公告列表
@bp.route('/announcements')
@login_required
def list_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('announcement_list.html', announcements=announcements)
