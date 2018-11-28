import ast
import copy

import csv
import os
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

from model import user, methoduse, login, mailconfirm, db
from flask import Flask, request, json, render_template, session, jsonify, url_for, current_app, g, redirect
from xlrd import open_workbook

app = Flask(__name__)

# app.run('127.0.0.1', debug=True, port=5000, ssl_context=('D:\OpenSSL-Win64\bin\server.crt', 'D:\OpenSSL-Win64\bin\server.key'))
# 用于加密，作为盐混在原始的字符串中，然后用加密算法进行加密
app.config['SECRET_KEY'] = os.urandom(24)
# 设定session的保存时间，当session.permanent=True的时候
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['NODES'] = []
app.config['MATRIX'] = []


@app.route('/')
@app.route('/index')
def index():
    g.count = 0
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        print(user1)
        return render_template('datagoo_homepage.html', user=user1)
    else:
        return render_template('datagoo_homepage.html')


@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    session.clear()
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
        session.clear()
        session['email'] = email
        session['user_id'] = theuser.id
        session.permanent = True
        login1 = login(email=email)
        db.session.add(login1)
        db.session.commit()
        print(theuser)
        return render_template("datagoo_homepage.html", user=theuser)


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
    subject = "激活您的Data Workshop账户"
    from_name = "Data Workshop"
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
    confirm1 = mailconfirm.query.filter_by(email=email, num=verify).first()
    if confirm1 is not None and confirm1.invalid > datetime.now():  # 首先看验证码是否正确
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
        user1.password = password
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
        user1.password = password
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
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] == 'jpg':
        old_file = 'static/user/' + session.get('email') + '/img/user_img.jpg'
        if os.path.exists(old_file):
            os.remove(old_file)
        file.save(old_file)
        return 'success'
    else:
        return "filename invalid or network error"


# 地图方法begin
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



# product master end
@app.route('/geo/globe/', methods=['GET', 'POST'])
def geo_globe():
    if not session.get('email'):
        return render_template("geogoo/geo_globe.html")
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/countries.json") and session.get('dollars'):
            return render_template("geogoo/geo_globe.html", dollars=session.get('dollars'),
                                   data="/static/user/" + email + "/data/countries.json")
        else:
            return render_template("geogoo/geo_globe.html")


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


# 用户上传plane数据
@app.route('/geo/plane/upload/export/', methods=['GET', 'POST'])
def geo_plane_upload_export():
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
                    old_file = path + "countries.xlsx"
                    if os.path.exists(path + filedata.filename):
                        os.remove(path + filedata.filename)
                    if os.path.exists(old_file):
                        os.remove(old_file)
                    try:
                        filedata.save(path + filedata.filename)
                    except IOError:
                        return '上传文件失败'

                    os.rename(path + filedata.filename, old_file)
                    if file2db2json(old_file, path + 'countries.json') == "no such sheet!":
                        return "no such sheet!"
                else:
                    return "filename invalid or network error"
            print("/static/user/" + email + "/data/countries.json")
            return redirect(url_for('geo_globe'))
    else:
        return render_template('user/login.html')


if __name__ == '__main__':
    app.run(processes=10)
