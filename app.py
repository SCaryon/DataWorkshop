from datetime import timedelta, datetime
import os,shutil
import smtplib
import csv
# from model import user, db, login, mailconfirm, methoduse
import os, shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import random
import ast
import numpy as np
import pandas as pd
import copy
from flask import Flask, request, json, redirect, render_template, url_for, flash, session, g, jsonify
from statistics import Statistics
from projection import ProjectionWay
from cluster import ClusterWay, EvaluationWay
from anomaly import AnonalyMethod
from regression import fitSLR
import sys
from io import StringIO
from werkzeug.utils import secure_filename
import zipfile

#用于文字识别
from PIL import Image
import pytesseract
#用于文字识别

#用于执行c和java程序
# from jpype import *
from ctypes import *
import platform
#用于执行c和java程序

#用于执行病毒查杀
import pyclamd


app = Flask(__name__)

# app.run('127.0.0.1', debug=True, port=5000, ssl_context=('D:\OpenSSL-Win64\bin\server.crt', 'D:\OpenSSL-Win64\bin\server.key'))
# 用于加密，作为盐混在原始的字符串中，然后用加密算法进行加密
app.config['SECRET_KEY'] = os.urandom(24)
# 设定session的保存时间，当session.permanent=True的时候
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


global final_data_object
final_data_object = {}


def data_list_to_dictionary(list_key, list_value):
    if len(list_key) != len(list_value):
        print("键值对的长度不匹配")
        exit(0)
    dict = {}
    for i in range(len(list_key)):
        dict[list_key[i]] = list_value[i]
    return dict


def create_differ_type_data(fea_list, da_list, type):
    global final_data_object
    identifiers_list = []  # identifiers of samples
    features_list = fea_list  # features of samples
    data_list = []  # data for clean
    no_identifiers_data_list = []  # data for cluster & embedding
    no_identifiers_data_dictionary = []  # dictionary data for visual analysis
    features_dictionary = []  # dictionary features for display
    data_dictionary = []  # dictionary data for display
    temp = copy.deepcopy(da_list)
    data_exception_flag = True
    for temp_list in temp:
        identifiers_list.append(temp_list[0])
        del temp_list[0]
        if type:
            sample_list = []
            for str in temp_list:
                try:
                    t = ast.literal_eval(str)
                except:
                    data_exception_flag = False
                    t = 'no_data'
                finally:
                    sample_list.append(t)
            no_identifiers_data_list.append(sample_list)
        else:
            no_identifiers_data_list.append(temp_list)
    # get data_list
    for temp_list in da_list:
        if type:
            sample_list = []
            for str in temp_list:
                if temp_list.index(str) == 0:
                    sample_list.append(str)
                    continue
                try:
                    t = ast.literal_eval(str)
                except:
                    data_exception_flag = False
                    t = 'no_data'
                finally:
                    sample_list.append(t)
            data_list.append(sample_list)
        else:
            data_list.append(temp_list)
        # get data_dictionary & no_identifiers_data_dictionary
    for i in range(len(temp)):
        l = temp[i]
        list_num = []
        list_num.append(identifiers_list[i])
        for num in l:
            list_num.append(num)
        my_dic = data_list_to_dictionary(features_list, list_num)
        data_dictionary.append(my_dic)
        my_dic = data_list_to_dictionary(features_list[1:], list_num[1:])
        no_identifiers_data_dictionary.append(my_dic)
    # get features_dictionary
    features_dictionary.append(data_list_to_dictionary(features_list, features_list))
    final_data_object['identifiers_list'] = identifiers_list
    final_data_object['features_list'] = features_list
    final_data_object['data_list'] = data_list
    final_data_object['no_identifiers_data_list'] = no_identifiers_data_list
    final_data_object['no_identifiers_data_list_transform'] = np.transpose(no_identifiers_data_list).tolist()
    final_data_object['no_identifiers_data_dictionary'] = no_identifiers_data_dictionary
    final_data_object['features_dictionary'] = features_dictionary
    final_data_object['data_dictionary'] = data_dictionary
    if not data_exception_flag:
        return data_exception_flag

    final_data_object['statistics_data'] = {'mean': [], 'median': [], 'mode': [], 'min': [], 'max': [], 'var': [],
                                            'corr': []}
    stt = Statistics(final_data_object['no_identifiers_data_list'], final_data_object['features_list'][1:])
    final_data_object['statistics_data']['mean'] = stt.mean
    final_data_object['statistics_data']['median'] = stt.median
    final_data_object['statistics_data']['mode'] = stt.mode
    final_data_object['statistics_data']['min'] = stt.min
    final_data_object['statistics_data']['max'] = stt.max
    final_data_object['statistics_data']['var'] = stt.var
    final_data_object['statistics_data']['corr'] = stt.corr

    final_data_object['cluster_method'] = 'KMeans'
    final_data_object['embedding_method'] = 'Principal_Component_Analysis'

    parameters = {}
    parameters['data'] = final_data_object['no_identifiers_data_list']
    result = getattr(ClusterWay(), final_data_object['cluster_method'])(parameters)
    clustering = result['clustering']
    labels = clustering.labels_.tolist()
    final_data_object['n_clusters'] = np.unique(labels).size
    embedding = getattr(ProjectionWay(), final_data_object['embedding_method'])(
        final_data_object['no_identifiers_data_list'])
    samples, features = embedding['data'].shape
    data_embedding = embedding['data'].tolist()
    for i in range(samples):
        lll = labels[i]
        data_embedding[i].append(lll)
    final_data_object['cluster_embedding_data'] = data_embedding

    parameters = {}
    parameters['data'] = final_data_object['no_identifiers_data_list_transform']
    result = getattr(ClusterWay(), final_data_object['cluster_method'])(parameters)
    clustering = result['clustering']
    labels = clustering.labels_.tolist()
    final_data_object['n_clusters'] = np.unique(labels).size
    embedding = getattr(ProjectionWay(), final_data_object['embedding_method'])(
        final_data_object['no_identifiers_data_list_transform'])
    samples, features = embedding['data'].shape
    data_embedding = embedding['data'].tolist()
    final_data_object['regression_data'] = fitSLR(data_embedding)
    for i in range(samples):
        lll = labels[i]
        data_embedding[i].append(lll)
    final_data_object['attributions_analysis_data'] = data_embedding

    final_data_object['anomaly_detection_data'] = AnonalyMethod.clfdetection(final_data_object['cluster_embedding_data'])

    final_data_object['visualization_method'] = 'Radviz'

    return data_exception_flag


