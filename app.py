import ast
import copy
import pandas as pd
import numpy as np
import csv
import os
from io import StringIO
import sys
import platform
import random
import shutil
import smtplib
from datetime import timedelta, datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pymysql
import codecs
from anomaly import AnonalyMethod
from cluster import ClusterWay, EvaluationWay
from projection import ProjectionWay
from regression import fitSLR
from statistics import Statistics
from model import user, methoduse, login, mailconfirm, db
from flask import Flask, request, json, render_template, session, jsonify, url_for, current_app, g, redirect
from xlrd import open_workbook
from werkzeug.utils import secure_filename
from api.new import new

from aip import AipOcr  # 引入百度api
import jieba
import wav2text  # wav转text的自定义py文件
from docx import Document

# 用于执行病毒查杀
import pyclamd
# 连接百度服务器的密钥
APP_ID = '14658891'
API_KEY = 'zWn97gcDqF9MiFIDOeKVWl04'
SECRET_KEY = 'EEGvCjpzTtWRO3GIxqz94NLz99YSBIT9'
# 连接百度服务器
# 输入三个密钥，返回服务器对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

app = Flask(__name__)
app.register_blueprint(new)
# app.run('127.0.0.1', debug=True, port=5000, ssl_context=('D:\OpenSSL-Win64\bin\server.crt', 'D:\OpenSSL-Win64\bin\server.key'))
# 用于加密，作为盐混在原始的字符串中，然后用加密算法进行加密
app.config['SECRET_KEY'] = os.urandom(24)
# 设定session的保存时间，当session.permanent=True的时候
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

#ksw now

@app.route('/')
@app.route('/index')
def index():
    g.count = 0
    session['cluster_method'] = 'KMeans'
    session['embedding_method'] = 'Principal_Component_Analysis'
    session['visualization_method'] = 'Radviz'
    session['cluster_parameters'] = {}
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        print(user1)
        return render_template('datagoo_homepage.html', user=user1)
    else:
        return render_template('datagoo_homepage.html')


@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    return render_template('user/login.html')


# 验证密码
@app.route('/login/pass/', methods=['GET', 'POST'])
def login_pass():
    # 添加数据到session中
    data = request.get_json('data')
    email = data['email']
    pas = data['password']
    theuser = user.query.filter_by(email=email).first()
    if theuser is None:
        return "account not exist"
    elif not theuser.check_password_hash(pas):
        return "password not right"
    else:
        session['email'] = email
        session['user_id'] = theuser.id
        session.permanent = True
        login1 = login(email=email)
        db.session.add(login1)
        db.session.commit()

        if session.get("last_page"):
            print(session.get("last_page"))
            page = session.get("last_page")
            return page
        else:
            return '/'


@app.route('/login/pass/name/', methods=['GET', 'POST'])
def login_pass_name():
    name = request.get_json()['name']
    user1 = user.query.filter_by(username=name).first()
    if user1 is not None:
        return "true"
    else:
        return "false"


# 发送邮件
def sendmail(to_mail, num):
    # 邮件外主体
    smtp = ''
    smtpserver = "smtp.qq.com"
    smtpport = 465
    from_mail = "1361377791@qq.com"
    password = "ejpulrvmshuyibba"
    # 邮件内容主体
    subject = "激活您的DaGoo账户"
    from_name = "DaGoo"
    body = num + "\n以上是您的验证码，请在五分钟内填写。如非本人操作，请忽略此邮件。\n" \
                 "Here is your verification code, please fill in within five minutes. " \
                 "Ignore this message if it is not my operation.\n"
    msgtext = MIMEText(body, "plain", "utf-8")
    msg = MIMEMultipart()
    msg['Subject'] = Header(subject, "utf-8")
    msg["From"] = Header(from_name + "<" + from_mail + ">", "utf-8")
    msg["To"] = to_mail
    msg.attach(msgtext)
    try:
        smtp = smtplib.SMTP_SSL(smtpserver, smtpport)
        # smtp.starttls()
        smtp.login(from_mail, password)
        smtp.sendmail(from_mail, to_mail, msg.as_string())
        smtp.quit()
        return True
    except Exception as e:
        print(e)
        smtp.quit()
        return False


def mycopyfile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        return False
    else:
        fpath, fname = os.path.split(dstfile)
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        shutil.copyfile(srcfile, dstfile)
        print("copy %s->%s" % (srcfile, dstfile))


# 前台传过来的数据都是已经被验证好格式的，传到后台以后只需要进行数据库的比对即可
# 需要验证的内容为：数据库中是否已经存在该用户。如果存在，那么弹出提示信息
# 新建一个用户需要完成的内容有：
# 给该用户的邮箱发送邮件；为该用户在服务器新增一个个人文件夹存储个人信息
# 由于涉及到文件的路径，管理起来有点麻烦所以暂时先不考虑
@app.route('/login/signup/', methods=['GET', 'POST'])
def login_signup():
    data = request.get_json('data')
    email = data['email']
    cur_dir = "./static/user"
    if os.path.isdir(cur_dir):
        os.makedirs('./static/user/' + email)
        cur_dir = cur_dir + "/" + email
        print(cur_dir, "/img")
        os.makedirs(cur_dir + "/img")
        os.makedirs(cur_dir + "/code")
        os.makedirs(cur_dir + "/report")
        os.makedirs(cur_dir + "/data")
        cur_dir = cur_dir + "/code"
        os.makedirs(cur_dir + "/Clean")
        os.makedirs(cur_dir + "/Statistic")
        os.makedirs(cur_dir + "/Mining")
        os.makedirs(cur_dir + "/Visualiztion")
        srcfile = 'static/user/service/img/user_img.jpg'
        dstfiel = 'static/user/' + email + '/img/user_img.jpg'
        mycopyfile(srcfile, dstfiel)
    else:
        return "error"
    verify = data['verify']
    confirm1 = mailconfirm.search(email, verify)
    if confirm1 is not None:  # 首先看验证码是否正确
        theuser = user.query.filter_by(email=email).first()
        if theuser is not None:  # 然后看用户是否存在
            return "email already exist"
        name = data['username']
        pas = data['password']
        typ = data['tp']  # 以数字的形式存储用户权限级别
        if typ == 'Primary VIP':
            typ = 1
        elif typ == 'Intermediate VIP':
            typ = 2
        elif typ == 'Senior VIP':
            typ = 3
        else:
            typ = 0
        user1 = user(email=email, username=name, password=pas, permission=typ)
        db.session.add(user1)
        db.session.delete(confirm1)
        db.session.commit()
        session['email'] = email
        session.permanent = True
        return "success"
    else:  # 验证码不正确或者已经过期
        return "Verification code error"


# 发送验证码并将验证码存到数据库
@app.route('/login/verify/', methods=['GET', 'POST'])
def login_verify():
    data = request.get_json('data')
    email = data['email']
    num = str(random.randint(1000, 9999))
    send = sendmail(email, num)
    if send:
        confirm1 = mailconfirm.query.filter_by(email=email).first()
        if confirm1 is not None:
            confirm1.num = num
            confirm1.invalid = datetime.now() + timedelta(minutes=5)
        else:
            conf1 = mailconfirm(email=email, num=num)
            db.session.add(conf1)
        db.session.commit()
        return "success"
    else:
        return "fail to send the mail"


# 验证验证码，过期或者成功都删除这个验证码
@app.route('/forget/verify/', methods=['GET', 'POST'])
def forget_verify():
    data = request.get_json('data')
    email = data['email']
    verify = data['verify']
    confirm1 = mailconfirm.query.filter_by(email=email, num=verify).first()
    if confirm1 is not None:
        db.session.delete(confirm1)
        db.session.commit()
        if confirm1.invalid > datetime.now():
            print("session deleted.")
            return "success"
        else:
            return "false"
    else:
        return "false"


@app.route('/forget/change/', methods=['GET', 'POST'])
def forget_change():
    data = request.get_json('data')
    email = data['email']
    password = data['password']
    print("email")
    user1 = user.query.filter_by(email=email).first()
    if user1 is not None:
        user1.password(password)
        db.session.commit()
        return "success"
    else:
        return "false"


@app.route('/user/')
def user_user():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is not None:
            email = user1.email
            cur_dir = './static/user/' + email
            print(cur_dir)
            if os.path.exists(cur_dir):
                return render_template('user/user.html', user=user1)
            else:
                return "Unknown error"

        else:
            return "404 NOT FOUND"
    return render_template('user/login.html')


# 下一步，需要将用户的头像进行压缩
@app.route('/user/change/', methods=['GET', 'POST'])
def user_change():
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')
    gender = request.form.get('gender')
    signature = request.form.get('signature')
    user1 = user.query.filter_by(email=email).first()
    if user1 is not None:
        user1.username = name
        user1.password(password)
        if gender == 'male':
            user1.gender = True
        else:
            user1.gender = False
        user1.signature = signature
        db.session.commit()
        return "success"
    else:
        return "false"


@app.route('/user/change/img/', methods=['GET', 'POST'])
def user_change_img():
    file = request.files['file']
    if file and '.' in file.filename:
        file_types = ['jpg','jpeg','png','pdf']
        this_type = file.filename.rsplit('.', 1)[1]
        for file_type in file_types:
            old_file = 'static/user/' + session.get('email') + '/img/user_img.'+file_type
            if os.path.exists(old_file):
                os.remove(old_file)
        if this_type in file_types:
            old_file = 'static/user/' + session.get('email') + '/img/user_img.jpg'
            file.save(old_file)
            return 'success'
    else:
        return "filename invalid or network error"


