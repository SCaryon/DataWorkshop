import ast
import copy
import pandas as pd
import numpy as np
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
from anomaly import AnonalyMethod
from cluster import ClusterWay, EvaluationWay
from projection import ProjectionWay
from regression import fitSLR
from statistics import Statistics
from model import user, methoduse, login, mailconfirm, db
from flask import Flask, request, json, render_template, session, jsonify, url_for, current_app, g, redirect
from xlrd import open_workbook

app = Flask(__name__)

# app.run('127.0.0.1', debug=True, port=5000, ssl_context=('D:\OpenSSL-Win64\bin\server.crt', 'D:\OpenSSL-Win64\bin\server.key'))
# 用于加密，作为盐混在原始的字符串中，然后用加密算法进行加密
app.config['SECRET_KEY'] = os.urandom(24)
# 设定session的保存时间，当session.permanent=True的时候
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


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
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1] == 'jpg':
        old_file = 'static/user/' + session.get('email') + '/img/user_img.jpg'
        if os.path.exists(old_file):
            os.remove(old_file)
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


@app.route('/master/', methods=['POST', 'GET'])
def master():
    return render_template('geogoo/master.html')


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


@app.route('/geo/get/points/', methods=['GET','POST'])
def geo_get_points():
    final_data = csv.reader(open('./examples/geo/geo_points.csv'))
    point = []
    for i in final_data:
        dic = dict(zip(['longitude', 'latitude', 'value', 'name'], i))
        point.append(dic)
    final_data_object = {}
    final_data_object['points'] = point
    return jsonify(final_data_object)


@app.route("/graph/<id>")
def graph_id(id):
    id = id.replace('<', '')
    id = id.replace('>', '')
    return render_template('graphgoo/product/%s.html' % id)


def read_graph_data(filename):
    temp_data = pd.read_csv('./examples/graph/graph.csv')
    graph_nodes = temp_data.columns
    graph_nodes = graph_nodes.tolist()
    graph_matrix = np.array(temp_data).tolist()
    del graph_nodes[0]
    if not graph_nodes[-1]:
        del graph_nodes[-1]
    for temp_list in range(len(graph_nodes)):
        del graph_matrix[temp_list][0]
    return graph_nodes, graph_matrix


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
                else:
                    return "filename invalid or network error"
            return redirect(url_for('graphgoo'))
    else:
        session["last_page"] = '/graphgoo'
        return render_template('user/login.html')


def data_list_to_dictionary(list_key, list_value):
    if len(list_key) != len(list_value):
        print("the keys and the values don't match")
        exit(0)
    dict = {}
    for i in range(len(list_key)):
        dict[list_key[i]] = list_value[i]
    return dict


def generate_table_data(table_id, table_fea, table_da, table_cluster_method, table_embedding_method):
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
    table_stt_da = {'mean': [], 'median': [], 'mode': [], 'min': [], 'max': [], 'var': [],
                    'corr': []}
    stt = Statistics(table_da, table_fea[1:])
    table_stt_da['mean'] = stt.mean
    table_stt_da['median'] = stt.median
    table_stt_da['mode'] = stt.mode
    table_stt_da['min'] = stt.min
    table_stt_da['max'] = stt.max
    table_stt_da['var'] = stt.var
    table_stt_da['corr'] = stt.corr
    # table cluster and embedding data
    parameters = {}
    parameters['data'] = table_da
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
    table_ano_de_da = AnonalyMethod.clfdetection(table_clu_emb_da)
    # table regression data
    table_reg_da = fitSLR(data_embedding)
    return (table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da,
            table_stt_da, table_clu_emb_da, table_ano_de_da, table_reg_da, table_clusters)


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


