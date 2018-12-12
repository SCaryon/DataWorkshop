import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest


class AnonalyMethod:

    def clfdetection(data):
        clf = LocalOutlierFactor(n_neighbors=20)
        clf_pre=clf.fit_predict(data)
        clf_pre = clf_pre.tolist()
        Y = []
        index = []
        for i in range(len(clf_pre)):
            if clf_pre[i] == -1:
                Y.append(data[i])
                index.append(i)
        '''scores_pred = clf.negative_outlier_factor_
        scores_pred = scores_pred.tolist()
        outlierlist=list()
        for a in data[clf_pre==-1]:
            if a in data[scores_pred<-k]:
                outlierlist.append(a)
        outlierarray=np.array(outlierlist)
        return(outlierarray)'''
        return Y, index

    def suppport_vector_machine(data):
        clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
        clf.fit(data)
        outlier_pre=clf.predict(data)
        outlier=data[outlier_pre==-1]
        return(outlier)


    def ElliEnvelope(data):
        clf=EllipticEnvelope(contamination=0.1)
        clf.fit(data)
        outlier_pre=clf.predict(data)
        outlier=data[outlier_pre==-1]
        return(outlier)
