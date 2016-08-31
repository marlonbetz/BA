from pipeline import *
from cluster_weighting import *
print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {1228})

print("VECTORIZE TEST WORDS")
padToMaxLength=15
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])
print("shape of X:",X.shape)

print("FIT VAE")

batch_size = X.shape[0]
dim_phoneme_embeddings = 16
original_dim = dim_phoneme_embeddings * padToMaxLength
latent_dim = 2
intermediate_dim = 200


epsilon_std = 0.1
nb_epoch =40000

vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim,
          intermediate_dim=intermediate_dim,
          batch_size=batch_size,
          epsilon_std=epsilon_std)

vae.fit(X,
      nb_epoch=nb_epoch)

print("NEW VAE OBJECT FOR SMALLER BATCH SIZE")
vae.save_weights("weights_tmp.h5")
vae = VAE(latent_dim=latent_dim,
          original_dim=original_dim,
          intermediate_dim=intermediate_dim,
          batch_size=1,
          epsilon_std=epsilon_std)
vae.load_weights("weights_tmp.h5")
print("EMBED TEST WORDS")
embeddings = vae.embed(X)

print("SAMPLING POSTERIOR")
n_posterior_samples = 2000
posterior = np.array([vae.sample_z_posterior(X) for i in range(n_posterior_samples)]).reshape(-1,latent_dim)
print("KDE OF POSTERIOR")
from scipy.stats import gaussian_kde 
 
kernel_posterior = gaussian_kde(posterior.T)
#pref = [-1/kernel_posterior.pdf(x) for x in embeddings]

print("CLUSTER WORDS")
from scipy.spatial.distance import cosine,euclidean
from sklearn.preprocessing import minmax_scale
concepts2embeddings = dict((concept,[emb for i,emb in enumerate(embeddings) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))
#for damping_factor in np.arange(0.5,1,0.05):
damping_factor = 0.5

affinity = "euclidean"
ap = AffinityPropagation(damping=damping_factor,
                         #preference=pref
                         affinity=affinity
                         )

if affinity == "precomputed":
    alpha = 1
    dists = np.zeros((len(embeddings),len(embeddings)))
    for u,emb_u in enumerate(embeddings):
        print(u,"/",len(embeddings))
        for v,emb_v in enumerate(embeddings):
            print(u,"/",len(embeddings)," - ",v,"/",len(embeddings))

            dists[u,v] = -(
                    euclidean(
                            emb_u/(alpha*-np.log(kernel_posterior.pdf(emb_u))),
                             emb_v/(alpha*-np.log(kernel_posterior.pdf(emb_v)))
                              )
                ) 
    print("dists\n",dists)
    #dists = (minmax_scale(dists)-np.max(minmax_scale(dists)))
    #y_pred = ap.fit_predict((minmax_scale(dists)-np.max(minmax_scale(dists))).reshape((len(embeddings),len(embeddings))))
    y_pred = ap.fit_predict(dists)
else:
    y_pred = ap.fit_predict(embeddings)
    
n_cognate_classes = len(set(cognate_classes))
n_concepts = len(set(global_ids))
y_true = cognate_classes
y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)

y_pred2members = dict((y,np.array([emb for i,emb in enumerate(embeddings) if y_pred[i] == y])) for y in y_pred)

print("WEIGHT CLUSTERS AND REARRANGE INFERRED LABELS")
cw = ClusterWeighting(posterior)
y_pred2selfInformation = dict((y,cw.getClusterSelfInformation(y_pred2members[y])) for y in y_pred2members)
print(y_pred2selfInformation)
y_pred_weighted,i_X_changed_y = cw.rearrangeLabels(X=embeddings,y_pred=y_pred, threshold=-20)
y_pred_weighted = y_pred_weighted.flatten()
print(i_X_changed_y)

print("SAMPLE POSTERIOR OF UNRESOLVED WORDS")
n_posterior_samples_unresolved = 2000
posterior_unresolved = np.array([vae.sample_z_posterior(X[i_X_changed_y]) for i in range(n_posterior_samples_unresolved)]).reshape(-1,latent_dim)
# print("REPEAT CLUSTERING FOR UNRESOLVED WORDS")
# y_pred_unresolved = ap.fit_predict(embeddings[i_X_changed_y])
# cw_unresolved = ClusterWeighting(posterior_unresolved)
# y_pred_weighted_unresolved,i_X_changed_y_unresolved = cw_unresolved.rearrangeLabels(X=embeddings[i_X_changed_y],y_pred=y_pred_unresolved, threshold=-10)
# print(i_X_changed_y_unresolved)
# y_pred_weighted_unresolved = y_pred_weighted_unresolved.flatten()
# y_pred_weighted[i_X_changed_y] = y_pred_weighted_unresolved
print("SCORES BASE")
print(metrics.adjusted_rand_score(y_true, y_pred))
print(metrics.adjusted_mutual_info_score(y_true, y_pred))
print(metrics.homogeneity_completeness_v_measure(y_true, y_pred))

