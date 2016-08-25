from pipeline import *

print("LOAD TEST WORDLIST")
pathToAnnotatedWordList = "Data/IELex/output/IELex-2016.tsv.asjp"

languages,words,global_ids,cognate_classes = loadAnnotatedWordList(pathToAnnotatedWordList)

print("VECTORIZE TEST WORDS")
padToMaxLength=15
bpf = BinaryPhonemeFeatures()

X_dict = dict((concept,np.array([bpf.encodeWord(word, padToMaxLength=padToMaxLength).flatten() for word,concept_tmp in zip(words,global_ids) if  concept_tmp == concept]))for concept in global_ids)
concepts2cognate_classes = dict((concept,[cog for i,cog in enumerate(cognate_classes) if global_ids[i] == concept]) for concept in set(sorted(global_ids)))

adjusted_rand_scores = []
adjusted_mutual_info_scores  =[]
homogeneity_completeness_v_measures_scores = []
n_cognate_classes_true_perDataPoint = []
n_cognate_classes_pred_perDataPoint = []
n_concepts = len(X_dict.keys())
for i,item in enumerate(X_dict.items()):
    print(i,"/",n_concepts)
    concept,X  = item
    print("FIT VAE")
    
    batch_size = X.shape[0]
    dim_phoneme_embeddings = 16
    original_dim = dim_phoneme_embeddings * padToMaxLength
    latent_dim = 2
    intermediate_dim = 100
    
    
    epsilon_std = 0.1
    nb_epoch =40000
    
    vae = VAE(latent_dim=latent_dim,
              original_dim=original_dim,
              intermediate_dim=intermediate_dim,
              batch_size=batch_size,
              epsilon_std=epsilon_std)
    
    vae.fit(X,
          nb_epoch=nb_epoch)
    
    
    print("EMBED TEST WORDS")
    embeddings = vae.embed(X)
    
    print("CLUSTER WORDS")
    #for damping_factor in np.arange(0.5,1,0.05):

    damping_factor = 0.5
    ap = AffinityPropagation(damping=damping_factor)
    n_cognate_classes = len(set(cognate_classes))
    n_concepts = len(set(global_ids))
    y_true = concepts2cognate_classes[concept]
    y_pred = ap.fit_predict(embeddings)
    y_random = np.random.randint(0,int(n_cognate_classes/n_concepts),y_pred.shape)
    
    ars = metrics.adjusted_rand_score(y_true, y_pred)
    ami = metrics.adjusted_mutual_info_score(y_true, y_pred)
    hcv = metrics.homogeneity_completeness_v_measure(y_true, y_pred)
    adjusted_rand_scores.append(ars)
    adjusted_mutual_info_scores.append(ami)
    homogeneity_completeness_v_measures_scores.append(hcv)
    
    n_cognate_classes_true_tmp =  len(set(concepts2cognate_classes[concept]))
    n_cognate_classes_pred_tmp =  len(set(y_pred))
    print("estimated number of cognate classes",n_cognate_classes_pred_tmp)
    print("true number of cognate classes",n_cognate_classes_true_tmp)
    n_cognate_classes_true_perDataPoint.append(n_cognate_classes_true_tmp)
    n_cognate_classes_pred_perDataPoint.append(n_cognate_classes_pred_tmp)
    
    print(ars)
    print(ami)
    print(hcv)
    
    print(metrics.adjusted_rand_score(y_true, y_random))
    print(metrics.adjusted_mutual_info_score(y_true, y_random))
    print(metrics.homogeneity_completeness_v_measure(y_true, y_random))

print("adjusted_rand_scores",np.mean(adjusted_rand_scores))
print("adjusted_mutual_info_scores",np.mean(adjusted_mutual_info_scores))
print("homogeneity_completeness_v_measures_scores",np.mean(np.array(homogeneity_completeness_v_measures_scores),axis=0))
import pickle 
import codecs
pickle.dump(adjusted_rand_scores,codecs.open("adjusted_rand_scores.pkl","wb"))
pickle.dump(adjusted_mutual_info_scores,codecs.open("adjusted_mutual_info_scores.pkl","wb"))
pickle.dump(homogeneity_completeness_v_measures_scores,codecs.open("homogeneity_completeness_v_measures_scores.pkl","wb"))
pickle.dump(n_cognate_classes_true_perDataPoint,codecs.open("n_cognate_classes_true_perDataPoint.pkl","wb"))
pickle.dump(n_cognate_classes_pred_perDataPoint,codecs.open("n_cognate_classes_pred_perDataPoint.pkl","wb"))
#   
# print("PLOTTING")
# import matplotlib.pyplot as plt
# import seaborn as sns
# from  scipy.stats import multivariate_normal as mvn
# from scipy.stats import gaussian_kde 
# 
# 
# #prior = np.random.multivariate_normal(np.zeros(2),np.identity(2),(1000,X.shape[1]))
# print("SAMPLING POSTERIOR")
# n_posterior_samples = 1000
# posterior = np.array([vae.sample_z_posterior(X) for i in range(n_posterior_samples)]).reshape(-1,latent_dim)
# #posterior = embeddings
# print("KERNEL DENSITY ESTIMATOR OF POSTERIOR")
# prior_pdf  = lambda x : mvn.pdf(x,np.zeros(latent_dim),np.identity(latent_dim))
# posterior_kernel  = gaussian_kde(posterior.transpose())
# posterior_kernel_pdf = lambda x : posterior_kernel.pdf(x)
# kld = lambda x : (posterior_kernel_pdf(x)*(np.log(prior_pdf(x))+np.log(posterior_kernel_pdf(x))))[0]
# 
# for word,emb in zip(words,embeddings):
#     print(word,kld(emb))
# # words_kld_dict = dict((word,kld(emb)) for word,emb in zip(words,embeddings))
# # kld_words_dict = dict((kld(emb),word) for word,emb in zip(words,embeddings))
# # words_sorted_kld = sorted(words,key=lambda x: words_kld_dict[x])
# # kld_sorted = [words_kld_dict[x] for x in words_sorted_kld]
# # sns.barplot(words,kld_sorted)
# # plt.show()
# 
# # print("CALCULATING LOG(P(Z|X)) - LOG(P(Z))")
# # x_ticks= np.arange(-1,1,0.025)
# # y_ticks= np.arange(-1,1,0.025)
# # shape_grid = (x_ticks.shape[0],y_ticks.shape[0])
# # log_prior = np.array([prior_pdf([x,y]) for x in x_ticks for y in y_ticks]).reshape(shape_grid)
# # log_posterior = np.array([posterior_kernel_pdf([x,y]) for x in x_ticks for y in y_ticks]).reshape(shape_grid)
# # 
# # kld = np.exp(log_posterior)* (log_posterior -log_prior)
# 
# 
# # print("PLOTTING LOG(P(Z|X)) - LOG(P(Z))")
# # #plt.subplot(1,2,1)
# # #plt.imshow(kld,alpha=1,extent=[x_ticks[0],x_ticks[-1],y_ticks[0],y_ticks[-1]])
# # #plt.subplot(1,2,2)
# # #plt.imshow(post_prior,alpha=1,extent=[x_ticks[0],x_ticks[-1],y_ticks[0],y_ticks[-1]])
# # #plt.xticks(x_ticks)
# # #plt.yticks(y_ticks)
# # plt.scatter(embeddings[:,0],embeddings[:,1])
# # plt.show()
# 
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