
from pipeline import *
from models import VAE
print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {1261})


print("VECTORIZE TEST WORDS")
padToMaxLength=15
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])
print("shape of X:",X.shape)

padToMaxLength = 15
batch_size = 1
dim_phoneme_embeddings = 16
original_dim = dim_phoneme_embeddings * padToMaxLength
latent_dim = 2
intermediate_dim = 500
epsilon_std = 0.01
nb_epoch =100

vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim,
          intermediate_dim=intermediate_dim,
          batch_size=batch_size,
          epsilon_std=epsilon_std)

vae.load_weights("/Users/marlon/Documents/BA/Workspace/Workspace/saved_weights/ASJP_2000/pipeline_asjp_2000.h5") 

print("VECTORIZE WORDS")
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])

print("EMBED WORDS")
embeddings = vae.embed(X)

print("CHECK CORRELATION")
from scipy.stats import pearsonr,spearmanr
print("pearson",pearsonr(embeddings[:,0], embeddings[:,1]))
print("spearman",spearmanr(embeddings[:,0], embeddings[:,1]))

print("PCA")
# from sklearn.decomposition import PCA,KernelPCA,SparsePCA,TruncatedSVD
# 
# pca = PCA(latent_dim).fit(embeddings)
# embeddings_pca = pca.transform(embeddings)

from sklearn.preprocessing import minmax_scale
vae_pca = VAE(latent_dim=2,
          original_dim=2,
          intermediate_dim=10,
          batch_size=batch_size,
          epsilon_std=0.001)
#posterior = np.array([vae.sample_z_posterior(X) for n in range(1000)]).reshape((-1,2))
vae_pca.fit(minmax_scale(embeddings), nb_epoch=400)
embeddings_pca = vae_pca.embed(minmax_scale(embeddings))
print("PLOTTING")
cmap_y_true = dict((label,np.random.beta(1,1,3)) for label in cognate_classes)
import matplotlib.pyplot as plt
for word,emb,x,cognate_class in zip(words,embeddings_pca,X,cognate_classes):
    plt.annotate(word,vae_pca.embed(emb.reshape((1,-1)))[0])
    print("SAMPLING POSTERIOR")
    n_posterior_samples = 400
    #posterior = pca.transform(np.array([vae.sample_z_posterior(x.reshape(1,-1)) for i in range(n_posterior_samples)]).reshape(-1,latent_dim))
    #posterior = vae_pca.embed(np.array([vae.sample_z_posterior(x.reshape(1,-1)) for i in range(n_posterior_samples)]).reshape(-1,latent_dim))
    posterior = np.array([vae_pca.sample_z_posterior(emb.reshape((1,-1))) for n in range(n_posterior_samples)]).reshape((-1,2))
    plt.scatter(posterior[:,0],posterior[:,1],alpha=0.1,color = cmap_y_true[cognate_class])
plt.show()