print("SCORES WEIGHTED")
print(metrics.adjusted_rand_score(y_true, y_pred_weighted))
print(metrics.adjusted_mutual_info_score(y_true, y_pred_weighted))
print(metrics.homogeneity_completeness_v_measure(y_true, y_pred_weighted))

print("SCORES RANDOM")
print(metrics.adjusted_rand_score(y_true, y_random))
print(metrics.adjusted_mutual_info_score(y_true, y_random))
print(metrics.homogeneity_completeness_v_measure(y_true, y_random))


  
print("PLOTTING")
import matplotlib.pyplot as plt
import seaborn as sns
from  scipy.stats import multivariate_normal as mvn



# posterior = embeddings
# print("KERNEL DENSITY ESTIMATOR OF POSTERIOR")
# prior_pdf  = lambda x : mvn.pdf(x,np.zeros(latent_dim),np.identity(latent_dim))
# posterior_kernel  = gaussian_kde(posterior.transpose())
# posterior_kernel_pdf = lambda x : posterior_kernel.pdf(x)
# kld = lambda x : (posterior_kernel_pdf(x)*(np.log(prior_pdf(x))+np.log(posterior_kernel_pdf(x))))[0]

# for word,emb in zip(words,embeddings):
#     print(word,kld(emb))
# words_kld_dict = dict((word,kld(emb)) for word,emb in zip(words,embeddings))
# kld_words_dict = dict((kld(emb),word) for word,emb in zip(words,embeddings))
# words_sorted_kld = sorted(words,key=lambda x: words_kld_dict[x])
# kld_sorted = [words_kld_dict[x] for x in words_sorted_kld]
# sns.barplot(words,kld_sorted)
# plt.show()

# print("CALCULATING LOG(P(Z|X)) - LOG(P(Z))")
# x_ticks= np.arange(-1,1,0.025)
# y_ticks= np.arange(-1,1,0.025)
# shape_grid = (x_ticks.shape[0],y_ticks.shape[0])
# log_prior = np.array([prior_pdf([x,y]) for x in x_ticks for y in y_ticks]).reshape(shape_grid)
# log_posterior = np.array([posterior_kernel_pdf([x,y]) for x in x_ticks for y in y_ticks]).reshape(shape_grid)
# 
# kld = np.exp(log_posterior)* (log_posterior -log_prior)


# print("PLOTTING LOG(P(Z|X)) - LOG(P(Z))")
# #plt.subplot(1,2,1)
# #plt.imshow(kld,alpha=1,extent=[x_ticks[0],x_ticks[-1],y_ticks[0],y_ticks[-1]])
# #plt.subplot(1,2,2)
# #plt.imshow(post_prior,alpha=1,extent=[x_ticks[0],x_ticks[-1],y_ticks[0],y_ticks[-1]])
# #plt.xticks(x_ticks)
# #plt.yticks(y_ticks)
# plt.scatter(embeddings[:,0],embeddings[:,1])
# plt.show()

print("PLOTTING KDE OF POSTERIOR")
plt.subplot(1,3,1)
plt.scatter(posterior[:,0],posterior[:,1],alpha=0.01,color="black")
#plt.imshow(post_prior,alpha=0.1)
#sns.kdeplot(posterior[:,0],posterior[:,1])
plt.subplot(1,3,2)
plt.scatter(posterior[:,0],posterior[:,1],alpha=0.01,color="black")
#plt.imshow(post_prior,alpha=0.1)
#sns.kdeplot(posterior[:,0],posterior[:,1])
plt.subplot(1,3,3)
plt.scatter(posterior[:,0],posterior[:,1],alpha=0.01,color="black")
plt.scatter(posterior_unresolved[:,0],posterior_unresolved[:,1],alpha=0.01,color="red")


# 
# 
sns.set_style("white")
cmap_y_pred = dict((label,np.random.beta(1,1,3)) for label in y_pred)
cmap_y_pred_weighted = dict((label,np.random.beta(1,1,3)) for label in y_pred_weighted)
cmap_y_true = dict((label,np.random.beta(1,1,3)) for label in y_true)
for word,emb,y_p,y_p_w,y_t in zip(words,embeddings,y_pred,y_pred_weighted,y_true):
    plt.subplot(1,3,1)
    plt.annotate(word,emb,color=cmap_y_true[y_t])
    plt.subplot(1,3,2)
    plt.annotate(word+"_"+str(y_p),emb,color=cmap_y_pred[y_p])
    plt.subplot(1,3,3)
    plt.annotate(word+"_"+str(y_p_w),emb,color=cmap_y_pred_weighted[y_p_w])
plt.show()