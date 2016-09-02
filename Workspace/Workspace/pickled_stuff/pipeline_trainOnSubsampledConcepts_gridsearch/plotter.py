from pipeline import *
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
sns.set_style("white")

n_subsamples = 10
phoneme_vectorization = ["binary","embeddings"]
latent_dims = np.array([2,5,10,20,50])
intermediate_dims = np.array([100,200,500])
epsilon_stds = np.array([1,0.1,0.01])

n_ensemble = 2
nb_epoch = 4000

adjusted_rand_scores = np.zeros((2,len(latent_dims),len(intermediate_dims),len(epsilon_stds),n_subsamples,n_ensemble))
adjusted_mutual_info_scores = np.zeros((2,len(latent_dims),len(intermediate_dims),len(epsilon_stds),n_subsamples,n_ensemble))
homogeneity_scores = np.zeros((2,len(latent_dims),len(intermediate_dims),len(epsilon_stds),n_subsamples,n_ensemble))
completeness_scores = np.zeros((2,len(latent_dims),len(intermediate_dims),len(epsilon_stds),n_subsamples,n_ensemble))
v_measure_scores = np.zeros((2,len(latent_dims),len(intermediate_dims),len(epsilon_stds),n_subsamples,n_ensemble))

def plot_phoneme_vectorization(data,y_label):
    x_ticks = phoneme_vectorization
    y = []
    for i,key in enumerate(phoneme_vectorization):
        y.append(data[i,:,:,:].mean())
    y=np.array(y)
    print(y.shape)
    sns.barplot(x=x_ticks,y=y)
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
    plt.xlabel("latent dimension")

def plot_intermediate_dims(data,y_label):
    x_ticks = intermediate_dims
    y = []
    for i,key in enumerate(intermediate_dims):
        y.append(data[:,i,:,:].flatten())
    y=np.array(y)
    print(y.shape)
    plt.boxplot(y.T)
    plt.xticks(range(1,len(x_ticks)+1),x_ticks)
    plt.xlabel("intermediate dimensions")

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

plt.subplot(2,2,1)
plot_phoneme_vectorization(np.random.beta(3,0.4,adjusted_rand_scores.shape), "ars")
plt.subplot(2,2,2)
plot_latent_dims(np.random.beta(3,0.4,adjusted_rand_scores.shape), "ars")
plt.subplot(2,2,3)
plot_intermediate_dims(np.random.beta(3,0.4,adjusted_rand_scores.shape), "ars")
plt.subplot(2,2,4)
plot_epsilon_stds(np.random.beta(3,0.4,adjusted_rand_scores.shape), "ars")
plt.show()
# plot_latent_dims(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
# plot_intermediate_dims(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
# plot_epsilon_stds(np.random.normal(0,1,adjusted_rand_scores.shape), "ars")
