import numpy as np
from scipy.stats import gaussian_kde

class ClusterWeighting(object):
    def __init__(self,distr):
        self.distr = distr
        self.kernel = gaussian_kde(distr.T)
        
    
    def getClusterLogLikelihood(self,cluster_members):
        return np.sum(np.array([np.log2(self.kernel.pdf(x)) for x in cluster_members]))
    def getClusterSelfInformation(self,cluster_members):
        return - self.getClusterLogLikelihood(cluster_members)
    def rearrangeLabels(self,X,y_pred,threshold):
        y_pred2members =dict((y,np.array([emb for i,emb in enumerate(X) if y_pred[i] == y])) for y in y_pred)
        
        y_pred2selfInformation = dict((y,self.getClusterSelfInformation(y_pred2members[y])) for y in y_pred2members)
        y_tmp= np.max(list(set(y_pred2members.keys()))) +1
        y_pred_new = []
        i_X_with_changed_y = []
        for i,y in enumerate(y_pred):
            if y_pred2selfInformation[y] >= threshold:
                y_pred_new.append(y)
            else:
                y_pred_new.append(y_tmp)
                i_X_with_changed_y.append(i)
                y_tmp +=1 
        

        #y_pred_new = [x,for x,y_pred in zip(X,y_pred)]
        return np.array(y_pred_new).reshape(-1,1),i_X_with_changed_y
        
# cw = ClusterWeighting(np.random.normal(0,.1,(4000,2)))
# X1 = np.random.normal(0,.1,(4,2))
# X2 = np.random.normal(.5,.1,(4,2))
# print(cw.getClusterSelfInformation(X1))
# for d in X1:
#     print(cw.kernel.pdf(d))
# print(cw.getClusterSelfInformation(X2))
# print(cw.rearrangeLabels(np.append(X1,X2),[0,0,0,0,1,1,1,1],1))