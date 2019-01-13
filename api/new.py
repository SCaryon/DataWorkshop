from flask import Blueprint, render_template, session,request
from model import user
import os
from table_data_io import read_table_data,generate_table_data
import numpy as np
new = Blueprint('new',__name__,template_folder='../templates_new')

def is_login():
    if session.get('email'):
        email = session.get('email')
        user1 = user.query.filter_by(email=email).first()
        return user1

    return ""

@new.route("/new/")
def home():

    session['cluster_method'] = 'KMeans'
    session['embedding_method'] = 'Principal_Component_Analysis'
    session['visualization_method'] = 'Radviz'
    session['cluster_parameters'] = {}

    return render_template('front.html', user=is_login())


@new.route('/new/logout/')
def logout():
    session.clear()
    return home()

@new.route("/new/login/")
def login():
    return render_template('login.html')

@new.route("/new/signup/")
def signup():
    return render_template('signup.html')

@new.route("/new/term1/")
def term1():
    return render_template('term1.html', user=is_login())

@new.route("/new/term2")
def term2():
    return render_template('term2.html', user=is_login())

@new.route("/new/my/")
def my():
    return render_template('my.html', user=is_login())

@new.route("/new/work/")
def work():
    return render_template('work.html', user=is_login())

@new.route("/new/aboutus/")
def aboutus():
    return render_template('aboutus.html', user=is_login())

@new.route("/new/market/")
def market():
    return render_template('market.html', user=is_login())

@new.route("/new/lab/")
def lab():
    return render_template('lab.html', user=is_login())


# Product
@new.route("/new/product/")
def product():
    return render_template('product.html', user=is_login())

@new.route("/new/product/all")
def product_all():
    return render_template('products/all.html', user=is_login())

@new.route("/new/product/cleangoo")
def product_cleangoo():
    return render_template('products/cleangoo.html', user=is_login())

@new.route("/new/product/multigoo_analysis",methods=['POST', 'GET'])
def product_multigoo_analysis():

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
    return render_template('products/multigoo_analysis.html',
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

@new.route("/new/product/multigoo_visualization",methods=['POST', 'GET'])
def product_multigoo_visualization():

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
    return render_template('products/multigoo_visualization.html',
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

@new.route("/new/product/textgoo")
def product_textgoo():
    return render_template('products/textgoo.html', user=is_login())
# End: Product



@new.route("/new/first")
def world2():
    return "Hello Wo!"



