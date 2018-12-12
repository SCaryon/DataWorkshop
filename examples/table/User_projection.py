from sklearn import random_projection, decomposition, manifold, ensemble, preprocessing, discriminant_analysis
global User_data
#User_data=data%2

min_max_scaler = preprocessing.MinMaxScaler()

if session.get('email') and os.path.exists("./static/user/" + session.get('email') + "/data/table.csv"):
    table_data, table_features, table_identifiers = read_table_data(
        "./static/user/" + session.get('email') + "/data/table.csv")
else:
    table_data, table_features, table_identifiers = read_table_data('./examples/table/car.csv')
data_source = min_max_scaler.fit_transform(table_data)
pca = decomposition.PCA(n_components=2)
a = pca.fit_transform(data_source)
User_data=a.tolist()