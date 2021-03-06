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
from sklearn.decomposition import PCA,KernelPCA,SparsePCA,TruncatedSVD

pca = PCA(latent_dim).fit(embeddings)

embeddings_pca = pca.transform(embeddings)[:,0].reshape((-1,1))

print("CLUSTER WORDS")
from scipy.spatial.distance import cosine,euclidean
from sklearn.preprocessing import minmax_scale
#for damping_factor in np.arange(0.5,1,0.05):
damping_factor = 0.5

affinity = "euclidean"
ap = AffinityPropagation(damping=damping_factor,
                         #preference=pref
                         affinity=affinity
                         )
y_pred = ap.fit_predict(embeddings_pca)
n_cognate_classes = len(set(cognate_classes))
n_concepts = len(set(global_ids))
y_true = cognate_classes
y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)

print(metrics.adjusted_rand_score(y_true, y_pred))
print(metrics.adjusted_mutual_info_score(y_true, y_pred))
print(metrics.homogeneity_completeness_v_measure(y_true, y_pred))

print(metrics.adjusted_rand_score(y_true, y_random))
print(metrics.adjusted_mutual_info_score(y_true, y_random))
print(metrics.homogeneity_completeness_v_measure(y_true, y_random))
