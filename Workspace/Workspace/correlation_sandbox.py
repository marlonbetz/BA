from pipeline import *
import sys
from scipy.stats import spearmanr,pearsonr
from scipy.spatial.distance import cosine


def vectorLinspace(start,stop,num=50):
    assert len(start) == len(stop)
    assert num > 0
    return np.array([np.linspace(start[dim],stop[dim],num) for dim in range(len(start))]).transpose()



cluster1 = vectorLinspace([-1,10],[1,-10], num=50)
print(cluster1)
cluster1 = cluster1 + np.random.normal(0,.1,cluster1.shape)
cluster2 = vectorLinspace([0,0],[4,5], num=50)
cluster2 = cluster1 + np.random.normal(0,.1,cluster2.shape)
# cluster3 = vectorLinspace([4,1],[7,9], num=50)
# cluster3 = cluster1 + np.random.normal(5,.1,cluster3.shape)
# cluster4 = vectorLinspace([-1,4],[-4,2], num=50)
# cluster4 = cluster1 + np.random.normal(-5,.1,cluster4.shape)

X = cluster1#np.append(cluster1,np.append(cluster2,np.append(cluster3,cluster4,axis=0),axis=0),axis=0)
print(X)
print(pearsonr(X[:,0],X[:,1]),spearmanr(X[:,0],X[:,1]))
dists = np.zeros((len(X),len(X)))
for i1,x1 in enumerate(X): 
    print(i1,"/",len(X))
    for i2,x2 in enumerate(X):
#        for i3,x3 in enumerate(X):
#            if i1 != i2 and i2 != i3 and i1 != i3:
#                 tmp = np.append(x1,np.append(x2,x3,axis=0),axis=0).reshape((-1,2))
#                 #print(tmp)
#                 c = spearmanr(tmp[:,0],tmp[:,1])[0]
        dists[i1,i2] = cosine(x1,x2)
print(dists)
from sklearn.cluster import AffinityPropagation
ap = AffinityPropagation(affinity="precomputed")
y_pred = ap.fit_predict(dists)
print(len(set(y_pred)))
cmap = dict((y,np.random.beta(1,1,3)) for y in y_pred)
import matplotlib.pyplot as plt
for x,y in zip(X,y_pred):
    #plt.annotate(y,x,color=cmap[y])
    pass
plt.scatter(X[:,0],X[:,1])
plt.scatter(cluster2[:,0],cluster2[:,1])
plt.show()