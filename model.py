from flask import Flask, url_for, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import bcrypt
import random

app = Flask(__name__)

# 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名jianshu,连接方式参考 \
#  http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost:3306/data?charset=utf8'
# 设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 实例化
db = SQLAlchemy(app)


class user(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(128), primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128), nullable=False)
    register_on = db.Column(db.DateTime, nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=0)
    gender = db.Column(db.Boolean, nullable=False, default=True)
    signature = db.Column(db.String(128), nullable=True, default="这个人很懒，什么也没说~")

    def __init__(self, email, username, password, permission):
        self.email = email
        self.username = username
        self.password = password  # 这里回头可以找方法进行加密
        self.permission = permission
        self.register_on = datetime.now()

    def __repr__(self):
        return '<user %r>' % self.username


class login(db.Model):
    __tablename__ = 'login'
    email = db.Column(db.String(128), primary_key=True)
    log_time = db.Column(db.DateTime, primary_key=True)

    # 浏览器和ip

    def __init__(self, email):
        self.email = email
        self.log_time = datetime.now()


class mailconfirm(db.Model):
    __tablename__ = 'mailconfirm'
    email = db.Column(db.String(128), primary_key=True)
    num = db.Column(db.String(30), nullable=False)
    invalid = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, num):
        self.email = email
        self.num = num
        self.invalid = datetime.now() + timedelta(minutes=5)


class methoduse(db.Model):
    __tablename__ = 'methoduse'
    email = db.Column(db.String(128), primary_key=True)
    use_time = db.Column(db.DateTime, primary_key=True)
    module = db.Column(db.String(128), nullable=False)
    method = db.Column(db.String(128), nullable=False)

    def __init__(self, email, module, method):
        self.email = email
        self.module = module
        self.use_time = datetime.now()
        self.method = method


# 映射到数据库中
db.create_all()
