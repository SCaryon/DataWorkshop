import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn import metrics
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import Birch
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
from scipy.cluster import hierarchy
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import MeanShift
from sklearn.cluster import SpectralClustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import FeatureAgglomeration
# from hdbscan import HDBSCAN


class ClusterWay:
    def KMeans(self, parameters):
        result={}
        default_cluster = 3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster = int(parameters['cluster'])
        model = KMeans(n_clusters=default_cluster)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result

    def MiniBatchKMeans(self,parameters):# data, n_clusters, batch_size):
        result = {}
        default_cluster=3
        default_batch_size=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster=int(parameters['cluster'])
        if parameters.get('batch_size') is not None:
            default_batch_size=int(parameters['batch_size'])
        model = MiniBatchKMeans(n_clusters=default_cluster, batch_size=default_batch_size)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    def MeanShift(self,parameters):# data, bandwidth):
        result = {}
        default_bandwidth=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('bandwidth') is not None:
            default_bandwidth=int(parameters['bandwidth'])
        model = MeanShift(bandwidth=default_bandwidth, bin_seeding=True)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    def AffinityPropagation(self,parameters):# data, damping, preference):
        result = {}
        default_damping=0.7#0.5----1
        default_preference=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('damping') is not None:
            default_damping=float(parameters['damping'])
        if parameters.get('preference') is not None:
            default_preference=int(parameters['preference'])
        model = AffinityPropagation(damping=default_damping, preference=default_preference)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    def Birch(self, parameters):#data, threshold, branching_factor):
        result={}
        default_threshold=3
        default_branching_factor=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('threshold') is not None:
            default_threshold=int(parameters['threshold'])
        if parameters.get('branching_factor') is not None:
            default_branching_factor=int(parameters['branching_factor'])
        model = Birch(threshold=default_threshold, branching_factor=default_branching_factor)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    def DBSCAN(self, parameters):#data, eps, min_samples):
        result={}
        default_eps=3
        default_min_samples=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('eps') is not None:
            default_eps=float(parameters['eps'])
        if parameters.get('min_samples') is not None:
            default_min_samples=int(parameters['min_samples'])
        model = DBSCAN(eps=default_eps, min_samples=default_min_samples)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    '''def HDBSCAN(self,parameters):# data, min_cluster_size, min_samples, alpha, cluster_selection_method):
        result = {}
        default_min_cluster_size=3
        default_min_samples=3
        default_alpha=0.5#大于1的float
        default_cluster_selection_method="eom"# "eom", "leaf"
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('min_cluster_size') is not None:
            default_min_cluster_size=int(parameters['min_cluster_size'])
        if parameters.get('min_samples') is not None:
            default_min_samples=int(parameters['min_samples'])
        if parameters.get('alpha') is not None:
            default_alpha=float(parameters['alpha'])
        if parameters.get('cluster_selection_method') is not None:
            default_cluster_selection_method=str(parameters['cluster_selection_method'])
        model = HDBSCAN(min_cluster_size=default_min_cluster_size, min_samples=default_min_samples, alpha=default_alpha,
                        cluster_selection_method=default_cluster_selection_method, allow_single_cluster=True)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result'''
    def GaussianMixture(self,parameters):# data, n_clusters, cov_type):
        result = {}
        default_cluster=3
        default_covariance_type='spherical'#['spherical', 'tied', 'diag', 'full']
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster=int(parameters['cluster'])
        if parameters.get('covariance_type') is not None:
            default_covariance_type=str(parameters['covariance_type'])
        model = GaussianMixture(n_components=default_cluster, covariance_type=default_covariance_type)
        clustering = model.fit(data)
        labels = model.predict(data)
        result['clustering'] = clustering
        result['labels']=labels
        return result
    def Hierarchical(self,parameters):# data, method):
        result = {}
        default_method='single'
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        distance = hierarchy.distance.pdist(data, 'euclidean')
        if parameters.get('cluster_method') is not None:
            default_method=str(parameters['cluster_method'])
        linkage = hierarchy.linkage(distance, method=default_method)
        clustering = hierarchy.fcluster(linkage, t=1, criterion='inconsistent')
        labels = pd.Series(clustering)
        result['clustering'] = clustering
        result['labels'] = labels
        return result
    def AgglomerativeClustering(self,parameters):# data, n_clusters):
        result = {}
        default_cluster=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster=int(parameters['cluster'])
        model = AgglomerativeClustering(n_clusters=default_cluster)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result
    def SpectralClustering(self, parameters):#data, n_clusters):
        result = {}
        default_cluster=3
        data = np.array(parameters['data'])
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster=int(parameters['cluster'])
        model = SpectralClustering(n_clusters=default_cluster)
        clustering = model.fit(data)
        #metrics.calinski_harabaz_score(data, clustering.labels_)
        result['clustering'] = clustering
        return result

class EvaluationWay:
    def calinski_harabaz(self,s_data, labels):
        return metrics.calinski_harabaz_score(s_data, labels)
    def silhouette(self,data, labels):
        p_data = np.array(data)
        p_data = preprocessing.MinMaxScaler().fit_transform(p_data)
        return metrics.silhouette_score(p_data, labels)

'''
    def FeatureAgglomeration(self, parameters):#data, n_clusters, method):
        result={}
        default_cluster=10
        default_method='ward'#['ward', 'complete', 'average']
        data = np.array(parameters['data'])
        print(data)
        data = preprocessing.MinMaxScaler().fit_transform(data)
        if parameters.get('cluster') is not None:
            default_cluster=int(parameters['cluster'])
        if parameters.get('cluster_method') is not None:
            default_method=str(parameters['cluster_method'])
        print(default_cluster)
        print(default_method)
        model = FeatureAgglomeration(n_clusters=default_cluster, linkage=default_method)
        clustering = model.fit(data)
        result['clustering'] = clustering
        return result

'''