@app.route('/')
@app.route('/index')
def index():
    global final_data_object
    # initialization
    final_data_object = {}

    data_list = pd.read_csv('./test.csv', encoding='gbk')
    feature_list = data_list.columns
    feature_list = feature_list.tolist()
    data_list = np.array(data_list).tolist()
    create_differ_type_data(feature_list, data_list, 0)

    if session.get('email'):
        email=session.get('email')
        user1=user.query.filter_by(email=email).first()
        print(user1)
        return render_template('datagoo_homepage.html', user=user1)
    else:
        return render_template('datagoo_homepage.html')


@app.route('/login/', methods=['GET', 'POST'])
def user_login():
    session.clear()
    return render_template('login.html')

@app.route('/master/',methods=['GET','POST'])
def master():
    return render_template('master.html')


# 验证密码
@app.route('/login/pass/', methods=['GET','POST'])
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
    cur_dir = ".\\static\\user"
    if os.path.isdir(cur_dir):
        os.makedirs('.\\static\\user\\' + email)
        cur_dir = cur_dir + "\\" + email
        print(cur_dir, "\\img")
        os.makedirs(cur_dir + "\\img")
        os.makedirs(cur_dir + "\\code")
        os.makedirs(cur_dir + "\\report")
        os.makedirs(cur_dir + "\\olddata")
        cur_dir = cur_dir + "\\code"
        os.makedirs(cur_dir + "\\Clean")
        os.makedirs(cur_dir + "\\Statistic")
        os.makedirs(cur_dir + "\\Mining")
        os.makedirs(cur_dir + "\\Visualiztion")
        srcfile = 'static\\user\\service\\img\\user_img.jpg'
        dstfiel = 'static\\user\\' + email + '\\img\\user_img.jpg'
        mycopyfile(srcfile, dstfiel)
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
            cur_dir = '.\\static\\user\\' + email
            print(cur_dir)
            if os.path.exists(cur_dir):
                return render_template('user/user.html', user=user1)
            else:
                return "Unknown error"

        else:
            return "404 NOT FOUND"
    return render_template('login.html')


ALLOWED_EXTENSIONS = set(['jpg'])


def allowed_file(filename):  # 通过将文件名分段的方式查询文件格式是否在允许上传格式范围之内
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 下一步，需要将用户的头像进行压缩
@app.route('/user/change/', methods=['GET', 'POST'])
def user_change():
    email = request.form.get('email')
    name = request.form.get('username')
    password = request.form.get('password')
    gender = request.form.get('gender')
    signature = request.form.get('signature')
    print("jinlaile ")
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
    if file and allowed_file(file.filename):
        old_file = 'static\\user\\' + session.get('email') + '\\img\\user_img.jpg'
        if os.path.exists(old_file):
            os.remove(old_file)
        file.save(old_file)
        return 'success'
    else:
        return "filename invalid or network error"


@app.route('/admin/')
def admin():
    mananame = request.args.get('manager')
    return render_template('admin/admin.html', manager=mananame)


@app.route('/admin/<id>/')
def admin_id(id):
    id = id.replace('<', '')
    id = id.replace('>', '')
    return render_template('admin/' + id + '.html')


