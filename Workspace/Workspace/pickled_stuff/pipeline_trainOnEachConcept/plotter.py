import numpy as np 
import pickle
import codecs

ars = pickle.load(codecs.open("adjusted_rand_scores.pkl","rb"))
ami = pickle.load(codecs.open("adjusted_mutual_info_scores.pkl","rb"))
hvc =  np.array(pickle.load(codecs.open("homogeneity_completeness_v_measures_scores.pkl","rb")))
n_true =pickle.load(codecs.open("n_cognate_classes_true_perDataPoint.pkl","rb"))
import matplotlib.pyplot as plt

n_ars_map = dict(
                (n,[ars_ for i,ars_ in enumerate(ars) if n_true[i] == n])
                 for n in n_true
                  )
n_ami_map = dict(
                (n,[ami_ for i,ami_ in enumerate(ami) if n_true[i] == n])
                 for n in n_true
                  )
import seaborn as sns
sns.barplot(list(n_ami_map.keys()),[np.mean(n_ami_map[key]) for key in n_ami_map])
#sns.barplot(list(set(n_true)),[n_true.count(n) for n in list(set(n_true))])
plt.show()