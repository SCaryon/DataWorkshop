from sklearn import random_projection, decomposition, manifold, ensemble, preprocessing, discriminant_analysis


class ProjectionWay:
    def GaussianRandomProjection(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = random_projection.GaussianRandomProjection(n_components=2)
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = pca.dense_output#-错误
            return result

    def SparseRandomProjection(self, source):
        min_max_scaler = preprocessing.MinMaxScaler()
        data_source = min_max_scaler.fit_transform(source)
        pca = random_projection.SparseRandomProjection(n_components=2)
        result = {}
        result['data'] = pca.fit_transform(data_source)
        result['params'] =pca.density_#错误
        return result

    def Principal_Component_Analysis(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.PCA(n_components=2)
            #print(pca.fit_transform(data_source).explained_variance_ratio_)
            result={}
            result['data']=pca.fit_transform(data_source)
            params = 0.0
            for j in pca.explained_variance_ratio_:
                params = params + j
            result['params'] = params

            return result


    def KernelPCA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.KernelPCA(n_components=2)
            #没找到合适的评价指数
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0
            return result

    def MiniBatchSparsePCA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.MiniBatchSparsePCA(n_components=2)
            #没有相关参数------------------------
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0
            return result

    def IncrementalPCA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.IncrementalPCA(n_components=2)
            result = {}
            result['data'] = pca.fit_transform(data_source)
            params=0.0
            for j in pca.explained_variance_ratio_:
                params=params+j
            result['params'] = params
            return result

    def NMF(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.NMF(n_components=2)
            result={}
            result['data']=pca.fit_transform(data_source)
            result['params']=pca.reconstruction_err_
            return result

    def Linear_discriminant_analysis(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.LatentDirichletAllocation(n_components=2)
            #居然LDA没有？？？
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0;
            return result

    def QDA(self, source):#这个方法居然没在HTML里面？？？？？？？？？？？？？？？？？？？？？？？？？？？？、
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = discriminant_analysis.QuadraticDiscriminantAnalysis(n_components=2)
            print(pca.covariance_)
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0;
            return result

    def FastICA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.FastICA(n_components=2)
            #mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0;
            return result

    def MDS(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            mds = manifold.MDS(n_components=2)
            result = {}
            result['data'] = mds.fit_transform(data_source)
            result['params'] = 0;
            return result

    def ISOMAP(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            isomap = manifold.Isomap(n_components=2, n_neighbors=25)
            result = {}
            result['data'] = isomap.fit_transform(data_source)
            result['params'] = 0;
            return result

    def Local_Linear_Embedding(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            lle = manifold.LocallyLinearEmbedding(n_components=2, n_neighbors=25, method='standard')
            result = {}
            result['data'] = lle.fit_transform(data_source)
            result['params'] = 0;
            return result

    def LTSA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            lle = manifold.LocallyLinearEmbedding(n_components=2, n_neighbors=25, method='ltsa')
            result = {}
            result['data'] = lle.fit_transform(data_source)
            result['params'] = 0;
            return result

    def HLLE(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            lle = manifold.LocallyLinearEmbedding(n_components=2, n_neighbors=25, method='hessian')
            result = {}
            result['data'] = lle.fit_transform(data_source)
            result['params'] = 0;
            return result

    def MLLE(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            lle = manifold.LocallyLinearEmbedding(n_components=2, n_neighbors=25, method='modified')
            result = {}
            result['data'] = lle.fit_transform(data_source)
            result['params'] = 0;
            return result

    def t_distributed_stochastic_neighbor_embedding(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            tsne = manifold.TSNE(n_components=2, init='pca', random_state=0)
            result = {}
            result['data'] = tsne.fit_transform(data_source)
            result['params'] = 0;
            return result

    def SpectralEmbedding(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            se = manifold.SpectralEmbedding(n_components=2, random_state=0, eigen_solver='arpack')
            result = {}
            result['data'] = se.fit_transform(data_source)
            result['params'] = 0;
            return result

    def RandomForestEmbedding(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit(source)
            hasher = ensemble.RandomTreesEmbedding(n_estimators=200, random_state=0, max_depth=None)
            data_transformed = hasher.fit_transform(data_source)
            rfe = decomposition.TruncatedSVD(n_components=2)
            result = {}
            result['data'] = rfe.fit_transform(data_transformed)
            result['params'] = 0;
            return result


'''
    def SparsePCA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.SparsePCA(n_components=2)
            print(pca.error_)           #不一定对的得得得得得
            result = {}
            result['data'] = pca.fit_transform(data_source)
            result['params'] = 0
            return result

    def RandomizedPCA(self, source):
            min_max_scaler = preprocessing.MinMaxScaler()
            data_source = min_max_scaler.fit_transform(source)
            pca = decomposition.RandomizedPCA(n_components=2)
            result = {}
            result['data'] = pca.fit_transform(data_source)
            params=0.0
            for j in pca.explained_variance_ratio_:
                params=params+j
            result['params'] = params
            return result
'''