# 地图方法begin
# 进入地图的index界面
@app.route('/geo/index/', methods=['GET', 'POST'])
def geo_index():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('geo_Index.html',user=user1)
    else:
        return render_template('geo_Index.html')


# 行政热力图
@app.route('/geo/admin/', methods=['GET', 'POST'])
def geo_admin():
    global final_data_object
    if 'province' in final_data_object.keys():
        if session.get('email'):
            email = session.get('email')
            user1 = user.query.filter_by(email=email).first()
            if user1 is None:
                return "false"
            return render_template('geo_admin.html', user=user1, attr=final_data_object['attr'])
        else:
            return render_template('geo_admin.html', attr=final_data_object['attr'])
    else:  # 读取默认的数据
        final_data = csv.reader(open('./static/user/service/olddata/dist_code.csv'))
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
        if session.get('email'):
            email = session.get('email')
            user1 = user.query.filter_by(email=email).first()
            if user1 is None:
                return "false"
            return render_template('geo_admin.html', user=user1, attr=final_data_object['attr'])
        else:
            return render_template('geo_admin.html', attr=final_data_object['attr'])


# 读取用户上传的行政区数据
@app.route('/geo/admin/upload/', methods=['GET', 'POST'])
def geo_admin_upload():
    global final_data_object
    if request.method == 'POST':
        json_data = request.form.get('json_data')
        temp = json.loads(json_data)
        final_data = temp
        province = []
        for i in range(1, len(final_data)):
            province.append(final_data[i][0])
        for i in final_data:
            del i[0]
        attr = final_data[0]
        del final_data[0]
        final_data_object = {}
        final_data_object['province'] = province
        final_data_object['data'] = final_data
        final_data_object['attr'] = attr
        print("province:", province, ",\nattr:", attr, ",\ndata", final_data)
        return "true"
    else:
        return "false"


#海量点分布
@app.route('/geo/points/', methods=['GET', 'POST'])
def geo_points():
    global final_data_object
    if 'points' in final_data_object.keys():
        if session.get('email'):
            email = session.get('email')
            user1 = user.query.filter_by(email=email).first()
            if user1 is None:
                return "false"
            return render_template('geo_points.html', user=user1)
        else:
            return render_template('geo_points.html')
    else:  # 读取默认的数据
        final_data = csv.reader(open('./static/user/service/olddata/geo_points.csv'))
        point=[]
        for i in final_data:
            dic=dict(zip(['longitude','latitude','value','name'],i))
            point.append(dic)
        final_data_object = {}
        final_data_object['points']=point
        if session.get('email'):
            email = session.get('email')
            user1 = user.query.filter_by(email=email).first()
            if user1 is None:
                return "false"
            return render_template('geo_points.html', user=user1)
        else:
            return render_template('geo_points.html')


#读取用户上传的点数据
@app.route('/geo/points/upload/',methods=['GET','POST'])
def geo_points_upload():
    global final_data_object
    if request.method == 'POST':
        json_data = request.form.get('json_data')
        temp = json.loads(json_data)
        final_data = temp
        point=[]
        for i in final_data:
            dic=dict(zip(['longitude','latitude','value','name'],i))
            point.append(dic)
        final_data_object={}
        final_data_object['points']=point
        return 'true'
    else:
        return 'false'


# 向前端传递后台的地理信息数据
@app.route('/geo/get/', methods=['GET', 'POST'])
def geo_get():
    return jsonify(final_data_object)




@app.route('/geo/line/', methods=['GET', 'POST'])
def geo_line():
    return "true"


# 地图方法end


@app.route('/text_upload', methods=['GET', 'POST'])
def text_upload():
    global final_data_object
    clean_flag = False
    if request.method == 'POST':
        # initialization
        try:
            final_data_object = {}
            # get json data
            json_data = request.form.get('json_data')
            temp = json.loads(json_data)
            del temp[0]
            del temp[-1]
            text_no_identifiers_data_dictionary = []
            features_list = ['source', 'target', 'rela']
            for i in range(len(temp)):
                l = temp[i]
                list_num = []
                for num in l:
                    list_num.append(num)
                my_dic = data_list_to_dictionary(features_list, list_num)
                text_no_identifiers_data_dictionary.append(my_dic)
            final_data_object['text_no_identifiers_data_dictionary'] = text_no_identifiers_data_dictionary
            clean_flag = True
        except:
            clean_flag = False
    clean_flag = jsonify(clean_flag)
    return clean_flag


@app.route('/text_home', methods=['GET', 'POST'])
def text_home():
    return render_template('draw_text.html', text_data=final_data_object['text_no_identifiers_data_dictionary'])