@app.route('/tablegoo', methods=['POST', 'GET'])
def tablegoo():
    if not session.get('email'):
        table_cluster_method = 'KMeans'
        table_embedding_method = 'Principal_Component_Analysis'
        table_visualization_method = 'Radviz'
        table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
        table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da, table_stt_da, table_clu_emb_da, table_ano_de_da, table_reg_da, table_clusters = generate_table_data(
            table_identifiers, table_features, table_data, table_cluster_method, table_embedding_method)
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
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/table.csv"):
            table_data, table_features, table_identifiers = read_table_data(
                "./static/user/" + email + "/data/table.csv")
            table_cluster_method = 'KMeans'
            table_embedding_method = 'Principal_Component_Analysis'
            table_visualization_method = 'Radviz'
            table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da, table_stt_da, table_clu_emb_da, table_ano_de_da, table_reg_da, table_clusters = generate_table_data(
                table_identifiers, table_features, table_data, table_cluster_method, table_embedding_method)
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
        else:
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
            table_cluster_method = 'KMeans'
            table_embedding_method = 'Principal_Component_Analysis'
            table_visualization_method = 'Radviz'
            table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
            table_fea_fea_dic, table_fea_da_dic, table_id_fea_da_dic, table_id_da, table_stt_da, table_clu_emb_da, table_ano_de_da, table_reg_da, table_clusters = generate_table_data(
                table_identifiers, table_features, table_data, table_cluster_method, table_embedding_method)
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
                else:
                    return "filename invalid or network error"
            return redirect(url_for('tablegoo'))
    else:
        session["last_page"] = '/tablegoo'
        return render_template('user/login.html')


@app.route('/textgoo', methods=['GET', 'POST'])
def textgoo():
    if not session.get('email'):
        csv_reader = csv.reader(open('./examples/text/text_data.csv'))
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
        return render_template('textgoo/draw_text.html', text_data=text_no_identifiers_data_dictionary)
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/text.csv"):
            csv_reader = csv.reader(open("./static/user/" + email + "/data/text.csv"))
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
            return render_template('textgoo/draw_text.html', text_data=text_no_identifiers_data_dictionary)
        else:
            csv_reader = csv.reader(open('./examples/text/text_data.csv'))
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
            return render_template('textgoo/draw_text.html', text_data=text_no_identifiers_data_dictionary)


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
        return render_template('user/login.html')


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


@app.route('/streaming_data', methods=['GET', 'POST'])
def streaming_data():
    email = session.get('email')
    user1 = user.query.filter_by(email=email).first()
    if user1 is not None:
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
        for item in range(len(time_data_object['year'])):
            year = time_data_object['year'][item]
            for feature in time_data_object.keys():
                if feature != 'year':
                    feature_data = time_data_object[feature][item]
                    data = [str(int(year)), feature_data, feature]
                    themeriver_data.append(data)
        themeriver = {}
        themeriver['data'] = themeriver_data
        themeriver_features = []
        features = time_data_object.keys()
        for feature in features:
            if feature != 'year':
                themeriver_features.append(feature)
        themeriver['features'] = themeriver_features
        return jsonify(themeriver)
    else:
        print("please sign in first")
        return 'please sign in first'


@app.route('/streaming_data_fourier', methods=['GET', 'POST'])
def streamingdata_fourier():
    if session.get('email') and request.method == 'POST':
        original_data = csv.reader(open("./static/user/" + session.get('email') + "/data/user_data.csv"))
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
    else:
        return 'please sign in first'


@app.route('/time/ex/', methods=['POST', 'GET'])
def Exponential_smoothing():
    # global time_data_object
    if session.get('email') and request.method == 'POST':
        original_data = csv.reader(open("./static/user/" + session.get('email') + "/data/user_data.csv"))
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
        return re_result


@app.route('/time/ar/', methods=['POST', 'GET'])
def Arithmetic_averaging():
    if session.get('email') and request.method == 'POST':
        original_data = csv.reader(open("./static/user/" + session.get('email') + "/data/user_data.csv"))
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
        original_data = csv.reader(open("./static/user/" + session.get('email') + "/data/user_data.csv"))
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


if __name__ == '__main__':
    app.run(processes=10)