@app.route('/products', methods=['POST', 'GET'])
def products():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('products.html', user=user1)
    else:
        return render_template('products.html')


@app.route('/contact_us', methods=['POST', 'GET'])
def contact_us():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('contact_us.html', user=user1)
    else:
        return render_template('contact_us.html')


@app.route('/about_us', methods=['POST', 'GET'])
def about_us():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('about_us.html', user=user1)
    else:
        return render_template('about_us.html')


@app.route('/gallery/', methods=['POST', 'GET'])
def gallery():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('gallery.html', user=user1)
    else:
        return render_template('gallery.html')


@app.route('/master/', methods=['POST', 'GET'])
def master():
    return render_template('geogoo/master_change.html')


@app.route('/masterpoint/', methods=['POST', 'GET'])
def masterpoint():
    return render_template('geogoo/masterpoint.html')


# 地图方法begin

# In short, this method is to store the data uploaded by
# the user into the database and process it, and then transfer
# it to the user's own folder.
def file2db2json(file, jsonfile):
    bk = open_workbook(file, encoding_override="utf-8")
    try:
        sh_export = bk.sheet_by_name("countries")
        sh_product = bk.sheet_by_name("products")
        sh_cate = bk.sheet_by_name('categories')
    except:
        return "no such sheet!"
    else:
        # Create a temporary database link, then create a new temporary table, drop it after use.
        # I don’t need db.session, it’s too hard to use.
        # Here to explain, each user has their own database table, are used
        # to temporarily store data and calculate, so you can drop at any time
        email = session.get('user_id')
        print(email)
        dbcur = pymysql.connect(host="localhost", user='root', password='qazxswedcvfr', database='data')
        cursor = dbcur.cursor()
        sql = "drop table if exists export%s" % email
        cursor.execute(sql)
        sql = "drop table if exists product%s" % email
        cursor.execute(sql)
        sql = "drop table if exists category%s" % email
        cursor.execute(sql)
        sql = "drop table if exists country_pro%s" % email
        cursor.execute(sql)
        sql = "drop table if exists country%s" % email
        cursor.execute(sql)
        sql = "create table export%s (fromISO varchar(128),toISO varchar(128),product varchar(128)," \
              "year INT ,Quantity FLOAT, primary key(fromISO,toISO,product,year))" % email
        cursor.execute(sql)
        sql = "create table category%s (color varchar(128),cateID INT ,name varchar(128),total int default 0" \
              ",primary key (color))" % email
        cursor.execute(sql)
        sql = "create table product%s(products varchar(128),name varchar(128),color varchar(128)," \
              "proID int,sale float default 0,primary key(products))" % email
        cursor.execute(sql)
        sql = "create table country_pro%s(fromISO varchar(128),product varchar(128),sale float," \
              "primary key(fromISO,product))" % email
        cursor.execute(sql)
        sql = "create table country%s(fromISO varchar(128),export double , primary key(fromISO))" % email
        cursor.execute(sql)
        # values = []
        nrows = sh_export.nrows
        for i in range(0, nrows):
            row_data = sh_export.row_values(i)
            row = (row_data[0], row_data[1], row_data[2], row_data[3], row_data[4])
            # values.append(row)
            sql = "insert into export%s" % email + " values('%s','%s',%d, %d, %f)" % row
            cursor.execute(sql)
        sql = "insert into country_pro%s " \
              "select fromISO,product,sum(Quantity) from export%s group by fromISO,product" % (email, email)
        cursor.execute(sql)
        sql = "insert into country%s " \
              "select fromISO,sum(Quantity) from export%s group by fromISO" % (email, email)
        cursor.execute(sql)

        # print(sql)
        # print(values)
        dbcur.commit()

        # values = []
        nrows = sh_product.nrows
        for i in range(0, nrows):
            row_data = sh_product.row_values(i)
            row = (row_data[0], row_data[1], row_data[2], row_data[3])
            # values.append(row)
            sql = "insert into product%s(products,name,color,proID)" % email + " values(%d,'%s','%s',%d)" % row
            cursor.execute(sql)
        cursor.execute("select product,sum(Quantity) from export%s group by product" % email)
        result = cursor.fetchall()
        # print(result)
        for row in result:
            pro = row[0]
            sa = row[1]
            # print("update product%s set sale=%f where products=%s" % (email, sa, pro))
            cursor.execute("update product%s set sale=%f where products=%s" % (email, sa, pro))
        dbcur.commit()

        # values = []
        nrows = sh_cate.nrows
        for i in range(0, nrows):
            row_data = sh_cate.row_values(i)
            row = (row_data[0], row_data[1], row_data[2], row_data[3])
            # values.append(row)
            sql = "insert into category%s" % email + " values('%s','%s','%s',%d)" % row
            cursor.execute(sql)
        dbcur.commit()

        with open(jsonfile, "r", encoding="UTF-8") as load_f:
            load_dict = json.load(load_f)
            # print(load_dict["countries"])
            # json.dumps(load_dict, ensure_ascii=False)

            all_particle = 0

            sql = "select * from country_pro%s" % email
            cursor.execute(sql)
            result = cursor.fetchall()
            particles = 0
            for row in result:
                particles += row[2]
            particles = int(particles)
            dollars = len(str(particles))
            dollars = pow(10, dollars - 5)
            session['dollars'] = dollars

            for key in load_dict["countries"]:
                load_dict["countries"][key]['products'] = {}
                country = key
                # print(country)
                sql = "select * from country_pro%s where fromISO='%s'" % (email, country)
                # print(sql)
                cursor.execute(sql)
                result = cursor.fetchall()
                particles = 0
                for row in result:
                    particles += row[2] / dollars
                    load_dict["countries"][key]['products'][row[1]] = row[2]
                load_dict["countries"][key]['particles'] = int(particles)
                all_particle += int(particles)

                sql = "select export from country%s where fromISO='%s'" % (email, country)
                cursor.execute(sql)
                result = cursor.fetchall()
                # print(result)
                for row in result:
                    load_dict["countries"][key]['exports'] = row[0]
            print(all_particle)

            load_dict["categories"] = {}
            sql = "select * from category%s" % email
            cursor.execute(sql)
            result = cursor.fetchall()

            for row in result:
                load_dict['categories'][row[0]] = {}
                load_dict['categories'][row[0]]['id'] = row[1]
                load_dict['categories'][row[0]]['active'] = True
                load_dict['categories'][row[0]]['name'] = row[2]
                load_dict['categories'][row[0]]['total'] = row[3]

            load_dict['products'] = {}
            sql = "select * from product%s" % email
            cursor.execute(sql)
            result = cursor.fetchall()

            for row in result:
                load_dict['products'][row[0]] = {}
                load_dict['products'][row[0]]['x'] = 0
                load_dict['products'][row[0]]['y'] = 0
                load_dict['products'][row[0]]['name'] = row[1]
                load_dict['products'][row[0]]['color'] = row[2]
                load_dict['products'][row[0]]['sales'] = row[4]
                load_dict['products'][row[0]]['id'] = row[3]
                load_dict['products'][row[0]]["atlasid"] = row[0]

            with codecs.open(jsonfile, "w", encoding="UTF-8") as f:
                json.dump(load_dict, f, ensure_ascii=False)

            print("加载入文件完成...")
            # print(load_dict["countries"])
            # print(i["products"])

        cursor.close()
        dbcur.close()
    return 'success'