@app.route('/data_workshop', methods=['GET', 'POST'])
def data_workshop():
    global final_data_object
    if request.method == 'POST':
        # initialization
        final_data_object = {}
        # get json data
        json_data = request.form.get('json_data')
        temp = json.loads(json_data)
        # get features_list
        features_list = temp[0]
        del temp[0]
        del temp[-1]
        clean_flag = create_differ_type_data(features_list, temp, 1)
        clean_flag = jsonify(clean_flag)
        return clean_flag
    else:
        return render_template('datagoo_homepage.html')


@app.route('/home')
def home():
    return render_template('tablegoo_homepage.html',
                           features_dictionary=final_data_object['features_dictionary'],
                           no_identifiers_data_list=final_data_object['no_identifiers_data_list'],
                           no_identifiers_data_list_transform=final_data_object[
                               'no_identifiers_data_list_transform'],
                           no_identifiers_data_dictionary=final_data_object['no_identifiers_data_dictionary'],
                           data_dictionary=final_data_object['data_dictionary'],
                           data_list=final_data_object['data_list'],
                           mean=final_data_object['statistics_data']['mean'],
                           median=final_data_object['statistics_data']['median'],
                           mode=final_data_object['statistics_data']['mode'],
                           min=final_data_object['statistics_data']['min'],
                           max=final_data_object['statistics_data']['max'],
                           var=final_data_object['statistics_data']['var'],
                           corr=final_data_object['statistics_data']['corr'],
                           features_list=final_data_object['features_list'][1:],

                           cluster_embedding_data=final_data_object['cluster_embedding_data'],
                           n_clusters=final_data_object['n_clusters'],
                           cluster_method=final_data_object['cluster_method'],
                           embedding_method=final_data_object['embedding_method'],
                           attributions_analysis_data=final_data_object['attributions_analysis_data'],
                           anomaly_detection_data=final_data_object['anomaly_detection_data'],
                           regression_data=final_data_object['regression_data'],
                           visualization_method=final_data_object['visualization_method'])


@app.route('/mining/attribution_analysis', methods=['POST', 'GET'])
def attribution_analysis():
    return render_template('tablegoo_homepage.html')


@app.route('/mining/cluster', methods=['POST', 'GET'])
def mining_cluster():
    global final_data_object
    parameters = {}
    for key in request.get_json():
        if key != 'Cluster method':  # 要保证参数数组里面只有参数，没有方法名
            parameters[key] = request.get_json()[key]
        else:
            final_data_object['cluster_method'] = request.get_json()[key]

    parameters['data'] = final_data_object['no_identifiers_data_list']  # 用户输入的数据csv
    result = getattr(ClusterWay(), final_data_object['cluster_method'])(parameters)
    clustering = result['clustering']
    if result.get('labels') is None:
        initial_labels = clustering.labels_
    else:
        initial_labels = result.get('labels')
    labels = initial_labels.tolist()
    final_data_object['n_clusters'] = np.unique(labels).size

    embedding = getattr(ProjectionWay(), final_data_object['embedding_method'])(final_data_object['no_identifiers_data_list'])
    samples, features = embedding['data'].shape
    data_embedding = embedding['data'].tolist()
    for i in range(samples):
        lll = labels[i]
        data_embedding[i].append(lll)
    final_data_object['cluster_embedding_data'] = data_embedding

    return render_template('tablegoo_homepage.html',
                           features_dictionary=final_data_object['features_dictionary'],
                           no_identifiers_data_list=final_data_object['no_identifiers_data_list'],
                           no_identifiers_data_list_transform=final_data_object[
                               'no_identifiers_data_list_transform'],
                           no_identifiers_data_dictionary=final_data_object['no_identifiers_data_dictionary'],
                           data_dictionary=final_data_object['data_dictionary'],
                           data_list=final_data_object['data_list'],
                           mean=final_data_object['statistics_data']['mean'],
                           median=final_data_object['statistics_data']['median'],
                           mode=final_data_object['statistics_data']['mode'],
                           min=final_data_object['statistics_data']['min'],
                           max=final_data_object['statistics_data']['max'],
                           var=final_data_object['statistics_data']['var'],
                           corr=final_data_object['statistics_data']['corr'],
                           features_list=final_data_object['features_list'][1:],

                           cluster_embedding_data=final_data_object['cluster_embedding_data'],
                           n_clusters=final_data_object['n_clusters'],
                           cluster_method=final_data_object['cluster_method'],
                           embedding_method=final_data_object['embedding_method'],
                           attributions_analysis_data=final_data_object['attributions_analysis_data'],
                           anomaly_detection_data=final_data_object['anomaly_detection_data'],
                           regression_data=final_data_object['regression_data'],
                           visualization_method=final_data_object['visualization_method'])


