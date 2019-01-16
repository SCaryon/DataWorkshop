from flask import Blueprint, render_template, session,request, json,jsonify
from model import user
import pandas as pd
import os
from table_data_io import read_table_data,generate_table_data,data_list_to_dictionary,check_table_data,generate_table_dic_data
import numpy as np
from graph_data_io import read_graph_data, check_graph_data
import jieba
import wav2text  # wav转text的自定义py文件
from docx import Document
from werkzeug.utils import secure_filename
from aip import AipOcr  # 引入百度api

# 用于执行病毒查杀
import pyclamd
# 连接百度服务器的密钥
APP_ID = '14658891'
API_KEY = 'zWn97gcDqF9MiFIDOeKVWl04'
SECRET_KEY = 'EEGvCjpzTtWRO3GIxqz94NLz99YSBIT9'
# 连接百度服务器
# 输入三个密钥，返回服务器对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
url ='console'

console = Blueprint('console',__name__,template_folder='../templates_new')

def is_login():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        return user1

    return ""


@console.route("/"+url+"/all")
def all():
    return render_template('console/all.html', user=is_login())

# Product - Clean Goo
@console.route("/"+url+"/cleangoo")
def cleangoo():
    return render_template('console/clean/cleangoo.html', user=is_login())


# Product - Multi Goo
@console.route("/"+url+"/multigoo_analysis",methods=['POST', 'GET'])
def multigoo_analysis():

    session['cluster_method'] = 'KMeans'
    session['embedding_method'] = 'Principal_Component_Analysis'
    session['visualization_method'] = 'Radviz'
    session['cluster_parameters'] = {}


    if not session.get('email'):
        path="./examples/table/car.csv"
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
    return render_template('console/multi/multigoo_analysis.html',
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

@console.route("/"+url+"/multigoo_visualization",methods=['POST', 'GET'])
def multigoo_visualization():

    session['cluster_method'] = 'KMeans'
    session['embedding_method'] = 'Principal_Component_Analysis'
    session['visualization_method'] = 'Radviz'
    session['cluster_parameters'] = {}


    if not session.get('email'):
        path="./examples/table/car.csv"
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
    return render_template('console/multi/multigoo_visualization.html',
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

# Product - Text Goo
@console.route("/"+url+"/textgoo_knowledgegraph", methods=['GET', 'POST'])
def textgoo_knowledgegraph():
    if not session.get('email'):
        user1 = None
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
    return render_template('console/text/textgoo_knowledgegraph.html', user=is_login(), text_data=text_no_identifiers_data_dictionary)

@console.route("/"+url+"/textgoo_wordcloud")
def textgoo_wordcloud():
    return render_template('console/text/textgoo_wordcloud.html', user=is_login())

@console.route('/word_cloud_OCR', methods=['GET', 'POST'])
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


@console.route('/upload_pic', methods=['POST', 'GET'])
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



# Product - Geo Goo
@console.route("/"+url+"/geogoo_global")
def geogoo_global():
    return render_template('console/geo/geogoo_global.html', user=is_login())

@console.route("/"+url+"/geogoo_planemap")
def geogoo_planemap():
    return render_template('console/geo/geogoo_planemap.html', user=is_login())

@console.route("/"+url+"/geogoo_tower")
def geogoo_tower():
    return render_template('console/geo/geogoo_tower.html', user=is_login())

@console.route("/"+url+"/geogoo_list")
def geogoo_list():
    return render_template('console/geo/geogoo_list.html', user=is_login())

@console.route("/"+url+"/geogoo_administration")
def geogoo_administration():
    return render_template('console/geo/geogoo_administration.html', user=is_login())

@console.route("/"+url+"/geogoo_points")
def geogoo_points():
    return render_template('console/geo/geogoo_points.html', user=is_login())
@console.route("/"+url+"/geogoo_line")
def geogoo_line():
    return render_template('console/geo/geogoo_line.html', user=is_login())

@console.route("/"+url+"/geogoo_world")
def geogoo_world():
    return render_template('console/geo/geogoo_world.html', user=is_login())

# Product - Graph Goo
@console.route("/"+url+"/graphgoo_circular")
def graphgoo_circular():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_circular.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_chord")
def graphgoo_chord():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_chord.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_tree")
def graphgoo_tree():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_tree.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_pack")
def graphgoo_pack():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_pack.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_grid")
def graphgoo_grid():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_grid.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_hierarchical")
def graphgoo_hierarchical():
    if not session.get('email'):
        path = './examples/graph/graph.csv'
    else:
        email = session.get('email')
        if os.path.exists("./static/user/" + email + "/data/graph.csv"):
            path = "./static/user/" + email + "/data/graph.csv"
        else:
            path = './examples/graph/graph.csv'
    graph_nodes, graph_matrix = read_graph_data(path)
    return render_template('console/graph/graphgoo_hierarchical.html', user=is_login(),
                           nodes=graph_nodes, matrix=graph_matrix)

@console.route("/"+url+"/graphgoo_product3d")
def graphgoo_product3d():
    return render_template('console/graph/graphgoo_product3d.html', user=is_login())

@console.route("/"+url+"/graphgoo_product2d")
def graphgoo_product2d():
    return render_template('console/graph/graphgoo_product2d.html', user=is_login())

@console.route("/"+url+"/graphgoo_tower")
def graphgoo_tower():
    return render_template('console/graph/graphgoo_tower.html', user=is_login())

# Product - Streaming Goo

@console.route("/"+url+"/streaminggoo")
def streaminggoo():
    return render_template('console/streaming/streaminggoo.html', user=is_login())