def yearfile2db2json(file, jsonfile):
    bk = open_workbook(file, encoding_override="utf-8")
    try:
        sh_export = bk.sheet_by_name("countries")
        sh_product = bk.sheet_by_name("products")
        sh_cate = bk.sheet_by_name('categories')
    except:
        return "no such sheet!"
    else:
        # Create a temporary database link, then create a new temporary table, drop it after use.
        # I don’t need db.session, it’s too hard to use.
        # Here to explain, each user has their own database table, are used
        # to temporarily store data and calculate, so you can drop at any time
        email = 0
        dbcur = pymysql.connect(host="localhost", user='root', password='qazxswedcvfr', database='data')
        cursor = dbcur.cursor()
        sql = "drop table if exists export%s" % email
        cursor.execute(sql)
        sql = "drop table if exists product%s" % email
        cursor.execute(sql)
        sql = "drop table if exists category%s" % email
        cursor.execute(sql)
        sql = "drop table if exists country_pro%s" % email
        cursor.execute(sql)
        sql = "drop table if exists country%s" % email
        cursor.execute(sql)
        sql = "create table export%s (fromISO varchar(128),toISO varchar(128),product varchar(128)," \
              "year INT ,Quantity FLOAT, primary key(fromISO,toISO,product,year))" % email
        cursor.execute(sql)
        sql = "create table category%s (color varchar(128),cateID INT ,name varchar(128),year int,total int default 0" \
              ",primary key (color,year))" % email
        cursor.execute(sql)
        sql = "create table product%s(products varchar(128),name varchar(128),year int default 0,color varchar(128)," \
              "proID int,sale float default 0,primary key(products,year))" % email
        cursor.execute(sql)
        sql = "create table country_pro%s(fromISO varchar(128),product varchar(128),year int,sale float," \
              "primary key(fromISO,product,year))" % email
        cursor.execute(sql)
        sql = "create table country%s(fromISO varchar(128),year int,export double, primary key(fromISO,year))" % email
        cursor.execute(sql)
        # values = []
        nrows = sh_export.nrows
        for i in range(0, nrows):
            row_data = sh_export.row_values(i)
            row = (row_data[0], row_data[1], row_data[2], row_data[3], row_data[4])
            # values.append(row)
            sql = "insert into export%s" % email + " values('%s','%s',%d, %d, %f)" % row
            cursor.execute(sql)
        sql = "insert into country_pro%s " \
              "select fromISO,product,year,sum(Quantity) from export%s group by fromISO,product,year" % (email, email)
        cursor.execute(sql)
        sql = "insert into country%s " \
              "select fromISO,year,sum(Quantity) from export%s group by fromISO,year" % (email, email)
        cursor.execute(sql)

        dbcur.commit()

        # values = []
        nrows = sh_product.nrows
        for i in range(0, nrows):
            row_data = sh_product.row_values(i)
            row = (row_data[0], row_data[1], row_data[2], row_data[3])
            # values.append(row)
            for year in range(1985, 2012):
                sql = "insert into product%s(products,name,color,proID,year)" % email + \
                      " values(%d,'%s','%s',%d,%d)" % (row_data[0], row_data[1], row_data[2], row_data[3], year)
                cursor.execute(sql)
        cursor.execute("select product,year,sum(Quantity) from export%s group by product,year" % email)
        result = cursor.fetchall()
        # print(result)
        for row in result:
            pro = row[0]
            ye = row[1]
            sa = row[2]
            # print("update product%s set sale=%f where products=%s" % (email, sa, pro))
            cursor.execute("update product%s set sale=%f where products=%s and year=%d" % (email, sa, pro, ye))
        dbcur.commit()
        cursor.execute('delete from product0 where sale=0')

        # values = []
        nrows = sh_cate.nrows
        for i in range(0, nrows):
            row_data = sh_cate.row_values(i)
            # values.append(row)
            for year in range(1985, 2012):
                row = (row_data[0], row_data[1], row_data[2], year, 0)
                sql = "insert into category0(color,cateID,name,year,total) values('%s','%s','%s',%d,%d)" % row
                cursor.execute(sql)
        dbcur.commit()
        cursor.execute('select year,color,count(*) from product0 group by year,color ')
        result = cursor.fetchall()
        for row in result:
            cursor.execute("update category0 set total=%d where color='%s' and year=%d" % (row[2], row[1], row[0]))
        cursor.execute('delete from category0 where total=0')
        dbcur.commit()

        for i in range(1985, 2012):
            with open(jsonfile, "r", encoding="UTF-8") as load_f:
                load_dict = json.load(load_f)

                all_particle = 0
                dollars = 120

                for key in load_dict["countries"]:
                    load_dict["countries"][key]['products'] = {}
                    country = key
                    # print(country)
                    sql = "select * from country_pro%s where fromISO='%s' and year=%d" % (email, country, i)
                    # print(sql)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    particles = 0
                    for row in result:
                        particles += row[3] / dollars
                        load_dict["countries"][key]['products'][row[1]] = row[3]
                    load_dict["countries"][key]['particles'] = int(particles)
                    all_particle += int(particles)

                    sql = "select export from country%s where fromISO='%s' and year = %d" % (email, country, i)
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for row in result:
                        load_dict["countries"][key]['exports'] = row[0]
                print(all_particle)

                load_dict["categories"] = {}
                sql = "select * from category%s where year = %d" % (email, i)
                cursor.execute(sql)
                result = cursor.fetchall()

                for row in result:
                    load_dict['categories'][row[0]] = {}
                    load_dict['categories'][row[0]]['id'] = row[1]
                    load_dict['categories'][row[0]]['active'] = True
                    load_dict['categories'][row[0]]['name'] = row[2]
                    load_dict['categories'][row[0]]['total'] = row[4]

                load_dict['products'] = {}
                sql = "select * from product%s where year=%d" % (email, i)
                cursor.execute(sql)
                result = cursor.fetchall()

                for row in result:
                    load_dict['products'][row[0]] = {}
                    load_dict['products'][row[0]]['x'] = 0
                    load_dict['products'][row[0]]['y'] = 0
                    load_dict['products'][row[0]]['name'] = row[1]
                    load_dict['products'][row[0]]['color'] = row[3]
                    load_dict['products'][row[0]]['sales'] = row[5]
                    load_dict['products'][row[0]]['id'] = row[4]
                    load_dict['products'][row[0]]["atlasid"] = row[0]

                with codecs.open("./static/data/master/year/countries%d.json" % i, "w", encoding="UTF-8") as f:
                    json.dump(load_dict, f, ensure_ascii=False)

                # with codecs.open(jsonfile, "w", encoding="UTF-8") as f:
                #     json.dump(load_dict, f, ensure_ascii=False)
                print("加载入文件完成...")
                # print(load_dict["countries"])
                # print(i["products"])

        cursor.close()
        dbcur.close()
    return 'success'


@app.route("/geo/thisis/", methods=['GET', 'POST'])
def geo_thisis():
    if not os.path.exists("./static/user/service/data/countries.json"):
        shutil.copy("./static/data/geogoo/countries.json",
                    "./static/user/service/data/countries.json")
    path = "./static/user/service/data/"
    if yearfile2db2json(path + "countries.xlsx", path + 'countries.json') == "no such sheet!":
        return "no such sheet!"
    else:
        return render_template('geogoo/master.html')


# 进入地图的index界面
@app.route('/geo/', methods=['GET', 'POST'])
def geo_index():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('geogoo/geogoo_homepage.html', user=user1)
    else:
        return render_template('geogoo/geogoo_homepage.html')


# the first four geo models
@app.route('/geo/<id>/', methods=['GET', 'POST'])
def geo_id(id):
    id = id.replace('<', '')
    id = id.replace('>', '')
    if not session.get('email'):
        return render_template("geogoo/geo_%s.html" % id)
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/countries.json") and session.get('dollars'):
            return render_template("geogoo/geo_%s.html" % id, dollars=session.get('dollars'),
                                   data="/static/user/" + email + "/data/countries.json")
        else:
            return render_template("geogoo/geo_%s.html" % id)


# the upload method for the first four geo method
@app.route('/geo/<id>/upload/', methods=['GET', 'POST'])
def geo_plane_upload(id):
    id = id.replace('<', '')
    id = id.replace('>', '')
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if request.method == 'POST':
                if not os.path.exists("./static/user/" + email + "/data/countries.json"):
                    shutil.copy("./static/data/geogoo/countries.json",
                                "./static/user/" + email + "/data/countries.json")
                path = "./static/user/" + email + "/data/"
                filedata = request.files['file']
                if filedata:
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(path + "countries.xlsx"):
                        os.remove(path + "countries.xlsx")
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return '上传文件失败'
                    os.rename(path + filedata.filename, path + "countries.xlsx")
                    if file2db2json(path + "countries.xlsx", path + 'countries.json') == "no such sheet!":
                        return "no such sheet!"
                else:
                    return "filename invalid or network error"
            print("/static/user/" + email + "/data/countries.json")
            return redirect('/geo/<%s>/' % id)
    else:
        session["last_page"] = "/geo/<%s>" % id
        return render_template('user/login.html')


def read_geo_admin_csv(filename):
    final_data = csv.reader(open(filename))
    province = []
    data = []
    for i in final_data:
        province.append(i[0])
        del i[0]
        data.append(i)
    attr = data[0]
    del province[0]
    del data[0]
    final_data_object = {}
    final_data_object['province'] = province
    final_data_object['data'] = data
    final_data_object['attr'] = attr
    return final_data_object


# 行政热力图
@app.route('/geo/admin/', methods=['GET', 'POST'])
def geo_admin():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if os.path.exists("./static/user/" + email + "/data/geo_admin.csv"):
                final_data_object = read_geo_admin_csv("./static/user/" + email + "/data/geo_admin.csv")
                return render_template("geogoo/geo_admin.html", user=user1, attr=final_data_object['attr'])
            else:
                final_data_object = read_geo_admin_csv('./examples/geo/dist_code.csv')
                return render_template('geogoo/geo_admin.html', attr=final_data_object['attr'])
    else:  # 读取默认的数据
        final_data_object = read_geo_admin_csv('./examples/geo/dist_code.csv')
        return render_template('geogoo/geo_admin.html', attr=final_data_object['attr'])


# 读取用户上传的行政区数据
@app.route('/geo/admin/upload/', methods=['GET', 'POST'])
def geo_admin_upload():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if request.method == 'POST':
                path = "./static/user/" + email + "/data/"
                filedata = request.files['file']
                if filedata:
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(path + "geo_admin.csv"):
                        os.remove(path + "geo_admin.csv")
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return '上传文件失败'
                    os.rename(path + filedata.filename, path + "geo_admin.csv")
                else:
                    return "filename invalid or network error"
            return redirect(url_for('geo_admin'))
    else:
        session["last_page"] = "/geo/admin/"
        return render_template('user/login.html')


# 向前端传递后台的地理信息数据
@app.route('/geo/get/', methods=['GET', 'POST'])
def geo_get():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if os.path.exists("./static/user/" + email + "/data/geo_admin.csv"):
                final_data_object = read_geo_admin_csv("./static/user/" + email + "/data/geo_admin.csv")
                return jsonify(final_data_object)
            else:
                final_data_object = read_geo_admin_csv('./examples/geo/dist_code.csv')
                return jsonify(final_data_object)
    else:  # 读取默认的数据
        final_data_object = read_geo_admin_csv('./examples/geo/dist_code.csv')
        return jsonify(final_data_object)