@app.route('/mining/embedding', methods=['POST', 'GET'])
def mining_embedding():
    global final_data_object
    parameters = {}
    parameters['data'] = final_data_object['no_identifiers_data_list']  # 用户输入的数据csv
    result = getattr(ClusterWay(), final_data_object['cluster_method'])(parameters)
    clustering = result['clustering']
    if result.get('labels') is None:
        initial_labels = clustering.labels_
    else:
        initial_labels = result.get('labels')
    labels = initial_labels.tolist()
    final_data_object['n_clusters'] = np.unique(labels).size

    print("before:",final_data_object['embedding_method'])
    final_data_object['embedding_method']=request.get_json()['embedding_method']
    print('after',final_data_object['embedding_method'])
    embedding = getattr(ProjectionWay(), final_data_object['embedding_method'])(final_data_object['no_identifiers_data_list'])
    samples, features = embedding['data'].shape
    data_embedding = embedding['data'].tolist()
    for i in range(samples):
        lll = labels[i]
        data_embedding[i].append(lll)
    final_data_object['cluster_embedding_data'] = data_embedding

    return render_template('tablegoo_homepage.html',
                           features_dictionary=final_data_object['features_dictionary'],
                           no_identifiers_data_list=final_data_object['no_identifiers_data_list'],
                           no_identifiers_data_list_transform=final_data_object[
                               'no_identifiers_data_list_transform'],
                           no_identifiers_data_dictionary=final_data_object['no_identifiers_data_dictionary'],
                           data_dictionary=final_data_object['data_dictionary'],
                           data_list=final_data_object['data_list'],
                           mean=final_data_object['statistics_data']['mean'],
                           median=final_data_object['statistics_data']['median'],
                           mode=final_data_object['statistics_data']['mode'],
                           min=final_data_object['statistics_data']['min'],
                           max=final_data_object['statistics_data']['max'],
                           var=final_data_object['statistics_data']['var'],
                           corr=final_data_object['statistics_data']['corr'],
                           features_list=final_data_object['features_list'][1:],

                           cluster_embedding_data=final_data_object['cluster_embedding_data'],
                           n_clusters=final_data_object['n_clusters'],
                           cluster_method=final_data_object['cluster_method'],
                           embedding_method=final_data_object['embedding_method'],
                           attributions_analysis_data=final_data_object['attributions_analysis_data'],
                           anomaly_detection_data=final_data_object['anomaly_detection_data'],
                           regression_data=final_data_object['regression_data'],
                           visualization_method=final_data_object['visualization_method'])


@app.route('/mining/anomaly_detection', methods=['POST', 'GET'])
def anomaly_detection():
    return render_template('tablegoo_homepage.html')


@app.route('/mining/classification', methods=['POST', 'GET'])
def classification():
    return render_template('tablegoo_homepage.html')


@app.route('/mining/regression', methods=['POST', 'GET'])
def regression():
    return render_template('tablegoo_homepage.html')


@app.route('/cluster')
def cluster():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('cluster_2.html', user=user1)
    else:
        return render_template('cluster_2.html')


@app.route('/cluster/cluster_way',methods=['POST', 'GET'])
def cluster_way():
    #run cluster way except user's way
    parameters = {}
    draw_id = str(request.get_json()['draw_id'])
    body = 'page-top' + draw_id
    node_id = ['name' + draw_id, 'cluster' + draw_id, 'data_obj' + draw_id, 'method' + draw_id]
    if request.get_json()['exist'] != 'none':
        for key in request.get_json():
            if key!='cluster_method':#要保证参数数组里面只有参数，没有方法名
                parameters[key] = request.get_json()[key]
        # n_clusters = int(request.get_json()['cluster'])
        # use_method = int(request.get_json()['method'])
    parameters['data'] = final_data_object['no_identifiers_data_list']#用户输入的数据csv

    cluster_method=request.get_json()['cluster_method']
    result = getattr(ClusterWay(), cluster_method)(parameters)
    clustering=result['clustering']
    if result.get('labels') is None:
        initial_labels = clustering.labels_
    else:
        initial_labels = result.get('labels')
    labels = initial_labels.tolist()
    clusters = np.unique(labels).size

    pca = getattr(ProjectionWay(), final_data_object['embedding_method'])(final_data_object['no_identifiers_data_list'])
    data_pca = pca['data']
    samples, features = data_pca.shape
    data_pca = data_pca.tolist()
    for i in range(samples):
        lll = labels[i]
        data_pca[i].append(lll)

    this_html=render_template("cluster.html", data=data_pca, data_obj=final_data_object['data_dictionary'], clusters=clusters,
                           method=cluster_method + draw_id, body_id=body, body_draw_id=node_id)
    return this_html


