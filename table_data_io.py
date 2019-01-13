import numpy as np
import pandas as pd
from statistics import Statistics
from cluster import ClusterWay, EvaluationWay
from projection import ProjectionWay
from anomaly import AnonalyMethod
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
    table_stt_da = {'corr': []}
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