# 海量点分布
@app.route('/geo/points/', methods=['GET', 'POST'])
def geo_points():
    final_data = csv.reader(open('./examples/geo/geo_points.csv'))
    point = []
    for i in final_data:
        dic = dict(zip(['longitude', 'latitude', 'value', 'name'], i))
        point.append(dic)
    final_data_object = {}
    final_data_object['points'] = point
    return render_template('geogoo/geo_points.html')


@app.route('/geo/get/points/', methods=['GET', 'POST'])
def geo_get_points():
    final_data = csv.reader(open('./examples/geo/geo_points.csv'))
    point = []
    for i in final_data:
        dic = dict(zip(['longitude', 'latitude', 'value', 'name'], i))
        point.append(dic)
    final_data_object = {}
    final_data_object['points'] = point
    return jsonify(final_data_object)


@app.route('/geo/line/', methods=['GET', 'POST'])
def geo_line():
    return render_template('geogoo/geo_line.html')


@app.route("/graph/<id>")
def graph_id(id):
    id = id.replace('<', '')
    id = id.replace('>', '')
    return render_template('graphgoo/product/%s.html' % id)


@app.route('/alert')
def alert():
    if session.get('email'):
        email = session.get('email')
        last_page = session.get('last_page')
        return redirect(last_page)
    else:
        return redirect('/login/')


def read_graph_data(filename):
    temp_data = pd.read_csv(filename, encoding='gbk')
    graph_nodes = temp_data.columns
    graph_nodes = graph_nodes.tolist()
    graph_matrix = np.array(temp_data).tolist()
    del graph_nodes[0]
    if not graph_nodes[-1]:
        del graph_nodes[-1]
    for temp_list in range(len(graph_nodes)):
        del graph_matrix[temp_list][0]
    return graph_nodes, graph_matrix


def check_graph_data(nodes, matrix):
    matrix = np.array(matrix)
    try:
        rows, columns = matrix.shape
        if rows != columns:
            return False
        if len(nodes) != rows:
            return False
    except:
        return False
    else:
        return True


@app.route('/graphgoo', methods=['POST', 'GET'])
def graphgoo():
    if not session.get('email'):
        graph_nodes, graph_matrix = read_graph_data('./examples/graph/graph.csv')
        return render_template('graphgoo/graphgoo_homepage.html', nodes=graph_nodes, matrix=graph_matrix)
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            graph_nodes, graph_matrix = read_graph_data("./static/user/" + email + "/data/graph.csv")
            return render_template('graphgoo/graphgoo_homepage.html', nodes=graph_nodes, matrix=graph_matrix)
        else:
            graph_nodes, graph_matrix = read_graph_data('./examples/graph/graph.csv')
            return render_template('graphgoo/graphgoo_homepage.html', nodes=graph_nodes, matrix=graph_matrix)


@app.route('/graph_upload', methods=['POST', 'GET'])
def graph_upload():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if request.method == 'POST':
                path = "./static/user/" + email + "/data/"
                filedata = request.files['file']
                if filedata:
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(path + "graph.csv"):
                        os.remove(path + "graph.csv")
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return '上传文件失败'
                    os.rename(path + filedata.filename, path + "graph.csv")
                    graph_nodes, graph_matrix = read_graph_data(path + "graph.csv")
                    if not check_graph_data(graph_nodes, graph_matrix):
                        os.remove(path + "graph.csv")
                        session["last_page"] = '/graphgoo'
                        return render_template('data_error.html')
                else:
                    return "filename invalid or network error"
            return redirect(url_for('graphgoo'))
    else:
        session["last_page"] = '/graphgoo'
        return redirect(url_for('user_login'))


def data_list_to_dictionary(list_key, list_value):
    if len(list_key) != len(list_value):
        print("the keys and the values don't match")
        exit(0)
    dict = {}
    for i in range(len(list_key)):
        dict[list_key[i]] = list_value[i]
    return dict


def generate_table_data(table_id, table_fea, table_da, table_cluster_method, table_embedding_method, parameters):
    # table original data
    table_fea_fea_dic = []  # dictionary features for display
    table_fea_da_dic = []  # dictionary data for visual analysis
    table_id_fea_da_dic = []  # dictionary data for display
    table_fea_fea_dic.append(data_list_to_dictionary(table_fea, table_fea))
    for temp_list in table_da:
        table_fea_da_dic.append(data_list_to_dictionary(table_fea[1:], temp_list))
    table_id_da = []
    for i in range(len(table_id)):
        temp_list = []
        temp_list.append(table_id[i])
        for temp_item in table_da[i]:
            temp_list.append(temp_item)
        table_id_da.append(temp_list)
    for temp_list in table_id_da:
        table_id_fea_da_dic.append(data_list_to_dictionary(table_fea, temp_list))
    # table statistics data
    table_stt_da = { 'corr': []}
    stt = Statistics(table_da, table_fea[1:])
    table_stt_da['corr'] = stt.corr
    # table cluster and embedding data
    result = getattr(ClusterWay(), table_cluster_method)(parameters)
    clustering = result['clustering']
    labels = clustering.labels_.tolist()
    table_clusters = np.unique(labels).size
    embedding = getattr(ProjectionWay(), table_embedding_method)(table_da)
    samples, features = embedding['data'].shape
    data_embedding = embedding['data'].tolist()
    for i in range(samples):
        lll = labels[i]
        data_embedding[i].append(lll)
    table_clu_emb_da = data_embedding
    #  table anomaly detection data
    table_ano_de_da, table_ano_de_ind = AnonalyMethod.clfdetection(table_clu_emb_da)
    for i in range(len(table_ano_de_ind)):
        table_ano_de_da[i].append(table_ano_de_ind[i])
    return (table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da,
            table_stt_da, table_clu_emb_da, table_ano_de_da, table_clusters)


def generate_table_dic_data(table_id, table_da, table_fea):
    # table_id:current_app.config['TABLE_IDENTIFIERS']
    # table_da:current_app.config['TABLE_DATA']
    # table_fea:current_app.config['TABLE_FEATURES']
    table_id_da = []
    table_id_fea_da_dic = []
    for i in range(len(table_id)):
        temp_list = []
        temp_list.append(table_id[i])
        for temp_item in table_da[i]:
            temp_list.append(temp_item)
        table_id_da.append(temp_list)
    for temp_list in table_id_da:
        table_id_fea_da_dic.append(data_list_to_dictionary(table_fea, temp_list))
        return table_id_fea_da_dic


def read_table_data(filename):
    table_data = pd.read_csv(filename, encoding='gbk')
    table_features = table_data.columns
    table_features = table_features.tolist()
    table_data = np.array(table_data).tolist()
    table_identifiers = []
    for i in range(len(table_data)):
        table_identifiers.append(table_data[i][0])
        del table_data[i][0]
    return table_data, table_features, table_identifiers


def check_table_data(data_list):
    data_list = np.array(data_list)
    rows, columns = data_list.shape
    for i in range(rows):
        for j in range(columns):
            try:
                if np.isnan(data_list[i][j]):
                    return False
            except:
                return False
    return True


@app.route('/tablegoo', methods=['POST', 'GET'])
def tablegoo():
    if not session.get('email'):
        path = './examples/table/car.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/table.csv"):
            path = "./static/user/" + email + "/data/table.csv"
        else:
            path = './examples/table/car.csv'
    table_data, table_features, table_identifiers = read_table_data(path)
    table_cluster_method = session.get('cluster_method')
    table_embedding_method = session.get('embedding_method')
    table_visualization_method = session.get('visualization_method')
    parameters = session.get('cluster_parameters')
    parameters['data'] = table_data
    table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da, table_stt_da, table_clu_emb_da, table_ano_de_da, table_clusters = generate_table_data(
        table_identifiers, table_features, table_data, table_cluster_method, table_embedding_method, parameters)
    return render_template('tablegoo/tablegoo_homepage.html',
                            features_dictionary=table_fea_fea_dic,
                            no_identifiers_data_list=table_data,
                            no_identifiers_data_list_transform=np.transpose(table_data).tolist(),
                            no_identifiers_data_dictionary=table_fea_da_dic,
                            data_dictionary=table_id_fea_da_dic,
                            corr=table_stt_da['corr'],
                            features_list=table_features,
                            cluster_embedding_data=table_clu_emb_da,
                            n_clusters=table_clusters,
                            cluster_method=table_cluster_method,
                            embedding_method=table_embedding_method,
                            anomaly_detection_data=table_ano_de_da,
                            visualization_method=table_visualization_method)


@app.route('/table_upload', methods=['GET', 'POST'])
def table_upload():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if request.method == 'POST':
                path = "./static/user/" + email + "/data/"
                filedata = request.files['file']
                if filedata:
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(path + "table.csv"):
                        os.remove(path + "table.csv")
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return '上传文件失败'
                    os.rename(path + filedata.filename, path + "table.csv")
                    table_data, table_features, table_identifiers = read_table_data(
                        "./static/user/" + email + "/data/table.csv")
                    if not check_table_data(table_data):
                        os.remove(path + "table.csv")
                        session["last_page"] = '/tablegoo'
                        return render_template('data_error.html')
                else:
                    return "filename invalid or network error"
            return redirect(url_for('tablegoo'))
    else:
        session["last_page"] = '/tablegoo'
        return redirect(url_for('user_login'))