@app.route('/cluster/cluster_way_evaluation', methods=['POST', 'GET'])
def cluster_way_evaluation():  # 需要的参数是各个图所展示出来的聚类方法以及他们对应的参数
    # 返回的结果是聚类方法：聚类的评价值的键值对
    result = []
    evaluation_way = request.get_json()[0]
    result.append(evaluation_way)
    for count in range(len(request.get_json())):
        if count == 0:
            continue
        cluster_way = request.get_json()[count]
        print(cluster_way)
        cluster_way['data'] = final_data_object['no_identifiers_data_list']
        print(cluster_way['Cluster method'])
        cluster_result = {}
        if cluster_way['Cluster method'] == 'User_cluster':
            cluster_result['labels'] = final_data_object['user_labels']
        else:
            cluster_result = getattr(ClusterWay(), cluster_way['Cluster method'])(cluster_way)
            clustering = cluster_result['clustering']
        if cluster_result.get('labels') is None:
            initial_labels = clustering.labels_
        else:
            initial_labels = cluster_result.get('labels')
        try:
            score = getattr(EvaluationWay(), evaluation_way)(final_data_object['no_identifiers_data_list'],
                                                             initial_labels)
        except ValueError as e:
            score = 0
        result.append(str(score))
    result_str = ':'.join(result)
    return result_str


@app.route('/embedding')
def projection():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        if user1 is None:
            return "false"
        return render_template('projection_2.html', user=user1)
    else:
        return render_template('projection_2.html')


@app.route('/projection/projection_way', methods=['POST', 'GET'])
def projection_way():
    draw_id = str(request.get_json()['draw_id'])
    projection_method = str(request.get_json()['projection_method'])
    data_params = getattr(ProjectionWay(), projection_method)(final_data_object['no_identifiers_data_list'])
    projection_data = data_params['data'].tolist()
    print(data_params['params'])
    return render_template("projection.html", data=projection_data, data_obj=final_data_object['data_dictionary'],
                           method=projection_method + draw_id)


@app.route('/User_code', methods=['POST', 'GET'])
def User_code():
    #save user's embedding file
    global upload_path
    if request.method == 'POST':
        f = request.files['file']
        #basepath = os.path.dirname(__file__) + '\\static\\user\\' + session.get('email') + "\\user_code"  # 文件所要放入的路径
        basepath = os.path.join('/home/ubuntu/dagoo', 'static', 'user', '1361377791@qq.com', 'user_code')# upload_path = os.path.join(basepath, '', secure_filename('User_cluster.zip'))
        if (request.form.get('label') == 'zip'):
            filename = os.path.join(basepath,'User_embedding.zip')  # 要解压的文件
            filedir = basepath  # 解压后放入的目录
            # 如果他是压缩文件，就对它进行解压，不是的话就不进行操作
            f.save(basepath + '\\User_embedding.zip')
            fz = zipfile.ZipFile(filename, 'r')
            for file in fz.namelist():
                # print(file)  # 打印zip归档中目录
                fz.extract(file, filedir)
        if (request.form.get('label') == 'py'):
            #python
            user_cluster_url =os.path.join(basepath,'User_embedding.py')
        if (request.form.get('label') == 'jar'):#java
            user_cluster_url = os.path.join(basepath,'User_embedding.jar')
        if (request.form.get('label') == 'so'):#c/c++
            user_cluster_url = os.path.join(basepath,'User_embedding.so')
        if user_cluster_url is not None:
            f.save(user_cluster_url)
            cd = pyclamd.ClamdAgnostic()
            is_virus = cd.scan_file(user_cluster_url)
            if is_virus is None:
                #return redirect(url_for('cluster_code'))
                return 'upload the embedding code file successfully !'
            else:
                os.remove(user_cluster_url)
                return 'virus!!!'


@app.route('/projection/User_method', methods=['POST', 'GET'])
def User_method():
    #run user's embedding way
    current_path = os.getcwd()
    # os.chdir(os.path.dirname(__file__)+'\\static\\user\\'+session.get('email')+"\\user_code")  # 切换成用户代码的路径
    target_url = os.path.join('/home/ubuntu/dagoo', 'static', 'user', '1361377791@qq.com', 'user_code')
    os.chdir(target_url)
    draw_id = str(request.get_json()['draw_id'])
    if os.path.exists(os.path.join(target_url, 'User_embedding.py')):
        file_object = open(os.path.join(target_url,'User_embedding.py'))
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
            #os.remove('User_code.py')
        return render_template("projection.html", data=User_data, data_obj=final_data_object['data_dictionary'],
                               method='User_method' + draw_id)

    if os.path.exists(os.path.join(target_url, 'User_embedding.jar')):
        # 用户程序必须打包，名字为user_way，要执行的方法类名必须是user_way,执行的方法名必须是run
        startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % (os.path.join(target_url, 'User_embedding.jar')))
        user_way_class = JClass('exercise.user_way')
        user_way = user_way_class()
        User_data_jar=user_way.run()
        shutdownJVM()
        os.chdir(current_path)  # 切换回原来的工作路径
        return render_template("projection.html", data=User_data_jar, data_obj=final_data_object['data_dictionary'],
                               method='User_method' + draw_id)
    if os.path.exists(os.path.join(target_url, 'User_embedding.so')):
        if platform.system() == 'Linux':
            user_way = cdll.LoadLibrary(os.path.join(target_url, 'User_embedding.so'))
            User_data_so = user_way.run()#返回结果
        os.chdir(current_path)  # 切换回原来的工作路径
        return render_template("projection.html", data=User_data_so, data_obj=final_data_object['data_dictionary'],
                               method='User_method' + draw_id)


