import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.cluster import KMeans
global labels
data = np.array(final_data_object['no_identifiers_data_list'])
data = preprocessing.MinMaxScaler().fit_transform(data)
model = KMeans(n_clusters=6)
clustering = model.fit(data)
labels = clustering.labels_
labels = labels.tolist()