@app.route('/text_upload', methods=['GET', 'POST'])
def text_upload():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        else:
            if request.method == 'POST':
                path = "./static/user/" + email + "/data/"
                filedata = request.files['file']
                if filedata:
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(path + "text.csv"):
                        os.remove(path + "text.csv")
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return 'ä¸Šä¼ æ–‡ä»¶å¤±è´¥'
                    os.rename(path + filedata.filename, path + "text.csv")
                else:
                    return "filename invalid or network error"
            return redirect(url_for('textgoo'))
    else:
        session["last_page"] = '/textgoo'
        return redirect(url_for('user_login'))


@app.route('/clean', methods=['POST', 'GET'])
def clean():
    return render_template("clean.html")


@app.route('/clean_table', methods=['POST', 'GET'])
def clean_table():
    table_da, table_fea, table_id = read_table_data('./examples/table/car.csv')
    table_id_da = []
    for i in range(len(table_id)):
        temp_list = []
        temp_list.append(table_id[i])
        for temp_item in table_da[i]:
            temp_list.append(temp_item)
        table_id_da.append(temp_list)
    source_arr = np.mat(table_id_da)
    data_transform = source_arr.T
    data_list_transform = data_transform.tolist()
    return render_template("clean_table.html", data=table_id_da,
                           frame=table_fea, data_list=data_list_transform)


# streaming data start------------------------------------------------------
@app.route('/streaming_data', methods=['GET', 'POST'])
def streaming_data():
    email = session.get('email')
    user1 = user.query.filter_by(email=email).first()
    if user1 is not None:
        path = "./static/user/" + email + "/data/user_data.csv"
        if os.path.exists(path):
            os.remove(path)
        return render_template('streaminggoo/time.html', user=user1)
    else:
        return render_template('streaminggoo/time.html')


@app.route('/time_upload', methods=['GET', 'POST'])
def time_upload():
    email = session.get('email')
    user1 = user.query.filter_by(email=email).first()
    # if user1 is None:
    # print("please sign in")
    # return "please sign in"
    if session.get('email') and (request.method == 'POST'):
        path = "./static/user/" + email + "/data/user_data.csv"
        filedata = request.files['file']
        if filedata:
            if os.path.exists(path):
                os.remove(path)
            try:
                filedata.save(path)
            except IOError:
                return '上传文件失败'
        time_data_object = {}
        original_data = csv.reader(open("./static/user/" + email + "/data/user_data.csv"))
        features_list = []
        final_data = []
        length = 0
        for i in original_data:
            if length == 0:
                features_list = i
                del i
            else:
                final_data.append(i)
            length = length + 1

        for feature in features_list:
            time_data_object[feature] = []
        for i in range(len(final_data) - 1):
            if (len(final_data[i]) != len(final_data[i])):
                return 'error!exist none'
        for i in range(len(final_data)):
            if (len(final_data[i]) == 0):
                break
            if '' in final_data[i]:
                continue
            for j in range(len(final_data[i])):  # 对每一行都进行数据提取
                if features_list[j] == 'year':
                    time_data_object['year'].append(float(final_data[i][j]))
                else:
                    time_data_object[features_list[j]].append(float(final_data[i][j]))
        themeriver_data = []
        histogram_data = []
        for item in range(len(time_data_object['year'])):
            histogram_data_current = []
            year = time_data_object['year'][item]
            for feature in time_data_object.keys():
                feature_data = time_data_object[feature][item]
                histogram_data_current.append(feature_data)
                if feature != 'year':
                    data = [str(int(year)), feature_data, feature]
                    themeriver_data.append(data)
            histogram_data.append(histogram_data_current)
        themeriver = {}
        themeriver['data'] = themeriver_data
        themeriver_features = []
        features = time_data_object.keys()
        for feature in features:
            if feature != 'year':
                themeriver_features.append(feature)
        themeriver['features'] = themeriver_features
        themeriver['histogram_data'] = histogram_data
        return jsonify(themeriver)
    else:
        session["last_page"] = '/streaming_data'
        return jsonify('please sign in first')


@app.route('/streaming_data_fourier', methods=['GET', 'POST'])
def streamingdata_fourier():
    if session.get('email') and request.method == 'POST':
        user_path = "./static/user/" + session.get('email') + "/data/user_data.csv"
        if os.path.exists(user_path):
            path = user_path
        else:
            path = "./static/data/streaming_data/initial_streaming_data.csv"
    else:
        path = "./static/data/streaming_data/initial_streaming_data.csv"
    original_data = csv.reader(open(path))
    year = []
    attribution = []  # 创建一个包含30个点的余弦波信号
    length = 0
    year_location = 0
    attribution_location = 0
    for i in original_data:
        if length == 0:
            for f in range(len(i)):
                if i[f] == 'year':
                    year_location = f
                if i[f] == request.get_json()['attribution']:
                    attribution_location = f
        else:
            year.append(i[year_location])
            attribution.append(float(i[attribution_location]))
        length = length + 1
    wave = np.cos(attribution)
    transformed = np.fft.fft(wave)  # 使用fft函数对余弦波信号进行傅里叶变换。
    result = {}
    result['xdata'] = year
    result['ydata'] = []  # transformed.tolist()
    for i in transformed:
        result['ydata'].append(round(abs(i), 4))
    return jsonify(result)


@app.route('/time/ex/', methods=['POST', 'GET'])
def Exponential_smoothing():
    # global time_data_object

    if session.get('email') and request.method == 'POST':
        user_path = "./static/user/" + session.get('email') + "/data/user_data.csv"
        if os.path.exists(user_path):
            path = user_path
        else:
            path = "./static/data/streaming_data/initial_streaming_data.csv"
    else:
        path = "./static/data/streaming_data/initial_streaming_data.csv"
    original_data = csv.reader(open(path))
    year = []
    number = []  # 创建一个包含30个点的余弦波信号
    length = 0
    year_location = 0
    attribution_location = 0
    for i in original_data:
        if length == 0:
            for f in range(len(i)):
                if i[f] == 'year':
                    year_location = f
                if i[f] == request.get_json()['attribution']:
                    attribution_location = f
        else:
            year.append(int(i[year_location]))
            number.append(float(i[attribution_location]))
        length = length + 1
    alpha = .70  # 设置alphe，即平滑系数
    data = []
    for i in range(len(year)):
        data_i = [year[i], number[i]]
        data.append(data_i)
    for i in range(len(year)):
        abcyear = int(year[i])
    pre_year = np.array([abcyear + 1, abcyear + 2])  # 将需要预测的两年存入numpy的array对象里
    initial_line = np.array(
        [0, number[0]])  # 初始化，由于平滑指数是根据上一期的数值进行预测的，原始数据中的最早数据为1995，没有1994年的数据，这里定义1994年的数据和1995年数据相同
    initial_data = np.insert(data, 0, values=initial_line, axis=0)  # 插入初始化数据
    initial_year, initial_number = initial_data.T  # 插入初始化年
    s_single = np.zeros(initial_number.shape)
    s_single[0] = initial_number[0]
    for i in range(1, len(s_single)):
        s_single[i] = alpha * initial_number[i] + (1 - alpha) * s_single[i - 1]
    s_double = np.zeros(s_single.shape)
    s_double[0] = s_single[0]
    for i in range(1, len(s_double)):
        s_double[i] = alpha * s_single[i] + (1 - alpha) * s_double[
            i - 1]  # 计算二次平滑字数，二次平滑指数是在一次指数平滑的基础上进行的，三次指数平滑以此类推

    a_double = 2 * s_single - s_double  # 计算二次指数平滑的a
    b_double = (alpha / (1 - alpha)) * (s_single - s_double)  # 计算二次指数平滑的b
    s_pre_double = np.zeros(s_double.shape)  # 建立预测轴
    for i in range(1, len(initial_year)):
        s_pre_double[i] = a_double[i - 1] + b_double[i - 1]  # 循环计算每一年的二次指数平滑法的预测值，下面三次指数平滑法原理相同
    pre_next_year = a_double[-1] + b_double[-1] * 1  # 预测下一年
    pre_next_two_year = a_double[-1] + b_double[-1] * 2  # 预测下两年
    insert_year = np.array([pre_next_year, pre_next_two_year])
    s_pre_double = np.insert(s_pre_double, len(s_pre_double), values=np.array([pre_next_year, pre_next_two_year]),
                             axis=0)  # 组合预测值
    s_triple = np.zeros(s_double.shape)
    s_triple[0] = s_double[0]
    for i in range(1, len(s_triple)):
        s_triple[i] = alpha * s_double[i] + (1 - alpha) * s_triple[i - 1]

    a_triple = 3 * s_single - 3 * s_double + s_triple
    b_triple = (alpha / (2 * ((1 - alpha) ** 2))) * (
            (6 - 5 * alpha) * s_single - 2 * ((5 - 4 * alpha) * s_double) + (4 - 3 * alpha) * s_triple)
    c_triple = ((alpha ** 2) / (2 * ((1 - alpha) ** 2))) * (s_single - 2 * s_double + s_triple)

    s_pre_triple = np.zeros(s_triple.shape)

    for i in range(1, len(initial_year)):
        s_pre_triple[i] = a_triple[i - 1] + b_triple[i - 1] * 1 + c_triple[i - 1] * (1 ** 2)

    pre_next_year = a_triple[-1] + b_triple[-1] * 1 + c_triple[-1] * (1 ** 2)
    pre_next_two_year = a_triple[-1] + b_triple[-1] * 2 + c_triple[-1] * (2 ** 2)
    insert_year = np.array([pre_next_year, pre_next_two_year])
    s_pre_triple = np.insert(s_pre_triple, len(s_pre_triple), values=np.array([pre_next_year, pre_next_two_year]),
                             axis=0)

    new_year = np.insert(year, len(year), values=pre_year, axis=0)
    output = np.array([new_year, s_pre_double, s_pre_triple])
    result = []
    for a in range(1, len(new_year)):
        result.append(str(new_year[a]))
        result.append(str(s_pre_triple[a]))
    re_result = ':'.join(result)
    print(re_result)
    return re_result


