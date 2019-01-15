from flask import Blueprint, render_template, session,request
from model import user
import pandas as pd
import os
from table_data_io import read_table_data,generate_table_data,data_list_to_dictionary,check_table_data,generate_table_dic_data
import numpy as np

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
@console.route("/"+url+"/textgoo", methods=['GET', 'POST'])
def textgoo():
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
    return render_template('console/text/textgoo.html', user=is_login(), text_data=text_no_identifiers_data_dictionary)


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
    return render_template('console/graph/graphgoo_circular.html', user=is_login())

@console.route("/"+url+"/graphgoo_chord")
def graphgoo_chord():
    return render_template('console/graph/graphgoo_chord.html', user=is_login())

@console.route("/"+url+"/graphgoo_tree")
def graphgoo_tree():
    return render_template('console/graph/graphgoo_tree.html', user=is_login())

@console.route("/"+url+"/graphgoo_pack")
def graphgoo_pack():
    return render_template('console/graph/graphgoo_pack.html', user=is_login())

@console.route("/"+url+"/graphgoo_grid")
def graphgoo_grid():
    return render_template('console/graph/graphgoo_grid.html', user=is_login())

@console.route("/"+url+"/graphgoo_hierarchical")
def graphgoo_hierarchical():
    return render_template('console/graph/graphgoo_hierarchical.html', user=is_login())

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