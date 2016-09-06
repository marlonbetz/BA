from pipeline import *
import sys
from scipy.stats import spearmanr,pearsonr

cluster1 = np.random.normal(0,1,(20,2))
cluster2 = np.random.normal(4,.7,(15,2))
cluster3 = np.random.normal(-3,1.3,(14,2))
cluster4 = np.random.normal(0,3,(20,2))
X = np.append(cluster1,np.append(cluster2,np.append(cluster3,cluster4,axis=0),axis=0),axis=0)
print(pearsonr(X[:,0],X[:,1]),spearmanr(X[:,0],X[:,1]))
dists = np.zeros((len(X),len(X)))
from sklearn.linear_model import LinearRegression
l = LinearRegression()
for i1,x1 in enumerate(X): 
    for i2,x2 in enumerate(X):
        if i1 != i2:
            #print(x1,x2)
            l.fit([x1], [x2])
            #print(l.coef_,l.intercept_)
            dists[i1,i2] = -np.abs(np.sum(l.coef_))
print(dists)
from sklearn.cluster import AffinityPropagation
ap = AffinityPropagation(affinity="precomputed")
y_pred = ap.fit_predict(dists)
print(len(set(y_pred)))
cmap = dict((y,np.random.beta(1,1,3)) for y in y_pred)
import matplotlib.pyplot as plt
for x,y in zip(X,y_pred):
    plt.annotate(y,x,color=cmap[y])
plt.show()