@app.route('/cluster_code', methods=['POST', 'GET'])
def cluster_code():
    if request.method == 'POST':
        f = request.files['file']
        #1361377791@qq.com
        #basepath = os.path.dirname(__file__)+'\\static\\user\\'+session.get('email')+"\\user_code"
        #  文件所要放入的路径
        basepath = os.path.join("/home/ubuntu/dagoo",'static','user','1361377791@qq.com','user_code') #+ '\\static\\user\\1361377791@qq.com\\user_code'  # 文件所要放入的路径

        #upload_path = os.path.join(basepath, '', secure_filename('User_cluster.zip'))
        if(request.form.get('label')=='zip'):
            filename =  os.path.join(basepath,'User_cluster.zip')  # 要解压的文件
            filedir =basepath   # 解压后放入的目录
            #如果他是压缩文件，就对它进行解压，不是的话就不进行操作
            f.save(basepath + '\\User_cluster.zip')
            fz = zipfile.ZipFile(filename, 'r')
            for file in fz.namelist():
                #print(file)  # 打印zip归档中目录
                fz.extract(file, filedir)
            return 'upload the cluster code file successfully !'
        else:
            if (request.form.get('label') == 'py'):  # python
                user_cluster_url = os.path.join(basepath,'User_cluster.py')
            if (request.form.get('label') == 'jar'):  # java
                user_cluster_url = os.path.join(basepath,'User_cluster.jar')
            if (request.form.get('label') == 'so'):  # c/c++
                user_cluster_url = os.path.join(basepath,'User_cluster.so')
            if user_cluster_url is not None:
                f.save(user_cluster_url)
                cd = pyclamd.ClamdAgnostic()
                is_virus = cd.scan_file(user_cluster_url)
                if is_virus is None:
                    # return redirect(url_for('cluster_code'))
                    return 'upload the cluster code file successfully !'
                else:
                    os.remove(user_cluster_url)
                    return 'virus!!!'




@app.route('/cluster/User_cluster', methods=['POST', 'GET'])
def User_cluster():
    # 首先修改当前的工作路径，执行完程序后改回原来的工作路径
    current_path = os.getcwd()
    #os.chdir(os.path.dirname(__file__)+'\\static\\user\\'+session.get('email')+"\\user_code")  # 切换成用户代码的路径
    target_url=os.path.join('/home/ubuntu/dagoo', 'static', 'user', '1361377791@qq.com', 'user_code')
    os.chdir(target_url)
    draw_id = str(request.get_json()['draw_id'])
    body = 'page-top' + draw_id
    node_id = ['name' + draw_id, 'cluster' + draw_id, 'data_obj' + draw_id, 'method' + draw_id]
    print(os.path.exists(os.path.join(target_url,'User_cluster.py')))
    if os.path.exists(os.path.join(target_url,'User_cluster.py')):
        file_object = open(os.path.join(target_url,'User_cluster.py'))
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
            global final_data_object
            pca = getattr(ProjectionWay(), final_data_object['embedding_method'])(
                final_data_object['no_identifiers_data_list'])
            data_pca = pca['data']
            samples, features = data_pca.shape
            data_pca = data_pca.tolist()

            for i in range(samples):
                data_pca[i].append(labels[i])
            final_data_object['user_labels'] = labels
            file_object.close()
        os.chdir(current_path)  # 切换回原来的工作路径
        return render_template("cluster.html", data=data_pca, data_obj=final_data_object['data_dictionary'],
                               method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )
    if os.path.exists(os.path.join(target_url,'User_cluster.jar')):

        # 用户程序必须打包，名字为user_way，要执行的方法类名必须是user_way,执行的方法名必须是run
        startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % (os.path.join(target_url,'User_cluster.jar')))
        user_way_class = JClass('exercise.user_way')
        user_way = user_way_class()
        data_pca=user_way.run()
        shutdownJVM()
        os.chdir(current_path)  # 切换回原来的工作路径
        return render_template("cluster.html", data=data_pca, data_obj=final_data_object['data_dictionary'],
                               method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )
    if os.path.exists(os.path.join(target_url,'User_cluster.so')):
        if platform.system() == 'Linux':
            user_way = cdll.LoadLibrary(os.path.join(target_url,'User_cluster.so'))
            data_pca = user_way.run()#返回结果
        os.chdir(current_path)  # 切换回原来的工作路径
        return render_template("cluster.html", data=data_pca, data_obj=final_data_object['data_dictionary'],
                               method='User_cluster' + draw_id, body_id=body, body_draw_id=node_id, )


