import numpy as np 
import pickle
import codecs
from pandas import DataFrame
adjusted_rand_scores = pickle.load(codecs.open("adjusted_rand_scores.pkl","rb"))
adjusted_mutual_info_scores = pickle.load(codecs.open("adjusted_mutual_info_scores.pkl","rb"))
homogeneity_scores = pickle.load(codecs.open("homogeneity_scores.pkl","rb"))
completeness_scores = pickle.load(codecs.open("completeness_scores.pkl","rb"))
v_measures_scores = pickle.load(codecs.open("v_measures_scores.pkl","rb"))

adjusted_rand_scores_random = pickle.load(codecs.open("adjusted_rand_scores_random.pkl","rb"))
adjusted_mutual_info_scores_random = pickle.load(codecs.open("adjusted_mutual_info_scores_random.pkl","rb"))
homogeneity_scores_random = pickle.load(codecs.open("homogeneity_scores_random.pkl","rb"))
completeness_scores_random = pickle.load(codecs.open("completeness_scores_random.pkl","rb"))
v_measures_scores_random = pickle.load(codecs.open("v_measures_scores_random.pkl","rb"))

n_cognate_classes_true_perDataPoint = pickle.load(codecs.open("n_cognate_classes_true_perDataPoint.pkl","rb"))
n_cognate_classes_pred_perDataPoint = pickle.load(codecs.open("n_cognate_classes_pred_perDataPoint.pkl","rb"))

adjusted_rand_scores = adjusted_rand_scores[:,:4]
adjusted_mutual_info_scores = adjusted_mutual_info_scores[:,:4]
homogeneity_scores = homogeneity_scores[:,:4]
completeness_scores = completeness_scores[:,:4]
v_measures_scores = v_measures_scores[:,:4]

adjusted_rand_scores_random = adjusted_rand_scores_random[:,:4]
adjusted_mutual_info_scores_random = adjusted_mutual_info_scores_random[:,:4]
homogeneity_scores_random = homogeneity_scores_random[:,:4]
completeness_scores_random = completeness_scores_random[:,:4]
v_measures_scores_random = v_measures_scores_random[:,:4]

n_cognate_classes_true_perDataPoint = n_cognate_classes_true_perDataPoint[:,:4]
n_cognate_classes_pred_perDataPoint = n_cognate_classes_pred_perDataPoint[:,:4]

import matplotlib.pyplot as plt

import seaborn as sns
sns.set_style("white")
def plot(y_label,key):
    x_ticks = ["ARI","AMI","H","C","V"]

    y = []
    if key=="base":
        for i,data in enumerate([adjusted_rand_scores,#adjusted_rand_scores_random,
                                 adjusted_mutual_info_scores,#adjusted_mutual_info_scores_random,
                                 homogeneity_scores,#homogeneity_scores_random,
                                 completeness_scores,#completeness_scores_random,
                                 v_measures_scores#,v_measures_scores_random
                                 ]):
            y.append(data.flatten())
    elif key=="random":
        for i,data in enumerate([adjusted_rand_scores_random,
                                 adjusted_mutual_info_scores_random,
                                 homogeneity_scores_random,
                                 completeness_scores_random,
                                 v_measures_scores_random
                                 ]):
            y.append(data.flatten()) 
    y=np.array(y)
    print(y.shape)
    plt.boxplot(y.T)
    plt.xticks(np.arange(1,len(x_ticks)+1,1),x_ticks)
    plt.xlabel("measures")
    plt.ylabel(y_label)

def toLatexTable():
    return DataFrame(np.array([adjusted_rand_scores.mean(),#adjusted_rand_scores_random.mean(),
                             adjusted_mutual_info_scores.mean(),#adjusted_mutual_info_scores_random.mean(),
                             homogeneity_scores.mean(),#homogeneity_scores_random.mean(),
                             completeness_scores.mean(),#completeness_scores_random.mean(),
                             v_measures_scores.mean(),#v_measures_scores_random.mean()
                             ]),#columns=["ARI","ARI","AMI","AMI","H","H","C","C","V","V"]
                     index = ["ARI","AMI","H","C","V"]
                     ).transpose().to_latex()
    
print(toLatexTable())
plt.subplot(1,2,1)
plot("performance","base")
plt.subplot(1,2,2)
plot("performance","random")
plt.show()

