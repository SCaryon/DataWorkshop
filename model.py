from datetime import datetime, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # 转换密码用到的库

app = Flask(__name__)

# 这里登陆的是root用户，要填上自己的密码，MySQL的默认端口是3306，填上之前创建的数据库名jianshu,连接方式参考 \
#  http://docs.sqlalchemy.org/en/latest/dialects/mysql.html
# qYA2iIFnIJScti3s
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:qazxswedcvfr@localhost:3306/data?charset=utf8'
# 设置这一项是每次请求结束后都会自动提交数据库中的变动
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# 实例化
db = SQLAlchemy(app)


class user(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(128), primary_key=True)
    id = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    register_on = db.Column(db.DateTime, nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=0)
    gender = db.Column(db.Boolean, nullable=False, default=True)
    signature = db.Column(db.String(128), nullable=True, default="This guy is too lazy~")

    def __init__(self, email, username, password, permission):
        self.email = email
        self.username = username
        # 对password做10轮的加密，获得了加密之后的字符串hashed，
        self.password_hash = generate_password_hash(password)
        self.permission = permission
        self.register_on = datetime.now()

    def __repr__(self):
        return '<user %r>' % self.username

    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        print(self.password_hash)
        return check_password_hash(self.password_hash, password)


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