@app.route('/time/ar/', methods=['POST', 'GET'])
def Arithmetic_averaging():
    if session.get('email') and request.method == 'POST':
        user_path = "./static/user/" + session.get('email') + "/data/user_data.csv"
        if os.path.exists(user_path):
            path = user_path
        else:
            path = "./static/data/streaming_data/initial_streaming_data.csv"
    else:
        path = "./static/data/streaming_data/initial_streaming_data.csv"
    original_data = csv.reader(open(path))
    year = []
    number = []  # 创建一个包含30个点的余弦波信号
    length = 0
    year_location = 0
    attribution_location = 0
    for i in original_data:
        if length == 0:
            for f in range(len(i)):
                if i[f] == 'year':
                    year_location = f
                if i[f] == request.get_json()['attribution']:
                    attribution_location = f
        else:
            year.append(int(i[year_location]))
            number.append(float(i[attribution_location]))
        length = length + 1
    data = []
    for i in range(len(year)):
        data_i = [year[i], number[i]]
        data.append(data_i)
    for i in range(len(year)):
        abcyear = year[i]
    number = np.array(number)
    pre_year = np.array([abcyear + 1, abcyear + 2])  # 将需要预测的两年存入numpy的array对象里
    s_single = np.zeros(number.shape)
    s_single[0] = number[0]
    for i in range(1, len(s_single)):
        s_single[i] = sum(number[:i]) / i
    # 计算一次平滑
    s_pre_single = np.zeros(s_single.shape)  # 建立预测轴
    pre_next_year = sum(number[:]) / len(number)  # 预测下一年
    pre_next_two_year = (sum(number[:]) + pre_next_year) / (len(number) + 1)  # 预测下两年
    insert_year = np.array([pre_next_year, pre_next_two_year])
    s_pre_single = np.insert(s_single, len(s_single), values=np.array([pre_next_year, pre_next_two_year]),
                             axis=0)  # 组合预测值
    new_year = np.insert(year, len(year), values=pre_year, axis=0)
    result = []
    for a in range(1, len(new_year)):
        result.append(str(new_year[a]))
        result.append(str(s_pre_single[a]))
    re_result = ':'.join(result)
    return re_result


def simplle_smoothing(s):
    s2 = np.zeros(s.shape)
    s2[0:5] = s[0:5]
    for i in range(5, len(s2)):
        s2[i] = sum(s[i - 5:i]) / 5
    return s2


@app.route('/time/mo/', methods=['POST', 'GET'])
def Moving_averaging():
    if session.get('email') and request.method == 'POST':
        user_path = "./static/user/" + session.get('email') + "/data/user_data.csv"
        if os.path.exists(user_path):
            path = user_path
        else:
            path = "./static/data/streaming_data/initial_streaming_data.csv"
    else:
        path = "./static/data/streaming_data/initial_streaming_data.csv"
    original_data = csv.reader(open(path))
    year = []
    number = []  # 创建一个包含30个点的余弦波信号
    length = 0
    year_location = 0
    attribution_location = 0
    for i in original_data:
        if length == 0:
            for f in range(len(i)):
                if i[f] == 'year':
                    year_location = f
                if i[f] == request.get_json()['attribution']:
                    attribution_location = f
        else:
            year.append(int(i[year_location]))
            number.append(float(i[attribution_location]))
        length = length + 1
    number = np.array(number)
    data = []
    for i in range(len(year)):
        data_i = [year[i], number[i]]
        data.append(data_i)
    for i in range(len(year)):
        abcyear = year[i]
    pre_year = np.array([abcyear + 1, abcyear + 2])  # 将需要预测的两年存入numpy的array对象里
    s_single = np.zeros(number.shape)
    s_single[0:5] = number[0:5]
    for i in range(5, len(s_single)):
        s_single[i] = sum(number[i - 5:i]) / 5
    # 计算一次平滑
    s_pre_single = np.zeros(s_single.shape)  # 建立预测轴
    yearnumbertotal = len(year)
    select = yearnumbertotal - 5
    select1 = yearnumbertotal - 4
    pre_next_year = sum(number[select:]) / 5  # 预测下一年
    pre_next_two_year = (sum(number[select1:]) + pre_next_year) / 5  # 预测下两年
    insert_year = np.array([pre_next_year, pre_next_two_year])
    s_pre_single = np.insert(s_single, len(s_single), values=np.array([pre_next_year, pre_next_two_year]),
                             axis=0)  # 组合预测值
    new_year = np.insert(year, len(year), values=pre_year, axis=0)
    result = []
    for a in range(1, len(new_year)):
        result.append(str(new_year[a]))
        result.append(str(s_pre_single[a]))
    re_result = ':'.join(result)
    return re_result


# streaming data end------------------------------------------------------


# cluster start------------------------------------------------------------
@app.route('/cluster')
def cluster():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('tablegoo/cluster_2.html', user=user1)
    else:
        return render_template('tablegoo/cluster_2.html')


@app.route('/cluster/cluster_way', methods=['POST', 'GET'])
def cluster_way():
    # run cluster way except user's way
    if session.get('email'):
        if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
            # run cluster way except user's way
            table_data, table_features, table_identifiers = read_table_data(
                "./static/user/" + session.get('email') + "/data/table.csv")
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    else:
        table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    no_identifiers_data_list = table_data
    parameters = {}
    draw_id = str(request.get_json()['draw_id'])
    body = 'page-top' + draw_id
    node_id = ['name' + draw_id, 'cluster' + draw_id, 'data_obj' + draw_id, 'method' + draw_id]
    if request.get_json()['exist'] != 'none':
        for key in request.get_json():
            if key != 'cluster_method':  # 要保证参数数组里面只有参数，没有方法名
                parameters[key] = request.get_json()[key]
    parameters['data'] = no_identifiers_data_list  # final_data_object['no_identifiers_data_list']  # 用户输入的数据csv

    cluster_method = request.get_json()['cluster_method']
    result = getattr(ClusterWay(), cluster_method)(parameters)
    clustering = result['clustering']
    if result.get('labels') is None:
        initial_labels = clustering.labels_
    else:
        initial_labels = result.get('labels')
    labels = initial_labels.tolist()
    clusters = np.unique(labels).size

    if session.get('embedding_method'):
        embedding_method = session.get('embedding_method')
    else:
        embedding_method = 'Principal_Component_Analysis'
    pca = getattr(ProjectionWay(), embedding_method)(no_identifiers_data_list)
    data_pca = pca['data']
    samples, features = data_pca.shape
    data_pca = data_pca.tolist()
    for i in range(samples):
        lll = labels[i]
        data_pca[i].append(lll)
    table_da_dic = generate_table_dic_data(table_identifiers, table_data, table_features)
    this_html = render_template("tablegoo/cluster.html", data=data_pca, data_obj=table_da_dic,
                                clusters=clusters,
                                method=cluster_method + draw_id, body_id=body, body_draw_id=node_id)
    return this_html


@app.route('/mining/cluster', methods=['POST', 'GET'])
def mining_cluster():
    parameters = {}
    for key in request.get_json():
        if key != 'Cluster method':  # 要保证参数数组里面只有参数，没有方法名
            parameters[key] = request.get_json()[key]
        else:
            session['cluster_method'] = request.get_json()[key]
    session['cluster_parameters'] = parameters
    return jsonify(True)


@app.route('/cluster/cluster_way_evaluation', methods=['POST', 'GET'])
def cluster_way_evaluation():  # 需要的参数是各个图所展示出来的聚类方法以及他们对应的参数
    # 返回的结果是聚类方法：聚类的评价值的键值对
    if session.get('email'):
        if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
            # run cluster way except user's way
            table_data, table_features, table_identifiers = read_table_data(
                "./static/user/" + session.get('email') + "/data/table.csv")
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    else:
        table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    result = []
    evaluation_way = request.get_json()[0]
    result.append(evaluation_way)
    for count in range(len(request.get_json())):
        if count == 0:
            continue
        cluster_way = request.get_json()[count]
        print(cluster_way)
        cluster_way['data'] = table_data
        print(cluster_way['Cluster method'])
        cluster_result = {}
        if cluster_way['Cluster method'] == 'User_cluster':
            target_url = os.path.join("./static/user/" + session.get('email') + "/code/Mining")
            if os.path.exists("./static/user/" + session.get('email') + "/code/Mining/User_cluster.py"):
                print('user labels')
                cluster_result['labels'] = get_usermethod_labels()
        else:
            cluster_result = getattr(ClusterWay(), cluster_way['Cluster method'])(cluster_way)
            clustering = cluster_result['clustering']
        if cluster_result.get('labels') is None:
            initial_labels = clustering.labels_
        else:
            initial_labels = cluster_result.get('labels')
        try:
            score = getattr(EvaluationWay(), evaluation_way)(table_data,
                                                             initial_labels)
        except ValueError as e:
            score = 0
        result.append(str(score))
    result_str = ':'.join(result)
    return result_str

