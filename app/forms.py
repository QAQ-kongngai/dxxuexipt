from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import TextAreaField, DateTimeField, FileField
from flask_wtf.file import FileAllowed

class TaskForm(FlaskForm):
    title = StringField('任务标题', validators=[DataRequired()])
    description = TextAreaField('任务描述')
    deadline = DateTimeField('截止时间 (格式: YYYY-MM-DD HH:MM:SS)', format='%Y-%m-%d %H:%M:%S')
    attachment = FileField('附件上传', validators=[FileAllowed(['pdf', 'doc', 'docx', 'zip', 'txt'])])
    submit = SubmitField('发布任务')

class SubmissionForm(FlaskForm):
    file = FileField('上传作业文件', validators=[DataRequired(), FileAllowed(['pdf', 'docx', 'zip', 'txt'])])
    submit = SubmitField('提交作业')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(3, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(6, 128)])
    confirm = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

class AnnouncementForm(FlaskForm):
    title = StringField('公告标题', validators=[DataRequired()])
    content = TextAreaField('公告内容', validators=[DataRequired()])
    submit = SubmitField('发布公告')