@app.route('/clean', methods=['POST', 'GET'])
def clean():
    return render_template("clean.html")


@app.route('/products', methods=['POST', 'GET'])
def products():
    return render_template("products.html")


@app.route('/clean_table', methods=['POST', 'GET'])
def clean_table():
    source_arr = np.mat(final_data_object['data_list'])
    data_transform = source_arr.T
    data_list_transform = data_transform.tolist()
    return render_template("clean_table.html",data=final_data_object['data_list'],frame=final_data_object['features_list'],data_list=data_list_transform)


@app.route('/cluster/save_user_way',methods=['POST','GET'])
def save_user_way():
    if request.method=='POST':
        name = request.form.get('user_cluster_name')
        role=request.form.get('role')
        print(name)
        print(role)
        return 'save your cluster way successfully! '


@app.route('/OCR', methods=['POST', 'GET'])
def OCR():
    # text=pytesseract.image_to_string(Image.open('show.jpg'),lang='chi_sim') #设置为中文文字的识别
    if request.method == 'POST':
        f = request.files['file']
        filename=f.filename
        base_path = os.path.dirname(__file__) + '\\static\\user\\' + session.get('email') + "\\img"# 当前文件所在路径
        upload_path = os.path.join(base_path, '', secure_filename(filename))
        f.save(upload_path)
        #C:\Users\Administrator\DataA\static\user\1361377791@qq.com\img
        text = pytesseract.image_to_string(Image.open(upload_path), lang='eng')  # 设置为英文或阿拉伯字母的识别
        result=text.replace('\n', ' ')
        print(result)
        return 'success!'
    #return render_template("draw_text.html",result=result)
    '''
     if(filename.find('.pdf')):
            from wand.image import Image as wand_Image
            filename=filename.replace('.pdf', '.jpg')
            print(filename)
            image_jpg=wand_Image(filename=upload_path,resolution=300).convert('jpg')
            upload_path = os.path.join(base_path, '', secure_filename(filename))
            print(upload_path)
            image_jpg.save(upload_path)
    '''


@app.route('/word_cloud/OCR', methods=['GET', 'POST'])
def picture_OCR():
    if request.method == 'POST':
        f = request.files['image']
        base_path = os.path.dirname(__file__)#os.path.dirname(__file__) + '\\static\\user\\' + session.get('email') + "\\img"# 当前文件所在路径
        upload_path = os.path.join(base_path, '', secure_filename('temp.jpg'))
        f.save(upload_path)
        #C:\Users\Administrator\DataA\static\user\1361377791@qq.com\img
        text = pytesseract.image_to_string(Image.open(upload_path), lang='eng')  # 设置为英文或阿拉伯字母的识别
        result = text.replace('\n', ' ').replace(',', ' ').replace('.', ' ')
        print(result)
        return result


@app.route('/graphgoo', methods=['POST', 'GET'])
def graphgoo():
    global graph_object
    if request.method == 'POST':
        graph_object = {}
        json_data = request.form.get('json_data')
        temp = json.loads(json_data)
        del temp[0]
        graph_nodes = []
        graph_matrix = []
        for temp_list in temp:
            if not temp_list[0]:
                continue
            graph_nodes.append(temp_list[0])
            del temp_list[0]
            row = []
            for str in temp_list:
                try:
                    t = ast.literal_eval(str)
                except:
                    t = 'o'
                finally:
                    row.append(t)
            graph_matrix.append(row)
        graph_object['nodes'] = graph_nodes
        graph_object['matrix'] = graph_matrix
        return jsonify(True)
    else:
        graph_object = {}
        csv_reader = csv.reader(open('./examples/graph.csv'))
        graph_nodes = []
        graph_matrix = []
        for temp_list in csv_reader:
            if not temp_list[0]:
                continue
            graph_nodes.append(temp_list[0])
            del temp_list[0]
            row = []
            for str in temp_list:
                try:
                    t = ast.literal_eval(str)
                except:
                    t = 'o'
                finally:
                    row.append(t)
            graph_matrix.append(row)
        graph_object['nodes'] = graph_nodes
        graph_object['matrix'] = graph_matrix
        return render_template('graphgoo_homepage.html', nodes=graph_object['nodes'],
                           matrix=graph_object['matrix'])


@app.route('/graphgoo_home')
def graphgoo_home():
    return render_template('graphgoo_homepage.html', nodes=graph_object['nodes'],
                           matrix=graph_object['matrix'])


if __name__ == '__main__':
    app.run(debug=True,
            ssl_context=('certs/server.crt', 'certs/server.key'))