def get_usermethod_labels():
    target_url = os.path.join("./static/user/" + session.get('email') + "/code/Mining")
    if os.path.exists(os.path.join(target_url, 'User_cluster.py')):
        file_object = open(os.path.join(target_url, 'User_cluster.py'))
        try:
            code = file_object.read()
            codeOut = StringIO()
            codeErr = StringIO()
            sys.stdout = codeOut
            sys.stderr = codeErr
            exec(code)
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            s = codeOut.getvalue()
            codeOut.close()
            codeErr.close()
        finally:
            user_labels = labels
            file_object.close()
            return user_labels

@app.route('/cluster/User_cluster', methods=['POST', 'GET'])
def User_cluster():
    # 首先修改当前的工作路径，执行完程序后改回原来的工作路径
    current_path = os.getcwd()
    if session.get('email'):
        target_url = os.path.join("./static/user/" + session.get('email') + "/code/Mining")
        draw_id = str(request.get_json()['draw_id'])
        body = 'page-top' + draw_id
        node_id = ['name' + draw_id, 'cluster' + draw_id, 'data_obj' + draw_id, 'method' + draw_id]
        if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
                table_data, table_features, table_identifiers = read_table_data(
                    "./static/user/" + session.get('email') + "/data/table.csv")
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
        table_da_dic = generate_table_dic_data(table_identifiers, table_data, table_features)
        exist = False
        if os.path.exists(os.path.join(target_url, 'User_cluster.py')):
            exist = True
            file_object = open(os.path.join(target_url, 'User_cluster.py'))
            try:
                code = file_object.read()
                codeOut = StringIO()
                codeErr = StringIO()
                sys.stdout = codeOut
                sys.stderr = codeErr
                exec(code)
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                s = codeOut.getvalue()
                codeOut.close()
                codeErr.close()
            finally:
                print(session.get('embedding_method'))
                pca = getattr(ProjectionWay(), session.get('embedding_method'))(table_data)
                data_pca = pca['data']
                samples, features = data_pca.shape
                data_pca = data_pca.tolist()
                for i in range(samples):
                    data_pca[i].append(labels[i])
                file_object.close()
            os.chdir(current_path)  # 切换回原来的工作路径

            return render_template("tablegoo/cluster.html", data=data_pca, data_obj=table_da_dic,
                                   # final_data_object['data_dictionary'],
                                   method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )
        if os.path.exists(os.path.join(target_url, 'User_cluster.jar')):
            exist = True
            # 用户程序必须打包，名字为user_way，要执行的方法类名必须是user_way,执行的方法名必须是run
            startJVM(getDefaultJVMPath(), "-ea",
                     "-Djava.class.path=%s" % (os.path.join(target_url, 'User_cluster.jar')))
            os.chdir(target_url)  # in the user file folder to run the file
            user_way_class = JClass('exercise.user_way')
            user_way = user_way_class()
            data_pca = user_way.run()
            shutdownJVM()
            os.chdir(current_path)  # 切换回原来的工作路径
            return render_template("tablegoo/cluster.html", data=data_pca, data_obj=table_da_dic,
                                   # final_data_object['data_dictionary'],
                                   method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )
        if os.path.exists(os.path.join(target_url, 'User_cluster.so')):
            exist = True
            os.chdir(target_url)  # in the user file folder to run the file
            if platform.system() == 'Linux':
                user_way = cdll.LoadLibrary(os.path.join(target_url, 'User_cluster.so'))
                data_pca = user_way.run()  # 返回结果
            os.chdir(current_path)  # 切换回原来的工作路径
            return render_template("tablegoo/cluster.html", data=data_pca, data_obj=table_da_dic,
                                   # final_data_object['data_dictionary'],
                                   method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )
        if (exist == False):
            return jsonify({'prompt':'please upload file of your method first!'})
    else:
        return jsonify({'prompt':'please sign in first!'})



@app.route('/save_cluster_file', methods=['POST', 'GET'])
def cluster_code():
    #upload user file.include csv,py,jar,so
    if request.method == 'POST' and session.get('email'):
        f = request.files['file']
        # 1361377791@qq.com
        # basepath = os.path.dirname(__file__)+'/static/user/'+session.get('email')+"/user_code"
        #  文件所要放入的路径

        basepath = os.path.join(os.getcwd(),"static/user/" + session.get('email'))
        # upload_path = os.path.join(basepath, '', secure_filename('User_cluster.zip'))
        if (request.form.get('label') == 'zip'):
            filename = os.path.join(basepath, '/code/Mining/User_cluster.zip')  # 要解压的文件
            filedir = basepath  # 解压后放入的目录
            # 如果他是压缩文件，就对它进行解压，不是的话就不进行操作
            if os.path.exists(filename):
                os.remove(filename)
            f.save(filename)
            fz = zipfile.ZipFile(filename, 'r')
            for file in fz.namelist():
                # print(file)  # 打印zip归档中目录
                fz.extract(file, filedir)
            return 'upload the cluster code file successfully !'
        else:
            if (request.form.get('label') == 'py'):  # python
                user_cluster_url = basepath + '/code/Mining/User_cluster.py'
            if (request.form.get('label') == 'jar'):  # java
                user_cluster_url = basepath + '/code/Mining/User_cluster.jar'
            if (request.form.get('label') == 'so'):  # c/c++
                user_cluster_url = basepath + '/code/Mining/User_cluster.so'
            if (request.form.get('label') == 'csv'):  # csv
                user_cluster_url = basepath + '/data/table.csv'
            if user_cluster_url is not None:
                if os.path.exists(user_cluster_url):
                    os.remove(user_cluster_url)
                f.save(user_cluster_url)
                return 'upload the cluster code file successfully !'
                '''
                cd = pyclamd.ClamdAgnostic()
                is_virus = cd.scan_file(user_cluster_url)
                if is_virus is None:
                    # return redirect(url_for('cluster_code'))
                    return 'upload the cluster code file successfully !'
                else:
                    os.remove(user_cluster_url)
                    return 'virus!!!'
                '''
    else:
        session['last_page'] = '/cluster'
        return jsonify('please sign in first!')


# cluster end-------------------------------------------------
# embedding start---------------------------------------------
@app.route('/embedding')
def projection():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('tablegoo/projection_2.html', user=user1)
    else:
        return render_template('tablegoo/projection_2.html')


@app.route('/projection/projection_way', methods=['POST', 'GET'])
def projection_way():
    if session.get('email'):
        if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
            # run cluster way except user's way
            table_data, table_features, table_identifiers = read_table_data(
                "./static/user/" + session.get('email') + "/data/table.csv")
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    else:
        table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    draw_id = str(request.get_json()['draw_id'])
    projection_method = str(request.get_json()['projection_method'])
    data_params = getattr(ProjectionWay(), projection_method)(table_data)
    projection_data = data_params['data'].tolist()
    print(data_params['params'])
    table_da_dic = generate_table_dic_data(table_identifiers, table_data, table_features)
    return render_template("tablegoo/projection.html", data=projection_data, data_obj=table_da_dic,
                           method=projection_method + draw_id)


@app.route('/mining/embedding', methods=['POST', 'GET'])
def mining_embedding():
    if session.get('email'):
        if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
            # run cluster way except user's way
            table_data, table_features, table_identifiers = read_table_data(
                "./static/user/" + session.get('email') + "/data/table.csv")
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    else:
        table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
    parameters = {}
    parameters['data'] = table_data  # 用户输入的数据csv
    session['embedding_method'] = request.get_json()['embedding_method']
    table_cluster_method = session.get('cluster_method')
    table_embedding_method = session.get('embedding_method')
    table_visualization_method = session.get('visualization_method')
    table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da, table_stt_da, table_clu_emb_da, table_ano_de_da, table_reg_da, table_clusters = generate_table_data(
        table_identifiers, table_features, table_data, table_cluster_method, table_embedding_method, parameters)
    return render_template('tablegoo/tablegoo_homepage.html',
                           features_dictionary=table_fea_fea_dic,
                           no_identifiers_data_list=table_data,
                           no_identifiers_data_list_transform=np.transpose(table_data).tolist(),
                           no_identifiers_data_dictionary=table_fea_da_dic,
                           data_dictionary=table_id_fea_da_dic,
                           mean=table_stt_da['mean'],
                           median=table_stt_da['median'],
                           mode=table_stt_da['mode'],
                           min=table_stt_da['min'],
                           max=table_stt_da['max'],
                           var=table_stt_da['var'],
                           corr=table_stt_da['corr'],
                           features_list=table_features[1:],
                           cluster_embedding_data=table_clu_emb_da,
                           n_clusters=table_clusters,
                           cluster_method=table_cluster_method,
                           embedding_method=table_embedding_method,
                           anomaly_detection_data=table_ano_de_da,
                           regression_data=table_reg_da,
                           visualization_method=table_visualization_method)

