from pipeline import *
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
sns.set_style("white")

n_subsamples = 10
phoneme_vectorizations = ["dolgo","sca","binary","embeddings"]
latent_dims = np.array([10,20,50])
epsilon_stds = np.array([0.1,0.01,0.001])
n_ensemble = 1
nb_epoch = 2000
intermediate_dim = 1000
import pickle 

adjusted_rand_scores = pickle.load(codecs.open("adjusted_rand_scores_new.pkl","rb"))                        
adjusted_mutual_info_scores = pickle.load(codecs.open("adjusted_mutual_info_scores_new.pkl","rb"))                        
homogeneity_scores = pickle.load(codecs.open("homogeneity_scores_new.pkl","rb"))                        
completeness_scores = pickle.load(codecs.open("completeness_scores_new.pkl","rb"))                        
v_measure_scores = pickle.load(codecs.open("v_measure_scores_new.pkl","rb"))                        

def plot_phoneme_vectorization(data,y_label):
    x_ticks = phoneme_vectorizations
    y = []
    for i,key in enumerate(phoneme_vectorizations):
        y.append(data[i,:,:,:].flatten())
    y=np.array(y)
    print(y.shape)
    plt.boxplot(y.T)
    plt.xticks(range(1,len(x_ticks)+1),x_ticks)
    plt.xlabel("phoneme vectorization")
    
def plot_latent_dims(data,y_label):
    x_ticks = latent_dims
    y = []
    for i,key in enumerate(latent_dims):
        y.append(data[:,i,:,:].flatten())
    y=np.array(y)
    print(y.shape)
    plt.boxplot(y.T)
    plt.xticks(range(1,len(x_ticks)+1),x_ticks)
    plt.xlabel("latent dimensions")

def plot_epsilon_stds(data,y_label):
    x_ticks = epsilon_stds
    y  =[]
    for i,key in enumerate(epsilon_stds):
        y.append(data[:,i,:,:].flatten())
    y=np.array(y)
    print(y.shape)
    plt.boxplot(y.T)
    plt.xticks(range(1,len(x_ticks)+1),x_ticks)
    plt.xlabel(r"$\sigma_{\epsilon}$")

plt.subplot(1,3,1)
plot_phoneme_vectorization(v_measure_scores, "ars")
plt.subplot(1,3,2)
plot_latent_dims(v_measure_scores, "ars")
plt.subplot(1,3,3)
plot_epsilon_stds(v_measure_scores, "ars")
plt.show()
# plot_latent_dims(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
# plot_intermediate_dims(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
# plot_epsilon_stds(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
