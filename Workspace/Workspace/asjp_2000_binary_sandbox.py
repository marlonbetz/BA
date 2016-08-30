from pipeline import *
from models import VAE
words = ["apa","aba","ata","ada","pa","ba","ta","da","ap","ab","at","ad","naXt"]


padToMaxLength = 15
batch_size = len(words)
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

embeddings = vae.embed(X)

#posterior = np.array([vae.sample_z_posterior(X) for i in range(n_posterior_samples)]).reshape(-1,latent_dim)

print()

print("PLOTTING")
import matplotlib.pyplot as plt
for word,emb,x in zip(words,embeddings,X):
    plt.annotate(word,emb)
    print("SAMPLING POSTERIOR")
    n_posterior_samples = 100
    posterior = np.array([vae.sample_z_posterior(X) for i in range(n_posterior_samples)]).reshape(-1,latent_dim)
    plt.scatter(posterior[:,0],posterior[:,1],alpha=0.1,color = np.random.beta(1,1,3))
plt.show()