@app.route('/User_code', methods=['POST', 'GET'])
def User_code():
    # save user's embedding file
    if request.method == 'POST' and session.get('email'):
        f = request.files['file']
        # basepath = os.path.dirname(__file__) + '/static/user/' + session.get('email') + "/user_code"  # 文件所要放入的路径
        basepath = os.path.join(os.getcwd(),"static/user/" + session.get('email'))

        if (request.form.get('label') == 'zip'):
            filename = os.path.join(basepath, 'code/Mining/User_embedding.zip')  # 要解压的文件
            filedir = basepath  # 解压后放入的目录
            # 如果他是压缩文件，就对它进行解压，不是的话就不进行操作
            if os.path.exists(filename):
                os.remove(filename)
            f.save(filename)
            fz = zipfile.ZipFile(filename, 'r')
            for file in fz.namelist():
                # print(file)  # 打印zip归档中目录
                fz.extract(file, filedir)
        if (request.form.get('label') == 'py'):
            # python
            user_cluster_url = os.path.join(basepath, 'code/Mining/User_embedding.py')
        if (request.form.get('label') == 'jar'):  # java
            user_cluster_url = os.path.join(basepath, 'code/Mining/User_embedding.jar')
        if (request.form.get('label') == 'so'):  # c/c++
            user_cluster_url = os.path.join(basepath, 'code/Mining/User_embedding.so')
        if (request.form.get('label') == 'csv'):  # c/c++
            user_cluster_url = os.path.join(basepath, 'data/table.csv')
        if user_cluster_url is not None:
            if os.path.exists(user_cluster_url):
                os.remove(user_cluster_url)
            f.save(user_cluster_url)
            return 'upload the embedding code file successfully !'
            '''
            cd = pyclamd.ClamdAgnostic()
            is_virus = cd.scan_file(user_cluster_url)
            if is_virus is None:
                # return redirect(url_for('cluster_code'))
                return 'upload the embedding code file successfully !'
            else:
                os.remove(user_cluster_url)
                return 'virus!!!'
                '''
    else:
        session['last_page'] = '/embedding'
        return 'please sign in first!'

@app.route('/projection/User_method', methods=['POST', 'GET'])
def User_method():
    # run user's embedding way
    current_path = os.getcwd()
    if session.get('email'):
        if os.path.exists("./static/user/" + session.get('email') + "/code/Mining/User_embedding.py"):
            target_url = "./static/user/" + session.get('email') + "/code/Mining"
            draw_id = str(request.get_json()['draw_id'])
            if os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
                table_data, table_features, table_identifiers = read_table_data(
                    "./static/user/" + session.get('email') + "/data/table.csv")
            else:
                table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
            table_da_dic = generate_table_dic_data(table_identifiers, table_data, table_features)
            if os.path.exists(os.path.join(target_url, 'User_embedding.py')):
                file_object = open(os.path.join(target_url, 'User_embedding.py'))
                try:
                    code = file_object.read()
                    codeOut = StringIO()
                    codeErr = StringIO()
                    sys.stdout = codeOut
                    sys.stderr = codeErr
                    exec(code)
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                    s = codeOut.getvalue()
                    codeOut.close()
                    codeErr.close()
                finally:
                    file_object.close()
                    # os.remove('User_code.py')
                return render_template("tablegoo/projection.html", data=User_data, data_obj=table_da_dic,
                                       method='User_method' + draw_id)

            if os.path.exists(os.path.join(target_url, 'User_embedding.jar')):
                # 用户程序必须打包，名字为user_way，要执行的方法类名必须是user_way,执行的方法名必须是run
                # os.chdir(target_url)
                startJVM(getDefaultJVMPath(), "-ea",
                         "-Djava.class.path=%s" % (os.path.join(target_url, 'User_embedding.jar')))
                user_way_class = JClass('exercise.user_way')
                user_way = user_way_class()
                User_data_jar = user_way.run()
                shutdownJVM()
                os.chdir(current_path)  # 切换回原来的工作路径
                return render_template("tablegoo/projection.html", data=User_data_jar, data_obj=table_da_dic,
                                       method='User_method' + draw_id)
            if os.path.exists(os.path.join(target_url, 'User_embedding.so')):
                # os.chdir(target_url)
                if platform.system() == 'Linux':
                    user_way = cdll.LoadLibrary(os.path.join(target_url, 'User_embedding.so'))
                    User_data_so = user_way.run()  # 返回结果
                os.chdir(current_path)  # 切换回原来的工作路径
                return render_template("tablegoo/projection.html", data=User_data_so, data_obj=table_da_dic,
                                       method='User_method' + draw_id)
        else:
            return jsonify({'prompt': 'please upload file of your method first!'})
    else:
        return jsonify({'prompt': 'please sign in first!'})

# embedding end---------------------------------------------


# text_OCR--------------------------------------------------

@app.route('/textgoo', methods=['GET', 'POST'])
def textgoo():
    if not session.get('email'):
        user1=None
        path = './examples/text/text_data.csv'
    else:
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if os.path.exists("./static/user/" + email + "/data/text.csv"):
            path = "./static/user/" + email + "/data/text.csv"
        else:
            path = './examples/text/text_data.csv'
    csv_reader = pd.read_csv(path, encoding='gbk')
    csv_reader = np.array(csv_reader).tolist()
    text_no_identifiers_data_dictionary = []
    features_list = ['source', 'target', 'rela']
    for temp_list in csv_reader:
        if not temp_list[0]:
            continue
        list_num = []
        for str in temp_list:
            list_num.append(str)
        my_dic = data_list_to_dictionary(features_list, list_num)
        text_no_identifiers_data_dictionary.append(my_dic)
    return render_template('textgoo/draw_text.html', user=user1, text_data=text_no_identifiers_data_dictionary)


@app.route('/word_cloud_OCR', methods=['GET', 'POST'])
def picture_OCR():
    if session.get('email') and request.method == 'POST':
        type = request.form.get('label')
        if type == 'wav':
            f = request.files['wav']
            base_path = os.path.dirname(
                __file__ + '/static/user/' + session.get('email') + "/img")  # 当前文件所在路径
            upload_path = os.path.join(base_path, '', secure_filename('doc_by_upload.wav'))
            f.save(upload_path)
            result = wav2text.wav2word(upload_path)
            result = json.loads(result)
            if result["err_msg"] != "success.":
                os.remove(upload_path)
                return "err!:" + result["err_msg"]
            else:
                os.remove(upload_path)
                return (" ".join(jieba.cut("".join(result["result"]))))
        if type == 'image':
            f = request.files['image']
            base_path = os.path.dirname(
                __file__)  # os.path.dirname(__file__) + '/static/user/' + session.get('email') + "/img"# 当前文件所在路径
            upload_path = os.path.join(base_path, '', secure_filename('image_by_upload.jpg'))
            f.save(upload_path)
            # 读取刚储存的本地文件
            with open(upload_path, 'rb') as fp:
                image = fp.read()
            # 输入刚读取的本地文件，调用百度文字识别，返回json格式识别结构
            result = client.accurate(image)

            # 将百度返回的分行结果连接成一行
            raw = ""
            for sresult in result["words_result"]:
                raw += sresult["words"]

            # 输入连续的文字，返回分词结果
            x = (" ".join(jieba.cut(raw)))

            # 向浏览器返回分次结果
            os.remove(upload_path)
            return x
        if type == 'docx':
            f = request.files['docx']
            base_path = os.path.dirname(
                __file__)  # os.path.dirname(__file__) + '/static/user/' + session.get('email') + "/img"# 当前文件所在路径
            upload_path = os.path.join(base_path, '', secure_filename('doc_by_upload.docx'))
            f.save(upload_path)
            raw = ""
            document = Document(upload_path)
            for paragraph in document.paragraphs:
                raw += paragraph.text
                # 输入连续的文字，返回分词结果
            x = (" ".join(jieba.cut(raw)))
            # 向浏览器返回分次结果
            os.remove(upload_path)
            return x
        if type == 'text':
            raw = request.form.get('text')
            x = (" ".join(jieba.cut(raw)))
            # 向浏览器返回分次结果
            return x
        else:
            return "we don't support this type of file!"
    else:
        return jsonify(False)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


@app.route('/upload_pic', methods=['POST', 'GET'])
def upload_pic():
    # text=pytesseract.image_to_string(Image.open('show.jpg'),lang='chi_sim') #设置为中文文字的识别
    if session.get('email') and request.method == 'POST':
        f = request.files['uploadImage']
        filename = f.filename
        base_path = "./static/user/" + session.get('email') + "/data"  # 当前文件所在路径
        upload_path = os.path.join(base_path, '', secure_filename(filename))

        if os.path.exists(upload_path):
            os.remove(upload_path)
        f.save(upload_path)  # appends upload.filename automatically

        # 读取刚储存的本地文件
        image = get_file_content(upload_path)

        # 输入刚读取的本地文件，调用百度文字识别，返回json格式识别结构
        result = client.basicAccurate(image)

        # 将百度返回的分行结果连接成一行
        raw = ""
        for sresult in result["words_result"]:
            raw += sresult["words"]

        # 输入连续的文字，返回分词结果
        x = (" ".join(jieba.cut(raw)))

        # 打印分词结果
        print(x)

        # 向浏览器返回分次结果
        return x
    else:
        session['last_page'] = '/textgoo'
        return jsonify(False)


@app.route('/BusRoute/', methods=['POST', 'GET'])
def BusRoute():
	return render_template('geogoo/BusRoute.html')


@app.route('/PM25/', methods=['POST', 'GET'])
def PM25():
	return render_template('geogoo/PM25.html')


# text_OCR--------------------------------------------------

if __name__ == '__main__':
    app.run()
