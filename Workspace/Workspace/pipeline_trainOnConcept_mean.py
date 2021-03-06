from pipeline import *

print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList, {1456})

print("VECTORIZE TEST WORDS")
padToMaxLength=15
bpf = BinaryPhonemeFeatures()
X = np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word in words])
print("shape of X:",X.shape)

adjusted_rand_scores_euclidean = []
adjusted_mutual_info_scores_euclidean  =[]
homogeneity_completeness_v_measures_scores_euclidean = []
adjusted_rand_scores_weighted = []
adjusted_mutual_info_scores_weighted  =[]
homogeneity_completeness_v_measures_scores_weighted = []
for n in range(2):
    print(n, "FIT VAE")
    
    batch_size = X.shape[0]
    dim_phoneme_embeddings = 16
    original_dim = dim_phoneme_embeddings * padToMaxLength
    latent_dim = 10
    intermediate_dim = 200
    
    
    epsilon_std = 0.1
    nb_epoch =1000
    
    vae = VAE(latent_dim=latent_dim,
              original_dim=original_dim,
              intermediate_dim=intermediate_dim,
              batch_size=batch_size,
              epsilon_std=epsilon_std)
    
    vae.fit(X,
          nb_epoch=nb_epoch)
    
    
    print("EMBED TEST WORDS")
    embeddings = vae.embed(X)
    
    print("SAMPLING POSTERIOR")
    n_posterior_samples = 4000
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
    
    """
    EUCLIDEAN
    """
    ap_euclidean= AffinityPropagation(damping=damping_factor,
                             #preference=pref
                             affinity="euclidean"
                             )
    y_pred_euclidean = ap_euclidean.fit_predict(embeddings)
    
    """
    WEIGHTED
    """
    ap_weighted= AffinityPropagation(damping=damping_factor,
                             #preference=pref
                             affinity="precomputed"
                             )
    alpha = 1
    dists = np.zeros((len(embeddings),len(embeddings)))
    for u,emb_u in enumerate(embeddings):
        print(u,"/",len(embeddings))
        for v,emb_v in enumerate(embeddings):
            #print(u,"/",len(embeddings)," - ",v,"/",len(embeddings))

            dists[u,v] = -(
                    euclidean(
                            emb_u/(alpha*-np.log(kernel_posterior.pdf(emb_u))),
                             emb_v/(alpha*-np.log(kernel_posterior.pdf(emb_v)))
                              )
                ) 
        #dists = (minmax_scale(dists)-np.max(minmax_scale(dists)))
        #y_pred = ap.fit_predict((minmax_scale(dists)-np.max(minmax_scale(dists))).reshape((len(embeddings),len(embeddings))))
    y_pred_weighted = ap_weighted.fit_predict(dists)

    n_cognate_classes = len(set(cognate_classes))
    n_concepts = len(set(global_ids))
    y_true = cognate_classes
    y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred_euclidean.shape)
    
    adjusted_rand_scores_euclidean.append(metrics.adjusted_rand_score(y_true, y_pred_euclidean))
    adjusted_mutual_info_scores_euclidean.append(metrics.adjusted_mutual_info_score(y_true, y_pred_euclidean))
    homogeneity_completeness_v_measures_scores_euclidean.append(metrics.homogeneity_completeness_v_measure(y_true, y_pred_euclidean))
    
    adjusted_rand_scores_weighted.append(metrics.adjusted_rand_score(y_true, y_pred_weighted))
    adjusted_mutual_info_scores_weighted.append(metrics.adjusted_mutual_info_score(y_true, y_pred_weighted))
    homogeneity_completeness_v_measures_scores_weighted.append(metrics.homogeneity_completeness_v_measure(y_true, y_pred_weighted))
    

print("EUCLIDEAN")
print(np.mean(adjusted_rand_scores_euclidean))
print(np.mean(adjusted_mutual_info_scores_euclidean))
print(np.mean(homogeneity_completeness_v_measures_scores_euclidean,axis=0))

print("WEIGHTED")
print(np.mean(adjusted_rand_scores_weighted))
print(np.mean(adjusted_mutual_info_scores_weighted))
print(np.mean(homogeneity_completeness_v_measures_scores_weighted,axis=0))
  
print("PLOTTING")
import matplotlib.pyplot as plt
import seaborn as sns
from  scipy.stats import multivariate_normal as mvn



#posterior = embeddings
# print("KERNEL DENSITY ESTIMATOR OF POSTERIOR")
# prior_pdf  = lambda x : mvn.pdf(x,np.zeros(latent_dim),np.identity(latent_dim))
# posterior_kernel  = gaussian_kde(posterior.transpose())
# posterior_kernel_pdf = lambda x : posterior_kernel.pdf(x)
# kld = lambda x : (posterior_kernel_pdf(x)*(np.log(prior_pdf(x))+np.log(posterior_kernel_pdf(x))))[0]
# 
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

# print("PLOTTING KDE OF POSTERIOR")
# plt.subplot(1,2,1)
# #plt.imshow(post_prior,alpha=0.1)
# sns.kdeplot(posterior[:,0],posterior[:,1])
# plt.subplot(1,2,2)
# #plt.imshow(post_prior,alpha=0.1)
# sns.kdeplot(posterior[:,0],posterior[:,1])
# 
# 
# sns.set_style("white")
# cmap_y_pred = dict((label,np.random.beta(1,1,3)) for label in y_pred)
# cmap_y_true = dict((label,np.random.beta(1,1,3)) for label in y_true)
# for word,emb,y_p,y_t in zip(words,embeddings,y_pred,y_true):
#     plt.subplot(1,2,1)
#     plt.annotate(word,emb,color=cmap_y_true[y_t])
#     plt.subplot(1,2,2)
#     plt.annotate(word,emb,color=cmap_y_pred[y_p])
# plt.show()
